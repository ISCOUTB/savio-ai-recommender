<?php
/**
 * Delete Response - CHASIDE Block
 *
 * @package    block_chaside
 * @copyright  2026 SAVIO - Sistema de Aprendizaje Virtual Interactivo (UTB)
 * @author     SAVIO Development Team
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

require_once('../../config.php');

$id = required_param('id', PARAM_INT); // Response ID.
$courseid = required_param('courseid', PARAM_INT);
$confirm = optional_param('confirm', 0, PARAM_INT);

$course = $DB->get_record('course', array('id' => $courseid), '*', MUST_EXIST);
$context = context_course::instance($course->id);
$adminviewurl = new moodle_url('/blocks/chaside/admin_view.php', array('courseid' => $courseid));

require_login($course, false);
require_capability('block/chaside:deletestudentdata', $context);

$response = $DB->get_record('block_chaside_responses', array('id' => $id), '*', MUST_EXIST);

$PAGE->set_url('/blocks/chaside/delete_response.php', array('id' => $id, 'courseid' => $courseid));
$PAGE->set_title(get_string('confirm_delete', 'block_chaside'));
$PAGE->set_heading($course->fullname);
$PAGE->navbar->add(get_string('pluginname', 'block_chaside'), $adminviewurl);
$PAGE->navbar->add(get_string('admin_dashboard', 'block_chaside'), $adminviewurl);
$PAGE->navbar->add(get_string('confirm_delete', 'block_chaside'));

if ($confirm && confirm_sesskey()) {
    // Confirmed, proceed with deletion.
    $DB->delete_records('block_chaside_responses', array('id' => $id));
    redirect($adminviewurl, get_string('response_deleted_success', 'block_chaside'), 2);
}

// Show confirmation page.
echo $OUTPUT->header();

// We get user data to show who it is
$user = $DB->get_record('user', array('id' => $response->userid), 
    'id, firstname, lastname, firstnamephonetic, lastnamephonetic, middlename, alternatename');

// Fallback if user record is missing
$username = $user ? fullname($user) : get_string('deleteduser', 'block_chaside'); 

$message = get_string('deleteresponseconfirm', 'block_chaside', $username);
$confirmurl = new moodle_url($PAGE->url, array('confirm' => 1));
$cancelurl = $adminviewurl;

echo $OUTPUT->confirm($message, $confirmurl, $cancelurl);

echo $OUTPUT->footer();
