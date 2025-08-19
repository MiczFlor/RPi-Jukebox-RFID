#!/usr/bin/env php
<?php
/**
 * Test Script: Verify JSON-based AlarmManager functionality
 * 
 * This script tests the new JSON-based alarm management system to ensure
 * all functionality works correctly.
 * 
 * Usage: php test_alarm_manager.php
 */

// Include the AlarmManager class
require_once __DIR__ . '/../htdocs/inc.alarmManager.php';

echo "=== Phoniebox AlarmManager Test Script ===\n";
echo "Testing JSON-based alarm management system...\n\n";

try {
    // Initialize the alarm manager with a test file
    $testFile = __DIR__ . '/../settings/test_alarms.json';
    $alarmManager = new AlarmManager($testFile);
    
    echo "✓ AlarmManager initialized successfully\n";
    
    // Test 1: Create a new alarm
    echo "\n--- Test 1: Creating New Alarm ---\n";
    $alarmData = array(
        'hour' => 7,
        'minute' => 30,
        'ampm' => 'AM',
        'sound' => 'test_sound_001',
        'days' => ['mon', 'wed', 'fri'],
        'volume' => 75,
        'enabled' => true
    );
    
    $alarmId = $alarmManager->saveAlarm($alarmData);
    if ($alarmId !== false) {
        echo "✓ Alarm created successfully with ID: {$alarmId}\n";
    } else {
        echo "✗ Failed to create alarm\n";
        exit(1);
    }
    
    // Test 2: Retrieve all alarms
    echo "\n--- Test 2: Retrieving All Alarms ---\n";
    $alarms = $alarmManager->getAllAlarms();
    if (count($alarms) === 1) {
        echo "✓ Retrieved 1 alarm successfully\n";
        $alarm = $alarms[0];
        echo "  - ID: {$alarm['id']}, Time: {$alarm['hour']}:{$alarm['minute']} {$alarm['ampm']}\n";
        echo "  - Days: " . implode(', ', $alarm['days']) . "\n";
        echo "  - Volume: {$alarm['volume']}%, Enabled: " . ($alarm['enabled'] ? 'Yes' : 'No') . "\n";
    } else {
        echo "✗ Expected 1 alarm, got " . count($alarms) . "\n";
        exit(1);
    }
    
    // Test 3: Update an alarm
    echo "\n--- Test 3: Updating Alarm ---\n";
    $updateData = array(
        'hour' => 8,
        'minute' => 0,
        'ampm' => 'AM',
        'sound' => 'test_sound_002',
        'days' => ['tue', 'thu'],
        'volume' => 85,
        'enabled' => false
    );
    
    $updateResult = $alarmManager->updateAlarm($alarmId, $updateData);
    if ($updateResult) {
        echo "✓ Alarm updated successfully\n";
    } else {
        echo "✗ Failed to update alarm\n";
        exit(1);
    }
    
    // Verify the update
    $updatedAlarms = $alarmManager->getAllAlarms();
    $updatedAlarm = $updatedAlarms[0];
    if ($updatedAlarm['hour'] === 8 && $updatedAlarm['enabled'] === false) {
        echo "✓ Update verified successfully\n";
    } else {
        echo "✗ Update verification failed\n";
        exit(1);
    }
    
    // Test 4: Toggle alarm status
    echo "\n--- Test 4: Toggling Alarm Status ---\n";
    $toggleResult = $alarmManager->toggleAlarm($alarmId, true);
    if ($toggleResult) {
        echo "✓ Alarm enabled successfully\n";
    } else {
        echo "✗ Failed to enable alarm\n";
        exit(1);
    }
    
    // Test 5: Create another alarm
    echo "\n--- Test 5: Creating Second Alarm ---\n";
    $alarmData2 = array(
        'hour' => 9,
        'minute' => 15,
        'ampm' => 'PM',
        'sound' => 'test_sound_003',
        'days' => ['sat', 'sun'],
        'volume' => 60,
        'enabled' => true
    );
    
    $alarmId2 = $alarmManager->saveAlarm($alarmData2);
    if ($alarmId2 !== false) {
        echo "✓ Second alarm created successfully with ID: {$alarmId2}\n";
    } else {
        echo "✗ Failed to create second alarm\n";
        exit(1);
    }
    
    // Test 6: Verify multiple alarms
    echo "\n--- Test 6: Verifying Multiple Alarms ---\n";
    $allAlarms = $alarmManager->getAllAlarms();
    if (count($allAlarms) === 2) {
        echo "✓ Retrieved 2 alarms successfully\n";
        foreach ($allAlarms as $alarm) {
            echo "  - ID: {$alarm['id']}, Time: {$alarm['hour']}:{$alarm['minute']} {$alarm['ampm']}\n";
        }
    } else {
        echo "✗ Expected 2 alarms, got " . count($allAlarms) . "\n";
        exit(1);
    }
    
    // Test 7: Delete an alarm
    echo "\n--- Test 7: Deleting Alarm ---\n";
    $deleteResult = $alarmManager->deleteAlarm($alarmId);
    if ($deleteResult) {
        echo "✓ Alarm deleted successfully\n";
    } else {
        echo "✗ Failed to delete alarm\n";
        exit(1);
    }
    
    // Verify deletion
    $remainingAlarms = $alarmManager->getAllAlarms();
    if (count($remainingAlarms) === 1 && $remainingAlarms[0]['id'] == $alarmId2) {
        echo "✓ Deletion verified successfully\n";
    } else {
        echo "✗ Deletion verification failed\n";
        exit(1);
    }
    
    // Test 8: Check JSON file structure
    echo "\n--- Test 8: Verifying JSON File Structure ---\n";
    if (file_exists($testFile)) {
        $jsonContent = file_get_contents($testFile);
        $jsonData = json_decode($jsonContent, true);
        
        if ($jsonData !== null && isset($jsonData['version']) && isset($jsonData['alarms'])) {
            echo "✓ JSON file structure is valid\n";
            echo "  - Version: {$jsonData['version']}\n";
            echo "  - Alarms count: " . count($jsonData['alarms']) . "\n";
        } else {
            echo "✗ JSON file structure is invalid\n";
            exit(1);
        }
    } else {
        echo "✗ Test JSON file not found\n";
        exit(1);
    }
    
    // Cleanup test file
    echo "\n--- Cleanup ---\n";
    if (unlink($testFile)) {
        echo "✓ Test file cleaned up successfully\n";
    } else {
        echo "⚠ Warning: Could not remove test file: {$testFile}\n";
    }
    
    echo "\n=== All Tests Passed Successfully! ===\n";
    echo "The JSON-based AlarmManager is working correctly.\n";
    echo "All alarm functionality has been verified.\n";
    
} catch (Exception $e) {
    echo "✗ Test failed with error: " . $e->getMessage() . "\n";
    exit(1);
}
?> 