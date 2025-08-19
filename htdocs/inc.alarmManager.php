<?php
/**
 * Alarm Manager Class
 * Handles reading, writing, and managing alarm configuration in a single JSON file
 */

class AlarmManager {
    private $alarmsFile;
    
    public function __construct($alarmsFile = null) {
        if ($alarmsFile === null) {
            $this->alarmsFile = getcwd().'/../settings/alarms.json';
        } else {
            $this->alarmsFile = $alarmsFile;
        }
        
        // Create alarms file if it doesn't exist
        if (!file_exists($this->alarmsFile)) {
            $this->initializeAlarmsFile();
        }
    }
    
    /**
     * Initialize the alarms.json file with empty structure
     */
    private function initializeAlarmsFile() {
        $initialData = array(
            'version' => '1.0',
            'alarms' => array()
        );
        
        $this->writeAlarmsFile($initialData);
    }
    
    /**
     * Read the alarms.json file
     * @return array Array containing alarms data
     */
    private function readAlarmsFile() {
        if (!file_exists($this->alarmsFile)) {
            return array('version' => '1.0', 'alarms' => array());
        }
        
        $content = file_get_contents($this->alarmsFile);
        if ($content === false) {
            return array('version' => '1.0', 'alarms' => array());
        }
        
        $data = json_decode($content, true);
        if ($data === null) {
            // If JSON is invalid, return empty structure
            return array('version' => '1.0', 'alarms' => array());
        }
        
        return $data;
    }
    
    /**
     * Write data to the alarms.json file
     * @param array $data Data to write
     * @return bool True on success, false on failure
     */
    private function writeAlarmsFile($data) {
        // Ensure the directory exists
        $dir = dirname($this->alarmsFile);
        if (!empty($dir) && !is_dir($dir)) {
            mkdir($dir, 0755, true);
        }
        
        // Write with pretty formatting for readability
        $jsonContent = json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
        if ($jsonContent === false) {
            return false;
        }
        
        return file_put_contents($this->alarmsFile, $jsonContent) !== false;
    }
    
    /**
     * Get all alarms from the JSON file
     * @return array Array of alarm configurations
     */
    public function getAllAlarms() {
        $data = $this->readAlarmsFile();
        $alarms = isset($data['alarms']) ? $data['alarms'] : array();
        
        // Sort alarms by ID
        usort($alarms, function($a, $b) {
            return intval($a['id']) - intval($b['id']);
        });
        
        return $alarms;
    }
    
    /**
     * Save an alarm configuration to the JSON file
     * @param array $alarmData Alarm configuration data
     * @return bool|int True on success, false on failure, or the generated ID if successful
     */
    public function saveAlarm($alarmData) {
        $data = $this->readAlarmsFile();
        
        // Generate new ID if not provided
        if (empty($alarmData['id'])) {
            $alarmData['id'] = $this->getNextAlarmId($data['alarms']);
        }
        
        // Check if alarm with this ID already exists
        $existingIndex = -1;
        foreach ($data['alarms'] as $index => $alarm) {
            if ($alarm['id'] == $alarmData['id']) {
                $existingIndex = $index;
                break;
            }
        }
        
        // Update existing or add new
        if ($existingIndex >= 0) {
            $data['alarms'][$existingIndex] = $alarmData;
        } else {
            $data['alarms'][] = $alarmData;
        }
        
        $result = $this->writeAlarmsFile($data);
        
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
        $data = $this->readAlarmsFile();
        
        foreach ($data['alarms'] as $index => $alarm) {
            if ($alarm['id'] == $alarmId) {
                unset($data['alarms'][$index]);
                // Reindex array to remove gaps
                $data['alarms'] = array_values($data['alarms']);
                return $this->writeAlarmsFile($data);
            }
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
        $data = $this->readAlarmsFile();
        
        foreach ($data['alarms'] as $index => $alarm) {
            if ($alarm['id'] == $alarmId) {
                $data['alarms'][$index]['enabled'] = $enabled;
                return $this->writeAlarmsFile($data);
            }
        }
        
        return false;
    }
    
    /**
     * Get the next available alarm ID
     * @param array $alarms Array of existing alarms
     * @return int Next available alarm ID
     */
    private function getNextAlarmId($alarms) {
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
     * Migrate existing .conf files to JSON format
     * This method can be called once to convert existing alarm files
     * @return bool True on success, false on failure
     */
    public function migrateFromConfFiles() {
        $alarmsDir = dirname($this->alarmsFile) . '/alarms';
        
        if (!is_dir($alarmsDir)) {
            return true; // No existing alarms to migrate
        }
        
        $files = glob($alarmsDir . '/*.conf');
        if (empty($files)) {
            return true; // No .conf files to migrate
        }
        
        $migratedAlarms = array();
        
        foreach ($files as $file) {
            $alarm = $this->readConfFile($file);
            if ($alarm !== false) {
                $migratedAlarms[] = $alarm;
            }
        }
        
        if (!empty($migratedAlarms)) {
            $data = array(
                'version' => '1.0',
                'alarms' => $migratedAlarms
            );
            
            $result = $this->writeAlarmsFile($data);
            
            // If migration successful, backup and remove old files
            if ($result) {
                $this->backupAndRemoveConfFiles($alarmsDir);
            }
            
            return $result;
        }
        
        return true;
    }
    
    /**
     * Read a single alarm configuration file (for migration)
     * @param string $filePath Path to the alarm configuration file
     * @return array|false Alarm configuration array or false on failure
     */
    private function readConfFile($filePath) {
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
     * Get the alarms file path (for migration script access)
     * @return string Path to the alarms.json file
     */
    public function getAlarmsFile() {
        return $this->alarmsFile;
    }
    
    /**
     * Backup and remove old .conf files after successful migration
     * @param string $alarmsDir Directory containing old .conf files
     */
    private function backupAndRemoveConfFiles($alarmsDir) {
        $backupDir = $alarmsDir . '_backup_' . date('Y-m-d_H-i-s');
        
        // Create backup directory
        if (!is_dir($backupDir)) {
            mkdir($backupDir, 0755, true);
        }
        
        // Move all .conf files to backup directory
        $files = glob($alarmsDir . '/*.conf');
        foreach ($files as $file) {
            $filename = basename($file);
            rename($file, $backupDir . '/' . $filename);
        }
        
        // Remove empty alarms directory
        if (is_dir($alarmsDir) && count(scandir($alarmsDir)) <= 2) { // Only . and .. remain
            rmdir($alarmsDir);
        }
    }
}
?> 