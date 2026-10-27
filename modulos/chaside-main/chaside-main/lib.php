<?php
/**
 * CHASIDE Block Library Functions
 *
 * @package    block_chaside
 * @copyright  2026 SAVIO - Sistema de Aprendizaje Virtual Interactivo (UTB)
 * @author     SAVIO Development Team
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

/**
 * Helper function to get completed responses for a course.
 *
 * @param int $courseid The course ID.
 * @param int $groupid Optional group ID.
 * @return array|false Array containing [$course, $responses] or false if permission denied/error.
 */
function block_chaside_get_completed_responses($courseid, $groupid = 0) {
    global $DB;
    
    $course = $DB->get_record('course', array('id' => $courseid), '*', MUST_EXIST);
    $context = context_course::instance($course->id);
    
    require_login($course, false);
    
    // Check permissions
    if (!has_capability('block/chaside:viewstudentdata', $context)) {
        return false;
    }
    
    $student_ids = block_chaside_get_student_ids($context, $groupid);
    
    $responses = array();
    if (!empty($student_ids)) {
        list($insql, $params) = $DB->get_in_or_equal($student_ids, SQL_PARAMS_NAMED, 'user');
        $params['completed'] = 1;
        
        $responses = $DB->get_records_sql("
            SELECT cr.*, u.firstname, u.lastname, u.email, u.idnumber
            FROM {block_chaside_responses} cr
            JOIN {user} u ON cr.userid = u.id
            WHERE cr.userid $insql AND cr.is_completed = :completed
            ORDER BY cr.timemodified DESC
        ", $params);
    }
    
    return [$course, $responses];
}

/**
 * Helper function to get student IDs for a course context.
 *
 * @param context $context The course context.
 * @param int $groupid Optional group ID.
 * @return array Array of student user IDs.
 */
function block_chaside_get_student_ids($context, $groupid = 0) {
    // Get enrolled students
    $enrolled_users = get_enrolled_users($context, 'block/chaside:take_test', $groupid, 'u.id');
    $enrolled_ids = array_keys($enrolled_users);

    // Defensive: exclude any teacher/manager-type user even if misconfigured.
    $student_ids = array();
    foreach ($enrolled_ids as $candidateid) {
        $candidateid = (int)$candidateid;
        
        if (has_capability('block/chaside:viewstudentdata', $context, $candidateid)) {
            continue;
        }
        $student_ids[] = $candidateid;
    }
    return $student_ids;
}

/**
 * Helper function to get the mapping of area codes to string keys.
 * 
 * @return array Mapping of area code (e.g., 'C') to string key suffix (e.g., 'administrative').
 */
function block_chaside_get_area_keys() {
    return [
        'C' => 'administrative',
        'H' => 'humanities',
        'A' => 'artistic',
        'S' => 'health_sciences',
        'I' => 'technical',
        'D' => 'defense_security',
        'E' => 'experimental_sciences'
    ];
}

/**
 * Helper function to prepare export data for a single response.
 *
 * @param stdClass $response The response object joined with user data.
 * @param \block_chaside\facade $facade The facade instance.
 * @return array The formatted data row for export.
 */
function block_chaside_prepare_export_row($response, $facade) {
    // Convert stdClass to array for the facade
    $response_array = (array) $response;
    
    try {
        $scores = $facade->calculate_scores($response_array);
        $detailed_scores = $facade->calculate_detailed_scores($response_array);
        $top_areas = $facade->get_top_areas_v2($detailed_scores, 3);
    } catch (Exception $e) {
        // If calculation fails, use empty arrays
        $scores = array('C' => '', 'H' => '', 'A' => '', 'S' => '', 'I' => '', 'D' => '', 'E' => '');
        $detailed_scores = array('C' => array('interes_score' => '', 'aptitud_score' => ''), 'H' => array('interes_score' => '', 'aptitud_score' => ''), 'A' => array('interes_score' => '', 'aptitud_score' => ''), 'S' => array('interes_score' => '', 'aptitud_score' => ''), 'I' => array('interes_score' => '', 'aptitud_score' => ''), 'D' => array('interes_score' => '', 'aptitud_score' => ''), 'E' => array('interes_score' => '', 'aptitud_score' => ''));
        $top_areas = array();
    }
    
    // Safely access score keys with fallback
    $get_score = function($key) use ($scores) {
        return isset($scores[$key]) ? $scores[$key] : '';
    };
    
    $get_detailed = function($area, $type) use ($detailed_scores) {
        return isset($detailed_scores[$area][$type]) ? $detailed_scores[$area][$type] : '';
    };
    
    $row = array(
        'student_id' => $response->idnumber,
        'student_name' => $response->firstname . ' ' . $response->lastname,
        'student_email' => $response->email,
        'completion_date' => date('Y-m-d H:i:s', $response->timemodified),
    );

    $areas = block_chaside_get_area_keys();
    foreach ($areas as $code => $key) {
        $row[$key . '_score'] = $get_score($code);
        $row[$key . '_interests'] = $get_detailed($code, 'interes_score');
        $row[$key . '_aptitudes'] = $get_detailed($code, 'aptitud_score');
    }

    $row['top_area_1'] = isset($top_areas[0]) ? $top_areas[0]['area'] : '';
    $row['top_area_2'] = isset($top_areas[1]) ? $top_areas[1]['area'] : '';
    $row['top_area_3'] = isset($top_areas[2]) ? $top_areas[2]['area'] : '';

    return $row;
}

/**
 * Helper function to get CSV headers for export.
 *
 * @return array Array of translated headers.
 */
function block_chaside_get_export_headers() {
    $headers = array(
        get_string('export_student_id', 'block_chaside'),
        get_string('export_student_name', 'block_chaside'),
        get_string('export_student_email', 'block_chaside'),
        get_string('export_completion_date', 'block_chaside'),
    );

    $areas = block_chaside_get_area_keys();
    foreach ($areas as $code => $key) {
        $base_string = get_string('export_' . $key . '_score', 'block_chaside');
        $headers[] = $base_string;
        $headers[] = $base_string . ' - ' . get_string('interests', 'block_chaside');
        $headers[] = $base_string . ' - ' . get_string('aptitudes', 'block_chaside');
    }

    $headers[] = get_string('export_top_area', 'block_chaside') . ' 1';
    $headers[] = get_string('export_top_area', 'block_chaside') . ' 2';
    $headers[] = get_string('export_top_area', 'block_chaside') . ' 3';

    return $headers;
}
