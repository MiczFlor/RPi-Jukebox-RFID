<?php
include("config.php");
include("inc.alarmManager.php");

// Initialize the alarm manager
$alarmManager = new AlarmManager();

// Set response header
header('Content-Type: application/json');

// Check if this is a POST request
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Method not allowed']);
    exit;
}

// Get POST data
$postData = $_POST;

// Check if alarm ID is provided
if (empty($postData['alarm_id'])) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Missing alarm ID']);
    exit;
}

$alarmId = $postData['alarm_id'];

// Check if this is a toggle operation
if (isset($postData['enabled'])) {
    $enabled = ($postData['enabled'] === '1' || $postData['enabled'] === 'true');
    
    try {
        $success = $alarmManager->toggleAlarm($alarmId, $enabled);
        
        if ($success) {
            echo json_encode([
                'success' => true, 
                'message' => 'Alarm ' . ($enabled ? 'enabled' : 'disabled') . ' successfully'
            ]);
        } else {
            http_response_code(500);
            echo json_encode(['success' => false, 'message' => 'Failed to update alarm']);
        }
    } catch (Exception $e) {
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => 'Error updating alarm: ' . $e->getMessage()]);
    }
    exit;
}

// For other update operations, validate required fields
$requiredFields = ['alarm-hour', 'alarm-minute', 'alarm-ampm', 'alarm-sound', 'alarm-volume'];
foreach ($requiredFields as $field) {
    if (empty($postData[$field])) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Missing required field: ' . $field]);
        exit;
    }
}

// Validate days selection
if (empty($postData['days']) || !is_array($postData['days'])) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Please select at least one day']);
    exit;
}

// Prepare alarm data
$alarmData = array(
    'hour' => intval($postData['alarm-hour']),
    'minute' => intval($postData['alarm-minute']),
    'ampm' => $postData['alarm-ampm'],
    'sound' => $postData['alarm-sound'],
    'days' => $postData['days'],
    'volume' => intval($postData['alarm-volume']),
    'enabled' => isset($postData['enabled']) ? ($postData['enabled'] === '1' || $postData['enabled'] === 'true') : true
);

// Validate data (same validation as save_alarm.php)
$validDays = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];
foreach ($alarmData['days'] as $day) {
    if (!in_array($day, $validDays)) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Invalid day value: ' . $day]);
        exit;
    }
}

try {
    // Update the alarm
    $success = $alarmManager->updateAlarm($alarmId, $alarmData);
    
    if ($success) {
        echo json_encode([
            'success' => true, 
            'message' => 'Alarm updated successfully'
        ]);
    } else {
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => 'Failed to update alarm']);
    }
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Error updating alarm: ' . $e->getMessage()]);
}
?> 