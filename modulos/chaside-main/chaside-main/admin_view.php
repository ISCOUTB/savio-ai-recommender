<?php
/**
 * CHASIDE Block Admin View
 *
 * @package    block_chaside
 * @copyright  2026 SAVIO - Sistema de Aprendizaje Virtual Interactivo (UTB)
 * @author     SAVIO Development Team
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

require_once(dirname(dirname(dirname(__FILE__))) . '/config.php');
require_once(__DIR__ . '/lib.php');

$courseid = optional_param('courseid', 0, PARAM_INT);
if (!$courseid) {
    $courseid = required_param('cid', PARAM_INT);
}

if ($courseid == SITEID) {
    redirect($CFG->wwwroot);
}

$course = $DB->get_record('course', array('id' => $courseid), '*', MUST_EXIST);
$PAGE->set_course($course);
$context = context_course::instance($courseid);
$PAGE->set_context($context);

require_login($course, false);

// Check if the block is added to the course
if (!$DB->record_exists('block_instances', array('blockname' => 'chaside', 'parentcontextid' => $context->id))) {
    redirect(new moodle_url('/course/view.php', array('id' => $courseid)));
}

// Silent redirect
if (!has_capability('block/chaside:viewstudentdata', $context)) {
    redirect(new moodle_url('/course/view.php', array('id' => $courseid)));
}

$action = optional_param('action', '', PARAM_ALPHA);
$userid = optional_param('userid', 0, PARAM_INT);
$page = optional_param('page', 0, PARAM_INT); // Paging support
$perpage = optional_param('perpage', 20, PARAM_INT);
$search = optional_param('search', '', PARAM_NOTAGS); // Search term

$admin_url = new moodle_url('/blocks/chaside/admin_view.php', array('courseid' => $courseid));
$PAGE->set_url($admin_url);

// Process actions
if ($action === 'delete' && $userid && !has_capability('block/chaside:deletestudentdata', $context)) {
    redirect($admin_url);
}

if ($action === 'delete' && $userid && confirm_sesskey()) {
    $confirm = optional_param('confirm', 0, PARAM_INT);
    if ($confirm) {
        $targetuser = $DB->get_record('user', array('id' => $userid), '*', MUST_EXIST);
        if (!is_enrolled($context, $targetuser, 'block/chaside:take_test', true)
            || has_capability('block/chaside:viewstudentdata', $context, $userid)) {
            redirect(new moodle_url('/course/view.php', array('id' => $courseid)));
        }
        $DB->delete_records('block_chaside_responses', array('userid' => $userid));
        redirect($admin_url, get_string('response_deleted', 'block_chaside'));
    }
}

$title = get_string('admin_dashboard', 'block_chaside');
$PAGE->set_pagelayout('incourse');
$PAGE->set_title($title . " : " . $course->fullname);
$PAGE->set_heading($title . " : " . $course->fullname);
$PAGE->requires->css(new moodle_url('/blocks/chaside/styles.css'));

echo $OUTPUT->header();

$data = [
    'title' => $title,
    'plugin_icon_url' => $OUTPUT->image_url('icon', 'block_chaside')->out(),
    'description' => get_string('admin_dashboard_description', 'block_chaside'),
    'courseid' => $courseid,
    'admin_url' => $admin_url->out(false),
    'export_url' => (new moodle_url('/blocks/chaside/export.php', ['courseid' => $courseid, 'format' => 'csv']))->out(false),
    'course_url' => (new moodle_url('/course/view.php', ['id' => $courseid]))->out(false),
    'search_term' => $search,
    'can_delete' => has_capability('block/chaside:deletestudentdata', $context),
];

// Handle delete confirmation view
if ($action === 'delete' && $userid && empty($confirm)) {
     $user = $DB->get_record('user', array('id' => $userid), 'firstname, lastname');
     if ($user) {
         $data['delete_confirmation'] = true;
         $data['confirm_message'] = get_string('deleteresponseconfirm', 'block_chaside', fullname($user));
         $data['confirm_url'] = (new moodle_url('/blocks/chaside/admin_view.php', ['courseid' => $courseid, 'action' => 'delete', 'userid' => $userid, 'confirm' => 1, 'sesskey' => sesskey()]))->out(false);
         $data['cancel_url'] = $admin_url->out(false);
         echo $OUTPUT->render_from_template('block_chaside/admin_view', $data);
         echo $OUTPUT->footer();
         die();
     }
}

// 1. Get Enrolled Users Context
// Efficiently get ID of students using get_enrolled_sql
list($esql, $params) = get_enrolled_sql($context, 'block/chaside:take_test', 0, true);

// 2. Statistics (Count only)
$sql_enrolled = "SELECT COUNT(DISTINCT u.id) FROM {user} u JOIN ($esql) je ON je.id = u.id WHERE u.deleted = 0";
$total_enrolled = $DB->count_records_sql($sql_enrolled, $params);

$sql_completed = "SELECT COUNT(r.id) FROM {block_chaside_responses} r 
                  JOIN ($esql) je ON je.id = r.userid 
                  WHERE r.is_completed = 1";
$total_completed = $DB->count_records_sql($sql_completed, $params);

$sql_total_responses = "SELECT COUNT(r.id) FROM {block_chaside_responses} r 
                        JOIN ($esql) je ON je.id = r.userid";
$count_responses = $DB->count_records_sql($sql_total_responses, $params);
$total_in_progress = $count_responses - $total_completed;

$completion_rate = $total_enrolled > 0 ? round(($total_completed / $total_enrolled) * 100, 1) : 0;

$data['total_enrolled'] = $total_enrolled;
$data['total_completed'] = $total_completed;
$data['total_in_progress'] = $total_in_progress;
$data['completion_rate'] = $completion_rate;
$data['has_completed'] = ($total_completed > 0);

// 3. Advanced Statistics (Averages & Top Areas) - Only for completed tests
// NOTE: We still need to load completed response data to calculate averages because scores are JSON/serialized or columns.
// Optimization: Fetch only needed columns.
if ($total_completed > 0) {
    // Only fetch scores and ID for stats
    $sql_responses = "SELECT r.* FROM {block_chaside_responses} r 
                      JOIN ($esql) je ON je.id = r.userid 
                      WHERE r.is_completed = 1";

    // Calculate Averages using SQL is much faster
    $areas = ['c', 'h', 'a', 's', 'i', 'd', 'e'];
    $averages = [];
    foreach ($areas as $area) {
        $col = "score_" . $area;
        $sql_avg = "SELECT AVG($col) FROM {block_chaside_responses} r 
                    JOIN ($esql) je ON je.id = r.userid 
                    WHERE r.is_completed = 1";
        $avg = $DB->get_field_sql($sql_avg, $params);
        $averages[strtoupper($area)] = $avg ? round($avg, 1) : 0;
    }
    
    // Prepare Average Data for View
    $area_averages = [];
    foreach ($averages as $code => $score) {
        $area_averages[] = [
            'code' => $code,
            'name' => get_string('area_' . strtolower($code), 'block_chaside'),
            'avg_score' => $score,
            'progress_width' => ($score / 14) * 100,
            'preference_percentage' => round(($score / 14) * 100, 1)
        ];
    }
    $data['area_averages'] = $area_averages;

    // Calculate Top Areas Distribution
    $responses = $DB->get_records_sql($sql_responses, $params);
    
    $top1_counts = array_fill_keys(['C', 'H', 'A', 'S', 'I', 'D', 'E'], 0);
    $top2_counts = array_fill_keys(['C', 'H', 'A', 'S', 'I', 'D', 'E'], 0);
    
    $facade = new \block_chaside\facade();
    foreach ($responses as $r) {
        $response_array = (array) $r;
        $detailed_scores = $facade->calculate_detailed_scores($response_array);
        $top_areas = $facade->get_top_areas_v2($detailed_scores, 2);
        
        if (isset($top_areas[0])) $top1_counts[$top_areas[0]['area']]++;
        if (isset($top_areas[1])) $top2_counts[$top_areas[1]['area']]++;
    }

    // Helper to format area stats
    $format_area_stats = function($counts) use ($total_completed) {
        arsort($counts);
        $result = [];
        $icons = [
            'C' => 'fa-calculator', 'H' => 'fa-book', 'A' => 'fa-paint-brush',
            'S' => 'fa-user-md', 'I' => 'fa-cogs', 'D' => 'fa-shield', 'E' => 'fa-flask'
        ];
        foreach ($counts as $area => $count) {
            if ($count == 0) continue;
            $result[] = [
                'code' => $area,
                'name' => get_string('area_' . strtolower($area), 'block_chaside'),
                'count' => $count,
                'percentage' => ($total_completed > 0) ? round(($count / $total_completed) * 100, 1) : 0,
                'icon' => $icons[$area] ?? 'fa-star'
            ];
        }
        return $result;
    };

    $data['top1_areas'] = $format_area_stats($top1_counts);
    $data['top2_areas'] = $format_area_stats($top2_counts);
}

// 4. Participants Table with Pagination & Search
$userfields = \core_user\fields::for_name()->with_userpic()->get_sql('u', false, '', '', false)->selects;

$where_search = "";
$search_params = [];
if (!empty($search)) {
    $where_search = " AND (" . $DB->sql_like('u.firstname', ':s1', false) . " OR " . $DB->sql_like('u.lastname', ':s2', false) . " OR " . $DB->sql_like('u.email', ':s3', false) . ")";
    $search_params = ['s1' => "%$search%", 's2' => "%$search%", 's3' => "%$search%"];
}

// Total count for pagination
$sql_count_participants = "SELECT COUNT(r.id) 
                           FROM {block_chaside_responses} r
                           JOIN {user} u ON r.userid = u.id
                           JOIN ($esql) je ON je.id = r.userid
                           WHERE 1=1 $where_search";
$total_participants = $DB->count_records_sql($sql_count_participants, array_merge($params, $search_params));

// Fetch paginated records
$sql = "SELECT r.*, {$userfields}
        FROM {block_chaside_responses} r
        JOIN {user} u ON r.userid = u.id
        JOIN ($esql) je ON je.id = r.userid
        WHERE 1=1 $where_search
        ORDER BY r.timemodified DESC";

$participants = $DB->get_records_sql($sql, array_merge($params, $search_params), $page * $perpage, $perpage);

// LOGIC CHANGE: Show table container if course has any responses (count_responses > 0)
// even if search returns nothing.
$data['show_table'] = ($count_responses > 0);

$list = [];
if ($participants) {
    // $data['participants'] = true; // REMOVED: Managed by show_table now
    $facade = new \block_chaside\facade();

    foreach ($participants as $p) {
        $userpicture = new user_picture($p);
        $userpicture->size = 35;
        
        $row = [
            'userpicture' => $OUTPUT->render($userpicture),
            'fullname' => fullname($p),
            'email' => $p->email,
            'is_completed' => ($p->is_completed == 1),
            'date_completed' => userdate($p->timemodified, get_string('strftimedatetimeshort')),
            'view_url' => (new moodle_url('/blocks/chaside/view_results.php', ['userid' => $p->userid, 'courseid' => $courseid]))->out(false),
            'can_delete' => has_capability('block/chaside:deletestudentdata', $context),
            'delete_url' => (new moodle_url('/blocks/chaside/admin_view.php', ['courseid' => $courseid, 'action' => 'delete', 'userid' => $p->userid, 'sesskey' => sesskey()]))->out(false)
        ];

        if ($p->is_completed != 1) {
            $answered = 0;
            for ($i = 1; $i <= 98; $i++) {
                $field = 'q' . $i;
                if (isset($p->$field) && $p->$field !== null && $p->$field !== '') {
                    $answered++;
                }
            }
            $row['answered'] = $answered;
        } else {
             $response_array = (array) $p;
             $detailed_scores = $facade->calculate_detailed_scores($response_array);
             $top_areas = $facade->get_top_areas_v2($detailed_scores, 1);
             if (isset($top_areas[0])) {
                 $row['top_area'] = [
                     'code' => $top_areas[0]['area'],
                     'name' => get_string('area_' . strtolower($top_areas[0]['area']), 'block_chaside')
                 ];
             }
        }
        $list[] = $row;
    }
}
$data['list'] = $list;

// Output Pagination - Moved outside of 'if ($participants)' so it renders even if empty (e.g. for consistent UI)
$baseurl = new moodle_url('/blocks/chaside/admin_view.php', ['courseid' => $courseid]);
if ($search) {
    $baseurl->param('search', $search);
}
$data['pagination'] = $OUTPUT->render(new paging_bar($total_participants, $page, $perpage, $baseurl, 'page'));

echo $OUTPUT->render_from_template('block_chaside/admin_view', $data);

echo $OUTPUT->footer();
