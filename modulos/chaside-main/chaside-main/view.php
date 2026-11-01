<?php
/**
 * Test View - CHASIDE Block
 *
 * @package    block_chaside
 * @copyright  2026 SAVIO - Sistema de Aprendizaje Virtual Interactivo (UTB)
 * @author     SAVIO Development Team
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

require_once('../../config.php');

define('BLOCK_CHASIDE_QUESTIONS_PER_PAGE', 10);
define('BLOCK_CHASIDE_TOTAL_QUESTIONS', 98);

$courseid = required_param('courseid', PARAM_INT);
$page = optional_param('page', 1, PARAM_INT);
$scroll_to_finish = optional_param('scroll_to_finish', 0, PARAM_INT);

$course = $DB->get_record('course', array('id' => $courseid), '*', MUST_EXIST);
$context = context_course::instance($courseid);

require_login($course);
require_capability('block/chaside:take_test', $context);

// Check if the block is added to the course
if (!$DB->record_exists('block_instances', array('blockname' => 'chaside', 'parentcontextid' => $context->id))) {
    redirect(new moodle_url('/course/view.php', array('id' => $courseid)));
}

// Redirect teachers/admins to admin page
if (has_capability('block/chaside:viewstudentdata', $context)) {
    $manage_url = new moodle_url('/blocks/chaside/admin_view.php', array('courseid' => $courseid));
    redirect($manage_url, get_string('teachers_redirect_message', 'block_chaside'));
}

$PAGE->set_url('/blocks/chaside/view.php', array('courseid' => $courseid, 'page' => $page));
$PAGE->set_title(get_string('pluginname', 'block_chaside'));
$PAGE->set_heading($course->fullname);
$PAGE->set_context($context);
$PAGE->requires->css('/blocks/chaside/styles.css');

// Inicializar el facade
$facade = new \block_chaside\facade();

// Verificar si ya existe una respuesta del usuario (en cualquier curso)
$existing_response = $DB->get_record('block_chaside_responses', array(
    'userid' => $USER->id
));

// Pagination settings
$questions_per_page = BLOCK_CHASIDE_QUESTIONS_PER_PAGE;
$total_questions = BLOCK_CHASIDE_TOTAL_QUESTIONS;
$total_pages = ceil($total_questions / $questions_per_page);

// SECURITY: Validate that user cannot skip pages without completing previous ones
if ($existing_response && $page > 1) {
    // Check all questions from page 1 to current page - 1
    $max_allowed_page = 1;
    
    for ($p = 1; $p < $page; $p++) {
        $page_start = ($p - 1) * $questions_per_page + 1;
        $page_end = min($p * $questions_per_page, $total_questions);
        $page_complete = true;
        
        for ($i = $page_start; $i <= $page_end; $i++) {
            $field = "q{$i}";
            if (!isset($existing_response->$field) || $existing_response->$field === null) {
                $page_complete = false;
                break;
            }
        }
        
        if ($page_complete) {
            $max_allowed_page = $p + 1;
        } else {
            break;
        }
    }
    
    // If trying to access a page beyond allowed, redirect to max allowed
    if ($page > $max_allowed_page) {
        redirect(new moodle_url('/blocks/chaside/view.php', 
                 array('courseid' => $courseid, 'page' => $max_allowed_page)));
    }
}

// If coming from "continue test" link without explicit page, calculate which page to show
if ($existing_response && !isset($_GET['page'])) {
    // Find first unanswered question
    $first_unanswered = null;
    for ($i = 1; $i <= $total_questions; $i++) {
        $field = "q{$i}";
        if (!isset($existing_response->$field) || $existing_response->$field === null) {
            $first_unanswered = $i;
            break;
        }
    }
    
    // Calculate page for first unanswered question
    if ($first_unanswered !== null) {
        $page = ceil($first_unanswered / $questions_per_page);
    }
}

// Calculate question range for current page (needed for rendering)
$start_question = ($page - 1) * $questions_per_page + 1;
$end_question = min($page * $questions_per_page, $total_questions);

// Calculate how many questions are answered
$answered_count = 0;
if ($existing_response) {
    for ($i = 1; $i <= $total_questions; $i++) {
        $field = "q{$i}";
        if (isset($existing_response->$field) && $existing_response->$field !== null) {
            $answered_count++;
        }
    }
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    require_sesskey();
    
    // If the test is already complete, DON'T allow modifications
    if ($existing_response && $existing_response->is_completed) {
        $results_url = new moodle_url('/blocks/chaside/view_results.php', array('courseid' => $courseid));
        redirect($results_url);
    }
    
    $action = optional_param('action', 'save', PARAM_ALPHA);

    // Prepare helper to get responses safely
    function get_answers_from_post() {
        $responses = array();
        for ($i = 1; $i <= BLOCK_CHASIDE_TOTAL_QUESTIONS; $i++) {
            $response = optional_param("q{$i}", null, PARAM_INT);
            if ($response !== null) {
                $responses["q{$i}"] = $response;
            }
        }
        return $responses;
    }

    $posted_responses = get_answers_from_post();
    
    // Prepare base data
    $data = new stdClass();
    $data->userid = $USER->id;
    $data->timemodified = time();
    $data->is_completed = 0;
    
    // If a previous response exists, retain all existing data.
    if ($existing_response) {
        $data->id = $existing_response->id;
        $data->timecreated = $existing_response->timecreated;
        
        // Copy all existing answers from DB to preserve them
        for ($i = 1; $i <= BLOCK_CHASIDE_TOTAL_QUESTIONS; $i++) {
            if (isset($existing_response->{"q{$i}"})) {
                $data->{"q{$i}"} = $existing_response->{"q{$i}"};
            }
        }
    } else {
        $data->timecreated = time();
    }
    
    // OVERWRITE with new answers from current POST (this is crucial: trust POST over DB for current page)
    foreach ($posted_responses as $key => $val) {
        $data->$key = $val;
    }
    
    // -------------------------------------------------------------------------
    // AUTO-SAVE LOGIC
    // -------------------------------------------------------------------------
    if ($action === 'autosave') {
        header('Content-Type: application/json');
        
        // Optimize: If nothing changed from DB, don't write.
        // But for safety against race conditions, we usually write.
        // Let's just trust the write.

        if (empty($posted_responses) && !$existing_response) {
             echo json_encode(['success' => true, 'message' => 'No data to save']);
             exit;
        }

        try {
            if ($existing_response) {
                // To avoid "century" update, maybe check if update is needed?
                // But Moodle update_record is fast.
                $DB->update_record('block_chaside_responses', $data);
            } else {
                // ... logic ...

                $race_check = $DB->get_record('block_chaside_responses', array('userid' => $USER->id));
                if ($race_check) {
                    $data->id = $race_check->id;
                    $DB->update_record('block_chaside_responses', $data);
                } else {
                    $DB->insert_record('block_chaside_responses', $data);
                }
            }
            echo json_encode(['success' => true]);
        } catch (Exception $e) {
            echo json_encode(['success' => false, 'error' => $e->getMessage()]);
        }
        exit;
    }

    // -------------------------------------------------------------------------
    // NAVIGATION LOGIC (Previous / Next)
    // -------------------------------------------------------------------------
    if ($action === 'previous' || $action === 'next') {
        // First: SAVE EVERYTHING WE HAVE from the POST
        try {
             if ($existing_response) {
                $DB->update_record('block_chaside_responses', $data);
            } else {
                 // Double check race condition again
                $race_check = $DB->get_record('block_chaside_responses', array('userid' => $USER->id));
                if ($race_check) {
                    $data->id = $race_check->id;
                    $DB->update_record('block_chaside_responses', $data);
                } else {
                    $DB->insert_record('block_chaside_responses', $data);
                }
            }
        } catch (Exception $e) {
             // If save fails, we should probably stop and show error
             print_error('Error saving data: ' . $e->getMessage());
        }

        if ($action === 'previous') {
             if ($page > 1) {
                redirect(new moodle_url('/blocks/chaside/view.php', array('courseid' => $courseid, 'page' => $page - 1)));
            }
        } else {
            // ACTION: NEXT
            if ($page < $total_pages) {
                // We rely on the top-of-page Security check to validate that this page was completed.
                // We just save what we have and move on. 
                // If the user didn't answer everything, the Security check on the next page load 
                // will bounce them back to this page.
                redirect(new moodle_url('/blocks/chaside/view.php', array('courseid' => $courseid, 'page' => $page + 1)));
            }
        }
    }
    
    // -------------------------------------------------------------------------
    // FINISH LOGIC
    // -------------------------------------------------------------------------
    if ($action === 'finish') {
        // Collect entire dataset again to be 100% sure
        // We use $data which already has DB merge + POST merge
        
        $completed = true;
        $missing_questions = [];
        
        for ($i = 1; $i <= $total_questions; $i++) {
             if (!isset($data->{"q{$i}"}) || $data->{"q{$i}"} === null) {
                $completed = false;
                $missing_questions[] = $i;
            }
        }
        
        if ($completed) {
            // Prepare record for final save
            $final_data = (array)$data; // convert back to array if calculate_scores needs it, or adjust
            
            $scores = $facade->calculate_scores($final_data);
            $final_data['score_c'] = $scores['C'];
            $final_data['score_h'] = $scores['H'];
            $final_data['score_a'] = $scores['A'];
            $final_data['score_s'] = $scores['S'];
            $final_data['score_i'] = $scores['I'];
            $final_data['score_d'] = $scores['D'];
            $final_data['score_e'] = $scores['E'];
            $final_data['is_completed'] = 1;
            $final_data['timemodified'] = time();
            
            if ($existing_response) {
                 $DB->update_record('block_chaside_responses', $final_data);
            } else {
                // Should not happen usually on finish if pages were valid, but handled
                 $DB->insert_record('block_chaside_responses', $final_data);
            }
            
            redirect(new moodle_url('/blocks/chaside/view_results.php', array('courseid' => $courseid)), get_string('test_completed_success', 'block_chaside'), null, \core\output\notification::NOTIFY_SUCCESS);
        } else {
             // Redirect to first missing
            $first_unanswered = $missing_questions[0];
            $redirect_page = ceil($first_unanswered / $questions_per_page);
            
            redirect(new moodle_url('/blocks/chaside/view.php', array('courseid' => $courseid, 'page' => $redirect_page)));
        }
    }
}

// If the test is already completed, redirect to results (DO NOT allow retake)
if ($existing_response && $existing_response->is_completed) {
    $results_url = new moodle_url('/blocks/chaside/view_results.php', array('courseid' => $courseid));
    redirect($results_url);
}

echo $OUTPUT->header();

// Prepare Mustache context
$data = [
    'iconurl' => (new moodle_url('/blocks/chaside/pix/icon.svg'))->out(),
    'title' => get_string('pluginname', 'block_chaside'),
    'description' => get_string('test_description', 'block_chaside'),
    'str_note' => get_string('note', 'block_chaside'),
    'str_all_questions_required' => get_string('all_questions_required', 'block_chaside'),
    'sesskey' => sesskey(),
    'questions' => [],
    'show_previous' => ($page > 1),
    'show_next' => ($page < $total_pages),
    'show_finish' => ($page == $total_pages), // Changed logic slightly, finish only on last page
    'str_yes' => get_string('yes', 'block_chaside'),
    'str_no' => get_string('no', 'block_chaside'),
    'str_previous' => get_string('btn_previous', 'block_chaside'),
    'str_next' => get_string('btn_next', 'block_chaside'),
    'str_finish' => get_string('btn_finish', 'block_chaside'),
];

// Logic adjustment: Original code showed finish button ONLY if page >= total_pages.
// However, the original loop was: if ($page < $total_pages) { NEXT } else { FINISH }.
// So on the last page, NEXT is hidden and FINISH is shown. Correct.

for ($i = $start_question; $i <= $end_question; $i++) {
    $question_text = get_string("q{$i}", 'block_chaside');
    $current_value = '';
    
    if ($existing_response && isset($existing_response->{"q{$i}"})) {
        $current_value = (string)$existing_response->{"q{$i}"}; // Ensure string comparison
    }

    $data['questions'][] = [
        'number' => $i,
        'text' => $question_text,
        'yes_checked' => ($current_value === '1'),
        'no_checked' => ($current_value === '0')
    ];
}

// Calculate logic for auto-scroll highlighting
$auto_scroll = false;
if ($existing_response && $answered_count > 0 && $answered_count < 98 && !$scroll_to_finish) {
    $auto_scroll = true;
}

$js_opts = [
    'scroll_to_finish' => (bool)$scroll_to_finish,
    'auto_scroll_unanswered' => (bool)$auto_scroll
];

$PAGE->requires->js_call_amd('block_chaside/test_view', 'init', [$js_opts]);

echo $OUTPUT->render_from_template('block_chaside/test_view', $data);

echo $OUTPUT->footer();
