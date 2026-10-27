<?php
/**
 * Export - CHASIDE Block
 *
 * @package    block_chaside
 * @copyright  2026 SAVIO - Sistema de Aprendizaje Virtual Interactivo (UTB)
 * @author     SAVIO Development Team
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

require_once('../../config.php');
require_once(__DIR__ . '/lib.php');

$courseid = required_param('courseid', PARAM_INT);
$format = required_param('format', PARAM_ALPHA);
$currentgroup = optional_param('group', 0, PARAM_INT);

$result = block_chaside_get_completed_responses($courseid, $currentgroup);

if ($result === false) {
    redirect(new moodle_url('/course/view.php', array('id' => $courseid)));
}

list($course, $responses) = $result;
$context = context_course::instance($courseid);

if (empty($responses)) {
    redirect(new moodle_url('/blocks/chaside/admin_view.php', array('courseid' => $courseid)), 
             get_string('no_responses_yet', 'block_chaside'), null, 'error');
}

$facade = new \block_chaside\facade();
$export_data = array();

foreach ($responses as $response) {
    $export_data[] = block_chaside_prepare_export_row($response, $facade);
}

// Generate elegant filename using language string

// Generate elegant filename using language string
$course_name = preg_replace('/[^a-z0-9]/i', '_', strtolower($course->shortname));
$date_str = date('Y-m-d');
$filename = get_string('export_filename', 'block_chaside') . '_' . $course_name . '_' . $date_str;

if ($format == 'csv') {
    header('Content-Type: text/csv; charset=utf-8');
    header('Content-Disposition: attachment; filename="' . $filename . '.csv"');
    
    $fp = fopen('php://output', 'w');
    
    // Add BOM for UTF-8
    fprintf($fp, chr(0xEF).chr(0xBB).chr(0xBF));
    
    // Add translated headers
    $headers = block_chaside_get_export_headers();
    fputcsv($fp, $headers);
    
    // Add data
    foreach ($export_data as $row) {
        fputcsv($fp, $row);
    }
    
    fclose($fp);
    exit;
    
} elseif ($format == 'json') {
    header('Content-Type: application/json; charset=utf-8');
    header('Content-Disposition: attachment; filename="' . $filename . '.json"');
    echo json_encode($export_data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
    exit;
    
} else {
    print_error('invalidformat', 'block_chaside');
}
