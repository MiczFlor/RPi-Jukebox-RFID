<?php
/**
 * Alarm Manager Class
 * Handles reading, writing, and managing alarm configuration files
 */

class AlarmManager {
    private $alarmsDir;
    
    public function __construct($alarmsDir = null) {
        if ($alarmsDir === null) {
            $this->alarmsDir = realpath(getcwd().'/../settings/alarms');
        } else {
            $this->alarmsDir = $alarmsDir;
        }
        
        // Create alarms directory if it doesn't exist
        if (!is_dir($this->alarmsDir)) {
            mkdir($this->alarmsDir, 0755, true);
        }
    }
    
    /**
     * Get all alarms from configuration files
     * @return array Array of alarm configurations
     */
    public function getAllAlarms() {
        $alarms = array();
        
        if (!is_dir($this->alarmsDir)) {
            return $alarms;
        }
        
        $files = glob($this->alarmsDir . '/*.conf');
        
        foreach ($files as $file) {
            $alarm = $this->readAlarmFile($file);
            if ($alarm !== false) {
                $alarms[] = $alarm;
            }
        }
        
        // Sort alarms by ID
        usort($alarms, function($a, $b) {
            return intval($a['id']) - intval($b['id']);
        });
        
        return $alarms;
    }
    
    /**
     * Read a single alarm configuration file
     * @param string $filePath Path to the alarm configuration file
     * @return array|false Alarm configuration array or false on failure
     */
    private function readAlarmFile($filePath) {
        if (!file_exists($filePath)) {
            return false;
        }
        
        $content = file_get_contents($filePath);
        if ($content === false) {
            return false;
        }
        
        // Parse INI content
        $config = parse_ini_string($content);
        if ($config === false) {
            return false;
        }
        
        // Convert days string to array
        if (isset($config['days'])) {
            $config['days'] = explode(',', $config['days']);
        }
        
        // Ensure boolean values are properly converted
        if (isset($config['enabled'])) {
            $config['enabled'] = ($config['enabled'] === 'true' || $config['enabled'] === '1');
        }
        
        // Ensure numeric values are properly converted
        if (isset($config['hour'])) {
            $config['hour'] = intval($config['hour']);
        }
        if (isset($config['minute'])) {
            $config['minute'] = intval($config['minute']);
        }
        if (isset($config['volume'])) {
            $config['volume'] = intval($config['volume']);
        }
        
        return $config;
    }
    
    /**
     * Save an alarm configuration to file
     * @param array $alarmData Alarm configuration data
     * @return bool|int True on success, false on failure, or the generated ID if successful
     */
    public function saveAlarm($alarmData) {
        // Generate new ID if not provided
        if (empty($alarmData['id'])) {
            $alarmData['id'] = $this->getNextAlarmId();
        }
        
        $filename = 'alarm_' . str_pad($alarmData['id'], 3, '0', STR_PAD_LEFT) . '.conf';
        $filePath = $this->alarmsDir . '/' . $filename;
        
        // Prepare content for writing
        $content = $this->formatAlarmContent($alarmData);
        
        $result = file_put_contents($filePath, $content) !== false;
        
        // Return the generated ID if successful
        if ($result) {
            return $alarmData['id'];
        }
        
        return false;
    }
    
    /**
     * Update an existing alarm
     * @param string $alarmId Alarm ID to update
     * @param array $alarmData New alarm data
     * @return bool True on success, false on failure
     */
    public function updateAlarm($alarmId, $alarmData) {
        $alarmData['id'] = $alarmId;
        return $this->saveAlarm($alarmData);
    }
    
    /**
     * Delete an alarm
     * @param string $alarmId Alarm ID to delete
     * @return bool True on success, false on failure
     */
    public function deleteAlarm($alarmId) {
        $filename = 'alarm_' . str_pad($alarmId, 3, '0', STR_PAD_LEFT) . '.conf';
        $filePath = $this->alarmsDir . '/' . $filename;
        
        if (file_exists($filePath)) {
            return unlink($filePath);
        }
        
        return false;
    }
    
    /**
     * Toggle alarm enabled/disabled status
     * @param string $alarmId Alarm ID to toggle
     * @param bool $enabled New enabled status
     * @return bool True on success, false on failure
     */
    public function toggleAlarm($alarmId, $enabled) {
        $alarms = $this->getAllAlarms();
        
        foreach ($alarms as $alarm) {
            if ($alarm['id'] == $alarmId) {
                $alarm['enabled'] = $enabled;
                return $this->updateAlarm($alarmId, $alarm);
            }
        }
        
        return false;
    }
    
    /**
     * Get the next available alarm ID
     * @return int Next available alarm ID
     */
    private function getNextAlarmId() {
        $alarms = $this->getAllAlarms();
        
        if (empty($alarms)) {
            return 1;
        }
        
        $maxId = 0;
        foreach ($alarms as $alarm) {
            $id = intval($alarm['id']);
            if ($id > $maxId) {
                $maxId = $id;
            }
        }
        
        return $maxId + 1;
    }
    
    /**
     * Format alarm data for writing to file
     * @param array $alarmData Alarm configuration data
     * @return string Formatted content for the configuration file
     */
    private function formatAlarmContent($alarmData) {
        $content = "# Alarm Configuration\n";
        $content .= "id=" . $alarmData['id'] . "\n";
        $content .= "hour=" . $alarmData['hour'] . "\n";
        $content .= "minute=" . $alarmData['minute'] . "\n";
        $content .= "ampm=" . $alarmData['ampm'] . "\n";
        $content .= "sound=" . $alarmData['sound'] . "\n";
        
        // Convert days array to comma-separated string
        if (is_array($alarmData['days'])) {
            $content .= "days=" . implode(',', $alarmData['days']) . "\n";
        } else {
            $content .= "days=" . $alarmData['days'] . "\n";
        }
        
        $content .= "volume=" . $alarmData['volume'] . "\n";
        $content .= "enabled=" . ($alarmData['enabled'] ? 'true' : 'false') . "\n";
        
        return $content;
    }
}
?> 