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

try {
    // Delete the alarm
    $success = $alarmManager->deleteAlarm($alarmId);
    
    if ($success) {
        echo json_encode([
            'success' => true, 
            'message' => 'Alarm deleted successfully'
        ]);
    } else {
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => 'Failed to delete alarm']);
    }
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Error deleting alarm: ' . $e->getMessage()]);
}
?> 