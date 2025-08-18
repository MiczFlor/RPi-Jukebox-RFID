# Phoniebox Alarms Implementation

This document describes the implementation of the file-based alarm storage system for the Phoniebox RFID Jukebox.

## Overview

The alarms system has been implemented using individual configuration files stored in the `/settings/alarms/` directory, following the same architectural pattern used by the rest of the Phoniebox system for storing RFID card mappings and system configurations.

## Architecture

### Storage Structure

```
/settings/alarms/
├── alarm_001.conf
├── alarm_002.conf
├── alarm_003.conf
└── ...
```

Each alarm file contains INI-style configuration with the following structure:

```ini
# Alarm Configuration
id=001
hour=7
minute=0
ampm=AM
sound=1234567890
days=mon,tue,wed,thu,fri
volume=80
enabled=true
```

### File Naming Convention

- Files are named `alarm_XXX.conf` where XXX is a zero-padded 3-digit ID
- Example: `alarm_001.conf`, `alarm_015.conf`, `alarm_123.conf`

## Components

### 1. AlarmManager Class (`htdocs/inc.alarmManager.php`)

The core class that handles all alarm operations:

- **Constructor**: Initializes the alarms directory path
- **getAllAlarms()**: Reads all alarm configuration files and returns an array
- **saveAlarm()**: Creates or updates an alarm configuration file
- **updateAlarm()**: Updates an existing alarm
- **deleteAlarm()**: Removes an alarm configuration file
- **toggleAlarm()**: Enables/disables an alarm

### 2. AJAX Handlers

- **`ajax.load_alarms.php`**: Loads and displays all alarms in the UI
- **`ajax.save_alarm.php`**: Handles creating new alarms
- **`ajax.update_alarm.php`**: Handles updating existing alarms and toggling status
- **`ajax.delete_alarm.php`**: Handles deleting alarms
- **`ajax.load_alarm.php`**: Loads individual alarm data for editing

### 3. Frontend Integration

The alarms system is integrated into the existing Phoniebox web interface:

- **Settings Page**: Alarms section with add/edit/delete functionality
- **Dynamic Loading**: Alarms are loaded via AJAX and displayed in real-time
- **Form Validation**: Client-side validation for required fields
- **Real-time Updates**: UI updates automatically after operations

## Data Flow

### Creating an Alarm

1. User fills out alarm form in the web interface
2. JavaScript validates form data
3. AJAX request sent to `ajax.save_alarm.php`
4. `AlarmManager::saveAlarm()` creates configuration file
5. Success response returned to frontend
6. UI refreshes to show new alarm

### Updating an Alarm

1. User clicks edit button on existing alarm
2. `ajax.load_alarm.php` loads alarm data
3. Form populated with existing values
4. User modifies values and submits
5. `ajax.update_alarm.php` updates configuration file
6. UI refreshes to show updated alarm

### Deleting an Alarm

1. User clicks delete button on existing alarm
2. Confirmation dialog shown
3. `ajax.delete_alarm.php` removes configuration file
4. UI refreshes to remove deleted alarm

## Benefits of This Approach

1. **Consistency**: Follows the same file-based pattern used throughout Phoniebox
2. **Simplicity**: No database setup required, easy to backup/restore
3. **Reliability**: File system operations are robust and well-tested
4. **Portability**: Easy to move alarms between different Phoniebox installations
5. **Human Readable**: Configuration files can be manually edited if needed
6. **Integration**: Works seamlessly with existing sync-shared functionality

## File Permissions

The alarms directory and files should have appropriate permissions:

```bash
chmod 755 /settings/alarms/
chmod 644 /settings/alarms/*.conf
```

## Backup and Sync

Alarm configurations can be backed up by copying the `/settings/alarms/` directory. The existing sync-shared component can be extended to include alarm synchronization between multiple Phoniebox installations.

## Future Enhancements

1. **Alarm Scheduling**: Integration with cron or systemd timers
2. **Audio Playback**: Actual alarm sound triggering functionality
3. **Snooze Functionality**: Allow users to snooze alarms
4. **Alarm Categories**: Work alarms, weekend alarms, etc.
5. **Mobile Integration**: Control alarms from mobile devices
6. **Weather Integration**: Adjust alarm times based on weather conditions

## Troubleshooting

### Common Issues

1. **Alarms Not Saving**: Check file permissions on `/settings/alarms/` directory
2. **Alarms Not Loading**: Verify configuration files are valid INI format
3. **Permission Errors**: Ensure web server has read/write access to alarms directory

### Debug Mode

Enable debug logging in the Phoniebox settings to see detailed error messages.

## Testing

The system includes comprehensive error handling and validation:

- Input validation for all alarm parameters
- File operation error handling
- JSON response formatting for AJAX requests
- User-friendly error messages

## Security Considerations

- Input validation prevents malicious data injection
- File operations are restricted to the alarms directory
- No direct file path manipulation allowed
- Proper HTTP status codes returned for different error conditions 