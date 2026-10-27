<?php
/**
 * CHASIDE Block
 *
 * @package    block_chaside
 * @copyright  2026 SAVIO - Sistema de Aprendizaje Virtual Interactivo (UTB)
 * @author     SAVIO Development Team
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

require_once($CFG->dirroot . '/blocks/moodleblock.class.php');
require_once($CFG->dirroot . '/lib/enrollib.php');

class block_chaside extends block_base {
    
    public function init() {
        $this->title = get_string('pluginname', 'block_chaside');
    }
    
    public function get_content() {
        global $USER, $COURSE, $OUTPUT, $DB, $CFG, $PAGE;
        
        if ($this->content !== null) {
            return $this->content;
        }
        
        $this->content = new stdClass();
        $this->content->text = '';
        $this->content->footer = '';
        
        if (!isloggedin() || empty($COURSE->id)) {
            return $this->content;
        }

        $context = context_course::instance($COURSE->id);
        
        $PAGE->requires->css('/blocks/chaside/styles.css');
        
        $data = [];
        $template = 'block_chaside/content';
        
        // Configuration
        $showdescriptions = false;
        if (!empty($this->config) && !empty($this->config->showdescriptions)) {
            $showdescriptions = true;
        }
        $data['showdescriptions'] = $showdescriptions;

        // Las cifras y resultados solo están disponibles en el panel protegido.
        if (has_capability('block/chaside:viewstudentdata', $context)) {
            $this->content->text = $this->get_management_launcher();
            return $this->content;
        } else if (has_capability('block/chaside:take_test', $context)) {
            // Student view: check if test is completed (in any course)
            $response = $DB->get_record('block_chaside_responses', array(
                'userid' => $USER->id
            ));
            
            if ($response && $response->is_completed) {
                // Show results
                $results_data = $this->get_student_results_data($response);
                $results_data['showdescriptions'] = $showdescriptions;
                $data['results'] = $results_data;
                $data['iscompleted'] = true;
            } else {
                // Show invitation
                $invite_data = $this->get_student_invite_data($response);
                $invite_data['showdescriptions'] = $showdescriptions;
                $data['invitation'] = $invite_data;
                $data['iscompleted'] = false;
            }
        }
        
        if (!empty($data)) {
            $this->content->text = $OUTPUT->render_from_template($template, $data);
        }
           
        return $this->content;
    }

    private function get_management_launcher() {
        global $COURSE, $OUTPUT;

        return $OUTPUT->render_from_template('block_chaside/admin_launcher', [
            'icon_html' => '<img src="' . (new moodle_url('/blocks/chaside/pix/icon.svg'))->out(false) . '" alt="" style="width: 4.25rem; height: 4.25rem; display: block; margin: 0 auto;">',
            'security_label' => get_string('sensitive_data', 'block_chaside'),
            'title' => get_string('management_title', 'block_chaside'),
            'admin_url' => (new moodle_url('/blocks/chaside/admin_view.php', ['courseid' => $COURSE->id]))->out(false),
            'button_label' => get_string('open_admin_panel', 'block_chaside'),
        ]);
    }

    private function get_management_summary_data($context) {
        global $DB, $COURSE, $PAGE;

        // Use get_enrolled_sql for performance
        // This gets the SQL to find users enrolled in the course with the capability
        list($esql, $params) = get_enrolled_sql($context, 'block/chaside:take_test', 0, true);
        
        // Count total enrolled "students" (users with take_test capability)
        $sql_enrolled = "SELECT COUNT(DISTINCT u.id) FROM {user} u JOIN ($esql) je ON je.id = u.id WHERE u.deleted = 0";
        $total_enrolled = $DB->count_records_sql($sql_enrolled, $params);

        // Count responses for these enrolled users
        // Completed
        $sql_completed = "SELECT COUNT(r.id) FROM {block_chaside_responses} r 
                          JOIN ($esql) je ON je.id = r.userid 
                          WHERE r.is_completed = 1";
        $total_completed = $DB->count_records_sql($sql_completed, $params);
        
        // In Progress (Total responses - Completed)
        $sql_total_responses = "SELECT COUNT(r.id) FROM {block_chaside_responses} r 
                                JOIN ($esql) je ON je.id = r.userid";
        $count_responses = $DB->count_records_sql($sql_total_responses, $params);
        $total_in_progress = $count_responses - $total_completed;

        $completion_rate = $total_enrolled > 0 ? ($total_completed / $total_enrolled) * 100 : 0;

        $data = [
            'iconurl' => (new moodle_url('/blocks/chaside/pix/icon.svg'))->out(),
            'title' => get_string('management_title', 'block_chaside'),
            'subtitle' => get_string('course_overview', 'block_chaside'),
            'completion_rate' => number_format($completion_rate, 1),
            'str_completion_rate' => get_string('completion_rate', 'block_chaside'),
            'total_completed' => $total_completed,
            'str_completed' => get_string('completed', 'block_chaside'),
            'total_in_progress' => $total_in_progress,
            'str_in_progress' => get_string('in_progress', 'block_chaside'),
            'total_enrolled' => $total_enrolled,
            'str_of' => get_string('of', 'block_chaside'),
            'str_students_completed' => get_string('students_completed', 'block_chaside'),
            'str_recent_completions' => get_string('recent_completions', 'block_chaside'),
            'dashboard_url' => (new moodle_url('/blocks/chaside/admin_view.php', ['courseid' => $COURSE->id]))->out(false),
            'str_admin_dashboard' => get_string('admin_dashboard_invitation', 'block_chaside'),
        ];

        // Recent Activity
        if ($total_completed > 0) {
            $sql_recent = "SELECT r.id, u.firstname, u.lastname, r.timemodified 
                           FROM {block_chaside_responses} r 
                           JOIN ($esql) je ON je.id = r.userid 
                           JOIN {user} u ON u.id = r.userid 
                           WHERE r.is_completed = 1 
                           ORDER BY r.timemodified DESC";
            $recent_records = $DB->get_records_sql($sql_recent, $params, 0, 3);
            
            if ($recent_records) {
                $items = [];
                foreach ($recent_records as $rec) {
                    $items[] = [
                        'name' => fullname($rec),
                        'date' => userdate($rec->timemodified, get_string('strftimedatefullshort'))
                    ];
                }
                $data['recent_activity'] = ['items' => $items];
            }
        }

        return $data;
    }

    private function get_student_results_data($response) {
        global $COURSE, $USER;
        
        $response_array = (array) $response;
        // Assume facade class is available/autoloaded
        $facade = new \block_chaside\facade();
        $meta = array(
            'nombre' => fullname($USER),
            'curso' => $COURSE->shortname,
            'fecha_aplicacion' => date('Y-m-d', $response->timemodified),
        );
        
        $results = $facade->generate_results_json($response_array, $meta);
        
        $data = [
            'iconurl' => (new moodle_url('/blocks/chaside/pix/icon.svg'))->out(),
            'str_completed_title' => get_string('test_completed', 'block_chaside'),
            'str_completed_subtitle' => get_string('your_results_here', 'block_chaside'),
            'description' => get_string('chaside_description', 'block_chaside'),
            'str_executive_summary' => get_string('executive_summary', 'block_chaside'),
            'str_gap_alerts' => get_string('gap_alerts', 'block_chaside'),
            'str_recommendations' => get_string('recommendations', 'block_chaside'),
            'view_results_url' => (new moodle_url('/blocks/chaside/view_results.php', ['courseid' => $COURSE->id]))->out(false),
            'str_view_detailed_results' => get_string('view_detailed_results', 'block_chaside')
        ];

        if (!empty($results['resumen_ejecutivo']['top1'])) {
            $data['top1'] = $results['resumen_ejecutivo']['top1'];
        }
        $area_icons = [
            'C' => 'fa-calculator',
            'H' => 'fa-university',
            'A' => 'fa-paint-brush',
            'S' => 'fa-user-md',
            'I' => 'fa-cogs',
            'D' => 'fa-shield',
            'E' => 'fa-leaf'
        ];

        // Process alerts first to have them ready
        $alert_map = array();
        if (!empty($results['resumen_ejecutivo']['alertas_brecha'])) {
             foreach ($results['resumen_ejecutivo']['alertas_brecha'] as $alert) {
                 $rawarea = isset($alert['area']) ? trim((string)$alert['area']) : '';
                 $areacode = '';
                 
                 if (preg_match('/^\s*([CHASIDE])\s*$/u', $rawarea, $m)) {
                     $areacode = $m[1];
                 } elseif (preg_match('/\(([CHASIDE])\)\s*$/u', $rawarea, $m)) {
                     $areacode = $m[1];
                 }
                 
                 // Fallback: Check if the string starts with one of the keys
                 if (!$areacode) {
                     foreach (array_keys($area_icons) as $code) {
                         if (strpos($rawarea, $code) !== false) {
                             $areacode = $code;
                             break;
                         }
                     }
                 }

                 if ($areacode) {
                     $alert_map[$areacode] = $alert['tipo'];
                 }
             }
        }
        $data['has_gap_alerts'] = false; // Hide separate list
        $data['alerts'] = [];

        // Common strings for results
        $data['str_total'] = get_string('total', 'block_chaside');
        $data['str_interests'] = get_string('interests', 'block_chaside');
        $data['str_aptitudes'] = get_string('aptitudes', 'block_chaside');

        // Gap strings for icons
        $txt_int_high = get_string('gap_interest_higher', 'block_chaside');
        $txt_apt_high = get_string('gap_aptitude_higher', 'block_chaside');

        foreach (['top1', 'top2'] as $key) {
            if (!empty($results['resumen_ejecutivo'][$key])) {
                $area_code = $results['resumen_ejecutivo'][$key]['area'];
                $data[$key] = $results['resumen_ejecutivo'][$key];
                $data[$key]['area_icon'] = $area_icons[$area_code] ?? 'fa-star';
                
                if (isset($data[$key]['gap_type']) && $data[$key]['gap_type'] === 'gap_balanced') {
                    $data[$key]['gap_alert'] = get_string('gap_balanced', 'block_chaside');
                    $data[$key]['gap_icon'] = 'fa-balance-scale';
                } elseif (isset($alert_map[$area_code])) {
                    $gap_msg = $alert_map[$area_code];
                    $data[$key]['gap_alert'] = $gap_msg;
                    // Determine icon
                    if ($gap_msg === $txt_int_high) {
                        $data[$key]['gap_icon'] = 'fa-heart';
                    } elseif ($gap_msg === $txt_apt_high) {
                        $data[$key]['gap_icon'] = 'fa-graduation-cap';
                    } else {
                        $data[$key]['gap_icon'] = 'fa-balance-scale';
                    }
                }
            }
        }

        // De-duplicate recommendations
        $rec_list = [];
        if (!empty($results['recomendaciones'])) {
            $rawrecs = (array)$results['recomendaciones'];
            $recommendationsunique = array();
            foreach ($rawrecs as $recommendation) {
                $raw = (string)$recommendation;
                $normalized = preg_replace('/\s+/u', ' ', trim($raw));
                if ($normalized === '') continue;
                if (!array_key_exists($normalized, $recommendationsunique)) {
                     $recommendationsunique[$normalized] = $raw;
                }
            }
            // Only first 2
            $count = 0;
            foreach ($recommendationsunique as $rec) {
                if ($count >= 2) break;
                $rec_list[] = ['text' => $rec];
                $count++;
            }
        }
        $data['recommendations'] = $rec_list;

        return $data;
    }

    private function get_student_invite_data($response) {
        global $COURSE;

        $data = [
            'iconurl' => (new moodle_url('/blocks/chaside/pix/icon.svg'))->out(),
            'str_vocational_orientation' => get_string('pluginname', 'block_chaside'),
            'str_discover_interests' => get_string('discover_your_interests', 'block_chaside'),
            'description' => get_string('chaside_description', 'block_chaside'),
             'str_what_is_chaside' => get_string('what_is_chaside', 'block_chaside'),
             'str_feature_98_questions' => get_string('feature_98_questions', 'block_chaside'),
             'str_feature_7_areas' => get_string('feature_7_areas', 'block_chaside'),
             'str_feature_instant_results' => get_string('feature_instant_results', 'block_chaside'),
        ];

        if ($response) {
            $data['inprogress'] = true;
            $answered_count = 0;
            for ($i = 1; $i <= 98; $i++) {
                if (isset($response->{"q{$i}"}) && $response->{"q{$i}"} !== null) {
                    $answered_count++;
                }
            }
            $progress_percentage = ($answered_count / 98) * 100;
            $all_answered = ($answered_count == 98);

            $data['answered_count'] = $answered_count;
            $data['progress_percentage'] = $progress_percentage;
            $data['progress_percentage_formatted'] = number_format($progress_percentage, 1);
            $data['str_your_progress'] = get_string('your_progress', 'block_chaside');
            $data['str_completed_status'] = get_string('completed_status', 'block_chaside');

            if ($all_answered) {
                 $data['all_answered'] = true;
                 $data['str_all_answered_title'] = get_string('all_answered_title', 'block_chaside');
                 $data['str_all_answered_message'] = get_string('all_answered_message', 'block_chaside');
                 
                 $data['button_text'] = get_string('finish_test_now', 'block_chaside');
                 $data['button_icon'] = 'fa-flag-checkered';
                 $data['button_class'] = 'btn-success';
                 $data['button_style'] = 'background: #28a745; border-color: #28a745;';
                 
                 $questions_per_page = 10;
                 $total_questions = 98;
                 $last_page = (int)ceil($total_questions / $questions_per_page);
                 $data['button_url'] = (new moodle_url('/blocks/chaside/view.php', array(
                    'courseid' => $COURSE->id,
                    'page' => $last_page,
                    'scroll_to_finish' => 1
                )))->out(false);

            } else {
                 $data['button_text'] = get_string('continue_test', 'block_chaside');
                 $data['button_icon'] = 'fa-play';
                 $data['button_class'] = 'btn-primary';
                 $data['button_style'] = 'background: linear-gradient(135deg, #ffb600 0%, #e6a300 100%); border-color: #ffb600;';
                 $data['button_url'] = (new moodle_url('/blocks/chaside/view.php', array(
                    'courseid' => $COURSE->id
                )))->out(false);
            }

        } else {
            $data['inprogress'] = false;
            $data['button_text'] = get_string('start_test', 'block_chaside');
            $data['button_icon'] = 'fa-rocket';
            $data['button_class'] = 'btn-primary';
            $data['button_style'] = 'background: linear-gradient(135deg, #ffb600 0%, #e6a300 100%); border-color: #ffb600;';
            $data['button_url'] = (new moodle_url('/blocks/chaside/view.php', array(
                'courseid' => $COURSE->id
            )))->out(false);
        }

        return $data;
    }
    
    public function applicable_formats() {
        return array('course' => true, 'my' => true);
    }
    
    public function has_config() {
        return false;
    }
}
