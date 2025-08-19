#!/usr/bin/env php
<?php
/**
 * Migration Script: Convert alarm .conf files to alarms.json
 * 
 * This script migrates existing alarm configuration files from the old
 * .conf format to the new single alarms.json format.
 * 
 * Usage: php migrate_alarms_to_json.php
 */

// Include the AlarmManager class
require_once __DIR__ . '/../htdocs/inc.alarmManager.php';

echo "=== Phoniebox Alarms Migration Script ===\n";
echo "Converting alarm .conf files to alarms.json format...\n\n";

try {
    // Initialize the alarm manager
    $alarmManager = new AlarmManager();
    
    // Check if migration is needed
    $alarmsDir = dirname($alarmManager->getAlarmsFile()) . '/alarms';
    
    if (!is_dir($alarmsDir)) {
        echo "No existing alarms directory found. Migration not needed.\n";
        exit(0);
    }
    
    $confFiles = glob($alarmsDir . '/*.conf');
    if (empty($confFiles)) {
        echo "No .conf files found in alarms directory. Migration not needed.\n";
        exit(0);
    }
    
    echo "Found " . count($confFiles) . " alarm configuration files to migrate:\n";
    foreach ($confFiles as $file) {
        echo "  - " . basename($file) . "\n";
    }
    echo "\n";
    
    // Perform migration
    echo "Starting migration...\n";
    $result = $alarmManager->migrateFromConfFiles();
    
    if ($result) {
        echo "✓ Migration completed successfully!\n";
        echo "✓ Old .conf files have been backed up and removed.\n";
        echo "✓ All alarms are now stored in alarms.json\n";
        
        // Display migrated alarms
        $alarms = $alarmManager->getAllAlarms();
        echo "\nMigrated " . count($alarms) . " alarms:\n";
        foreach ($alarms as $alarm) {
            $time = $alarm['hour'] . ':' . str_pad($alarm['minute'], 2, '0', STR_PAD_LEFT) . ' ' . $alarm['ampm'];
            $status = $alarm['enabled'] ? 'Enabled' : 'Disabled';
            echo "  - ID: {$alarm['id']}, Time: {$time}, Days: " . implode(',', $alarm['days']) . ", Status: {$status}\n";
        }
        
        echo "\nMigration Summary:\n";
        echo "  - Old format: " . count($confFiles) . " .conf files\n";
        echo "  - New format: 1 alarms.json file\n";
        echo "  - Backup created: " . basename($alarmsDir) . "_backup_" . date('Y-m-d_H-i-s') . "\n";
        
    } else {
        echo "✗ Migration failed!\n";
        exit(1);
    }
    
} catch (Exception $e) {
    echo "✗ Error during migration: " . $e->getMessage() . "\n";
    exit(1);
}

echo "\n=== Migration Complete ===\n";
echo "Your alarms are now stored in a single alarms.json file.\n";
echo "The old .conf files have been safely backed up.\n";
echo "All alarm functionality will continue to work as before.\n";
?> 