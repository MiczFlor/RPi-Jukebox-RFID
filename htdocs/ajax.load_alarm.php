<?php
include("config.php");
include("inc.alarmManager.php");

// Initialize the alarm manager
$alarmManager = new AlarmManager();

// Set response header
header('Content-Type: application/json');

// Check if this is a GET request
if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Method not allowed']);
    exit;
}

// Check if alarm ID is provided
if (empty($_GET['alarm_id'])) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Missing alarm ID']);
    exit;
}

$alarmId = $_GET['alarm_id'];

try {
    // Get all alarms and find the one with matching ID
    $alarms = $alarmManager->getAllAlarms();
    $targetAlarm = null;
    
    foreach ($alarms as $alarm) {
        if ($alarm['id'] == $alarmId) {
            $targetAlarm = $alarm;
            break;
        }
    }
    
    if ($targetAlarm === null) {
        http_response_code(404);
        echo json_encode(['success' => false, 'message' => 'Alarm not found']);
        exit;
    }
    
    echo json_encode([
        'success' => true,
        'alarm' => $targetAlarm
    ]);
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Error loading alarm: ' . $e->getMessage()]);
}
?> 