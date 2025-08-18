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

// Validate required fields
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
    'enabled' => true // New alarms are enabled by default
);

// Validate hour range
if ($alarmData['hour'] < 1 || $alarmData['hour'] > 12) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Invalid hour value']);
    exit;
}

// Validate minute range
if ($alarmData['minute'] < 0 || $alarmData['minute'] > 59) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Invalid minute value']);
    exit;
}

// Validate AM/PM
if (!in_array($alarmData['ampm'], ['AM', 'PM'])) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Invalid AM/PM value']);
    exit;
}

// Validate volume range
if ($alarmData['volume'] < 1 || $alarmData['volume'] > 100) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Invalid volume value']);
    exit;
}

// Validate days
$validDays = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];
foreach ($alarmData['days'] as $day) {
    if (!in_array($day, $validDays)) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Invalid day value: ' . $day]);
        exit;
    }
}

try {
    // Save the alarm
    $result = $alarmManager->saveAlarm($alarmData);
    
    if ($result !== false) {
        echo json_encode([
            'success' => true, 
            'message' => 'Alarm saved successfully',
            'alarm_id' => $result
        ]);
    } else {
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => 'Failed to save alarm']);
    }
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Error saving alarm: ' . $e->getMessage()]);
}
?> 