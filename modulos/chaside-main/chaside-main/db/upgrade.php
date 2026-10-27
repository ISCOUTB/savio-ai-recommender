<?php
defined('MOODLE_INTERNAL') || die();

function xmldb_block_chaside_upgrade($oldversion) {
    global $DB;
    $dbman = $DB->get_manager();

    if ($oldversion < 2025120901) {
        // Define index to be added to block_chaside_responses
        $table = new xmldb_table('block_chaside_responses');
        
        // Drop old non-unique index if exists
        $old_index = new xmldb_index('userid_courseid', XMLDB_INDEX_NOTUNIQUE, ['userid', 'courseid']);
        if ($dbman->index_exists($table, $old_index)) {
            $dbman->drop_index($table, $old_index);
        }
        
        // Add unique index on userid to prevent duplicate tests per user
        $index = new xmldb_index('userid_unique', XMLDB_INDEX_UNIQUE, ['userid']);
        if (!$dbman->index_exists($table, $index)) {
            $dbman->add_index($table, $index);
        }

        // CHASIDE savepoint reached.
        upgrade_block_savepoint(true, 2025120901, 'chaside');
    }

    // Fix userid index to ensure it's UNIQUE and remove any duplicates
    if ($oldversion < 2025121101) {
        $table = new xmldb_table('block_chaside_responses');
        
        // Drop any existing non-unique indexes on userid (Moodle may have created with different names)
        $possible_index_names = ['mdl_blocchasresp_use_ix', 'userid', 'userid_idx', 'userid_ix'];
        foreach ($possible_index_names as $index_name) {
            $index = new xmldb_index($index_name, XMLDB_INDEX_NOTUNIQUE, ['userid']);
            if ($dbman->index_exists($table, $index)) {
                $dbman->drop_index($table, $index);
            }
        }
        
        // Remove duplicate rows before adding unique constraint
        // Keep the oldest record (lowest id) for each userid
        $sql = "SELECT userid, MIN(id) as keepid 
                FROM {block_chaside_responses} 
                GROUP BY userid 
                HAVING COUNT(*) > 1";
        
        $duplicates = $DB->get_records_sql($sql);
        
        if (!empty($duplicates)) {
            foreach ($duplicates as $dup) {
                // Delete all records for this userid except the one we want to keep
                $DB->execute(
                    "DELETE FROM {block_chaside_responses} 
                     WHERE userid = :userid AND id != :keepid",
                    ['userid' => $dup->userid, 'keepid' => $dup->keepid]
                );
            }
        }
        
        // Now add/recreate the UNIQUE index
        $unique_index = new xmldb_index('userid_unique', XMLDB_INDEX_UNIQUE, ['userid']);
        if (!$dbman->index_exists($table, $unique_index)) {
            $dbman->add_index($table, $unique_index);
        }
        
        upgrade_block_savepoint(true, 2025121101, 'chaside');
    }

    // Remove courseid field as functionality is now cross-course
    if ($oldversion < 2025121700) {
        $table = new xmldb_table('block_chaside_responses');
        
        // Drop foreign key constraint first if it exists
        $key = new xmldb_key('courseid', XMLDB_KEY_FOREIGN, ['courseid'], 'course', ['id']);
        $dbman->drop_key($table, $key);
        
        // Drop the courseid field
        $field = new xmldb_field('courseid');
        if ($dbman->field_exists($table, $field)) {
            $dbman->drop_field($table, $field);
        }
        
        upgrade_block_savepoint(true, 2025121700, 'chaside');
    }

    return true;
}
