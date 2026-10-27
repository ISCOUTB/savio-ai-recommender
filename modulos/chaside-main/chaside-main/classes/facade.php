<?php
/**
 * CHASIDE Facade
 *
 * @package    block_chaside
 * @copyright  2026 SAVIO - Sistema de Aprendizaje Virtual Interactivo (UTB)
 * @author     SAVIO Development Team
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace block_chaside;

defined('MOODLE_INTERNAL') || die();

class facade {
    public function get_question_mapping() {
        // Official mapping of the CHASIDE test - INTERESTS (70 questions) and APTITUDES (28 questions)
        return array(
            // INTERESTS - C: [1, 12, 20, 53, 64, 71, 78, 85, 91, 98]
            1 => 'C', 12 => 'C', 20 => 'C', 53 => 'C', 64 => 'C', 71 => 'C', 78 => 'C', 85 => 'C', 91 => 'C', 98 => 'C',
            // INTERESTS - H: [9, 25, 34, 41, 56, 67, 74, 80, 89, 95]
            9 => 'H', 25 => 'H', 34 => 'H', 41 => 'H', 56 => 'H', 67 => 'H', 74 => 'H', 80 => 'H', 89 => 'H', 95 => 'H',
            // INTERESTS - A: [3, 11, 21, 28, 36, 45, 50, 57, 81, 96]
            3 => 'A', 11 => 'A', 21 => 'A', 28 => 'A', 36 => 'A', 45 => 'A', 50 => 'A', 57 => 'A', 81 => 'A', 96 => 'A',
            // INTERESTS - S: [8, 16, 23, 33, 44, 52, 62, 70, 87, 92]
            8 => 'S', 16 => 'S', 23 => 'S', 33 => 'S', 44 => 'S', 52 => 'S', 62 => 'S', 70 => 'S', 87 => 'S', 92 => 'S',
            // INTERESTS - I: [6, 19, 27, 38, 47, 54, 60, 75, 83, 97]
            6 => 'I', 19 => 'I', 27 => 'I', 38 => 'I', 47 => 'I', 54 => 'I', 60 => 'I', 75 => 'I', 83 => 'I', 97 => 'I',
            // INTERESTS - D: [5, 14, 24, 31, 37, 48, 58, 65, 73, 84]
            5 => 'D', 14 => 'D', 24 => 'D', 31 => 'D', 37 => 'D', 48 => 'D', 58 => 'D', 65 => 'D', 73 => 'D', 84 => 'D',
            // INTERESTS - E: [17, 32, 35, 42, 49, 61, 68, 77, 88, 93]
            17 => 'E', 32 => 'E', 35 => 'E', 42 => 'E', 49 => 'E', 61 => 'E', 68 => 'E', 77 => 'E', 88 => 'E', 93 => 'E',
            
            // APTITUDES - C: [2, 15, 46, 51]
            2 => 'C', 15 => 'C', 46 => 'C', 51 => 'C',
            // APTITUDES - H: [30, 63, 72, 86]
            30 => 'H', 63 => 'H', 72 => 'H', 86 => 'H',
            // APTITUDES - A: [22, 39, 76, 82]
            22 => 'A', 39 => 'A', 76 => 'A', 82 => 'A',
            // APTITUDES - S: [4, 29, 40, 69]
            4 => 'S', 29 => 'S', 40 => 'S', 69 => 'S',
            // APTITUDES - I: [10, 26, 59, 90]
            10 => 'I', 26 => 'I', 59 => 'I', 90 => 'I',
            // APTITUDES - D: [13, 18, 43, 66]
            13 => 'D', 18 => 'D', 43 => 'D', 66 => 'D',
            // APTITUDES - E: [7, 55, 79, 94]
            7 => 'E', 55 => 'E', 79 => 'E', 94 => 'E'
        );
    }
    
    public function calculate_scores($responses) {
        $mapping = $this->get_question_mapping();
        $scores = array('C' => 0, 'H' => 0, 'A' => 0, 'S' => 0, 'I' => 0, 'D' => 0, 'E' => 0);
        
        for ($i = 1; $i <= 98; $i++) {
            if (isset($responses["q{$i}"]) && $responses["q{$i}"] == 1) {
                $area = $mapping[$i];
                $scores[$area]++;
            }
        }
        
        return $scores;
    }
    
    /**
     * Calculate detailed scores separating interests and aptitudes
     */
    public function calculate_detailed_scores($responses) {
        $mapping = $this->get_question_mapping();
        
        // Initialize scores
        $scores = array();
        foreach (['C', 'H', 'A', 'S', 'I', 'D', 'E'] as $area) {
            $scores[$area] = array(
                'interes_score' => 0,
                'aptitud_score' => 0
            );
        }
        
        // Interest questions (70 total)
        $interest_questions = array(
            'C' => [1, 12, 20, 53, 64, 71, 78, 85, 91, 98],
            'H' => [9, 25, 34, 41, 56, 67, 74, 80, 89, 95],
            'A' => [3, 11, 21, 28, 36, 45, 50, 57, 81, 96],
            'S' => [8, 16, 23, 33, 44, 52, 62, 70, 87, 92],
            'I' => [6, 19, 27, 38, 47, 54, 60, 75, 83, 97],
            'D' => [5, 14, 24, 31, 37, 48, 58, 65, 73, 84],
            'E' => [17, 32, 35, 42, 49, 61, 68, 77, 88, 93]
        );
        
        // Aptitude questions (28 total)
        $aptitude_questions = array(
            'C' => [2, 15, 46, 51],
            'H' => [30, 63, 72, 86],
            'A' => [22, 39, 76, 82],
            'S' => [4, 29, 40, 69],
            'I' => [10, 26, 59, 90],
            'D' => [13, 18, 43, 66],
            'E' => [7, 55, 79, 94]
        );
        
        // Count interest scores
        foreach ($interest_questions as $area => $questions) {
            foreach ($questions as $q) {
                if (isset($responses["q{$q}"]) && $responses["q{$q}"] == 1) {
                    $scores[$area]['interes_score']++;
                }
            }
        }
        
        // Count aptitude scores
        foreach ($aptitude_questions as $area => $questions) {
            foreach ($questions as $q) {
                if (isset($responses["q{$q}"]) && $responses["q{$q}"] == 1) {
                    $scores[$area]['aptitud_score']++;
                }
            }
        }
        
        return $scores;
    }
    
    /**
     * Calculate percentages for interests, aptitudes and total
     */
    public function calculate_percentages($scores) {
        $percentages = array();
        
        foreach ($scores as $area => $area_scores) {
            $total_score = $area_scores['interes_score'] + $area_scores['aptitud_score'];
            
            $percentages[$area] = array(
                'pct_interes' => round(100 * $area_scores['interes_score'] / 10, 1), // Max 10 interest questions per area
                'pct_aptitud' => round(100 * $area_scores['aptitud_score'] / 4, 1),   // Max 4 aptitude questions per area
                'pct_total' => round(100 * $total_score / 14, 1)                      // Max 14 total per area
            );
        }
        
        return $percentages;
    }
    
    /**
     * Determine levels based on total percentage
     */
    public function determine_levels($percentages) {
        $levels = array();
        
        foreach ($percentages as $area => $pcts) {
            $pct_total = $pcts['pct_total'];
            
            if ($pct_total >= 80.0) {
                $levels[$area] = 'level_alto';
            } elseif ($pct_total >= 60.0) {
                $levels[$area] = 'level_medio';
            } elseif ($pct_total >= 40.0) {
                $levels[$area] = 'level_emergente';
            } else {
                $levels[$area] = 'level_bajo';
            }
        }
        
        return $levels;
    }
    
    /**
     * Detect interest-aptitude gaps
     */
    public function detect_gaps($percentages) {
        $gaps = array();
        $threshold = 20.0; // 20 percentage points
        
        foreach ($percentages as $area => $pcts) {
            $diff = $pcts['pct_interes'] - $pcts['pct_aptitud'];
            
            if ($diff >= $threshold) {
                $gaps[$area] = 'gap_interest_higher';
            } elseif ($diff <= -$threshold) {
                $gaps[$area] = 'gap_aptitude_higher';
            } else {
                $gaps[$area] = 'gap_balanced';
            }
        }
        
        return $gaps;
    }
    
    /**
     * Get top areas with official CHASIDE tiebreaker rules
     */
    public function get_top_areas_v2($scores, $limit = 2) {
        $areas_with_totals = array();
        
        foreach ($scores as $area => $area_scores) {
            $total = $area_scores['interes_score'] + $area_scores['aptitud_score'];
            $areas_with_totals[] = array(
                'area' => $area,
                'total_score' => $total,
                'interes_score' => $area_scores['interes_score'],
                'aptitud_score' => $area_scores['aptitud_score'],
                'gap' => abs($area_scores['interes_score'] - $area_scores['aptitud_score'])
            );
        }
        
        // Sort with tiebreaker rules:
        // 1. Higher total_score
        // 2. Higher aptitud_score
        // 3. Lower gap (|interes - aptitud|)
        // 4. Alphabetical by area
        usort($areas_with_totals, function($a, $b) {
            if ($a['total_score'] != $b['total_score']) {
                return $b['total_score'] - $a['total_score'];
            }
            if ($a['aptitud_score'] != $b['aptitud_score']) {
                return $b['aptitud_score'] - $a['aptitud_score'];
            }
            if ($a['gap'] != $b['gap']) {
                return $a['gap'] - $b['gap'];
            }
            return strcmp($a['area'], $b['area']);
        });
        
        return array_slice($areas_with_totals, 0, $limit);
    }
    
    /**
     * Generate complete results JSON according to official CHASIDE format
     */
    public function generate_results_json($responses, $meta = array()) {
        // Calculate detailed scores
        $detailed_scores = $this->calculate_detailed_scores($responses);
        $percentages = $this->calculate_percentages($detailed_scores);
        $levels = $this->determine_levels($percentages);
        $gaps = $this->detect_gaps($percentages);
        $top_areas = $this->get_top_areas_v2($detailed_scores, 2);
        
        // Area labels
        $labels = array(
            'C' => get_string('area_c', 'block_chaside'),
            'H' => get_string('area_h', 'block_chaside'),
            'A' => get_string('area_a', 'block_chaside'),
            'S' => get_string('area_s', 'block_chaside'),
            'I' => get_string('area_i', 'block_chaside'),
            'D' => get_string('area_d', 'block_chaside'),
            'E' => get_string('area_e', 'block_chaside')
        );
        
        // Build executive summary
        $top1 = !empty($top_areas) ? $top_areas[0] : null;
        $top2 = count($top_areas) > 1 ? $top_areas[1] : null;
        
        $quick_reading = '';
        $gap_alerts = array();
        
        if ($top1) {
            $top1['gap_type'] = $gaps[$top1['area']]; // Add gap type
            $quick_reading = get_string('highest_strength_in', 'block_chaside') . " " . $labels[$top1['area']];
            if ($top2) {
                $top2['gap_type'] = $gaps[$top2['area']]; // Add gap type
                $quick_reading .= " y " . $labels[$top2['area']];
            }
        }
        
        // Detect significant gaps for alerts
        foreach ($gaps as $area => $gap_type) {
            if ($gap_type != 'gap_balanced') {
                $gap_alerts[] = array(
                    'area' => $area,
                    'tipo' => get_string($gap_type, 'block_chaside')
                );
            }
        }
        
        // Build main table
        $main_table = array();
        foreach (['C', 'H', 'A', 'S', 'I', 'D', 'E'] as $area) {
            
            // Logic for interpretation
            $level_key = $levels[$area]; // level_alto, level_medio, level_emergente, level_bajo
            $gap_key = $gaps[$area];     // gap_interest_higher, gap_aptitude_higher, gap_balanced
            
            $interpretation_key = 'interpretation_' . strtolower($area) . '_low'; // Default to low logic
            
            if ($level_key !== 'level_bajo') {
                $suffix_level = '';
                if ($level_key === 'level_alto') $suffix_level = 'high';
                elseif ($level_key === 'level_medio') $suffix_level = 'medium';
                elseif ($level_key === 'level_emergente') $suffix_level = 'emerging';
                
                $suffix_gap = 'balanced';
                if ($gap_key === 'gap_interest_higher') $suffix_gap = 'interest';
                elseif ($gap_key === 'gap_aptitude_higher') $suffix_gap = 'aptitude';
                
                $interpretation_key = 'interpretation_' . strtolower($area) . '_' . $suffix_level . '_' . $suffix_gap;
            } else {
                 $interpretation_key = 'interpretation_' . strtolower($area) . '_low';
            }

            $main_table[] = array(
                'area' => $area,
                'label' => $labels[$area],
                'interes' => array(
                    'score' => $detailed_scores[$area]['interes_score'],
                    'pct' => $percentages[$area]['pct_interes']
                ),
                'aptitud' => array(
                    'score' => $detailed_scores[$area]['aptitud_score'],
                    'pct' => $percentages[$area]['pct_aptitud']
                ),
                'total' => array(
                    'score' => $detailed_scores[$area]['interes_score'] + $detailed_scores[$area]['aptitud_score'],
                    'pct' => $percentages[$area]['pct_total']
                ),
                'nivel' => get_string($levels[$area], 'block_chaside'),
                'brecha' => get_string($gaps[$area], 'block_chaside'),
                'interpretacion_breve' => get_string($interpretation_key, 'block_chaside')
            );
        }
        
        // Generate recommendations
        $recommendations = array(
            get_string('rec_prioritize_top', 'block_chaside')
        );
        
        if (!empty($gap_alerts)) {
            foreach ($gap_alerts as $alert) {
                if ($alert['tipo'] == get_string('gap_interest_higher', 'block_chaside')) {
                    $recommendations[] = get_string('rec_interest_higher', 'block_chaside');
                } elseif ($alert['tipo'] == get_string('gap_aptitude_higher', 'block_chaside')) {
                    $recommendations[] = get_string('rec_aptitude_higher', 'block_chaside');
                }
            }
        } else {
            $recommendations[] = get_string('rec_balanced_development', 'block_chaside');
        }
        
        $recommendations[] = get_string('rec_explore_combinations', 'block_chaside');
        
        // Build final result
        $result = array(
            'meta' => $meta,
            'resumen_ejecutivo' => array(
                'top1' => $top1 ? array(
                    'area' => $top1['area'],
                    'label' => $labels[$top1['area']],
                    'gap_type' => $top1['gap_type'] ?? null,
                    'total' => $top1['total_score'],
                    'pct_total' => $percentages[$top1['area']]['pct_total'],
                    'i' => $top1['interes_score'],
                    'a' => $top1['aptitud_score']
                ) : null,
                'top2' => $top2 ? array(
                    'area' => $top2['area'],
                    'label' => $labels[$top2['area']],
                    'gap_type' => $top2['gap_type'] ?? null,
                    'total' => $top2['total_score'],
                    'pct_total' => $percentages[$top2['area']]['pct_total'],
                    'i' => $top2['interes_score'],
                    'a' => $top2['aptitud_score']
                ) : null,
                'lectura_rapida' => $quick_reading,
                'alertas_brecha' => $gap_alerts
            ),
            'tabla_principal' => $main_table,
            'recomendaciones' => $recommendations,
            'apendice_opcional' => array(
                'nota' => get_string('orientation_note', 'block_chaside')
            )
        );
        
        return $result;
    }
}
