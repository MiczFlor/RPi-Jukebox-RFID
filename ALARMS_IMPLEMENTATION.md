# Phoniebox Alarms Implementation

This document describes the implementation of the JSON-based alarm storage system for the Phoniebox RFID Jukebox.

## Overview

The alarms system has been implemented using a single JSON configuration file stored as `/settings/alarms.json`, providing a more efficient and maintainable approach compared to the previous individual configuration file system.

## Architecture

### Storage Structure

```
/settings/
├── alarms.json          # Single JSON file containing all alarms
├── alarms.json.sample   # Sample file showing the format
└── alarms/              # Legacy directory (backed up after migration)
    └── alarms_backup_YYYY-MM-DD_HH-MM-SS/  # Backup of old .conf files
```

The `alarms.json` file contains all alarm configurations in a structured JSON format:

```json
{
    "version": "1.0",
    "alarms": [
        {
            "id": 1,
            "hour": 7,
            "minute": 0,
            "ampm": "AM",
            "sound": "1234567890",
            "days": ["mon", "tue", "wed", "thu", "fri"],
            "volume": 80,
            "enabled": true
        }
    ]
}
```

## Components

### 1. AlarmManager Class (`htdocs/inc.alarmManager.php`)

The core class that handles all alarm operations:

- **Constructor**: Initializes the alarms.json file path and creates the file if it doesn't exist
- **getAllAlarms()**: Reads all alarms from the JSON file and returns an array
- **saveAlarm()**: Creates or updates an alarm in the JSON file
- **updateAlarm()**: Updates an existing alarm
- **deleteAlarm()**: Removes an alarm from the JSON file
- **toggleAlarm()**: Enables/disables an alarm
- **migrateFromConfFiles()**: Migrates existing .conf files to JSON format
- **getAlarmsFile()**: Returns the path to the alarms.json file

### 2. Migration Script (`scripts/migrate_alarms_to_json.php`)

A command-line script that converts existing alarm configuration files from the old `.conf` format to the new JSON format:

- Automatically detects existing `.conf` files
- Converts them to the new JSON structure
- Creates a timestamped backup of the old files
- Removes the old files after successful migration
- Provides detailed migration status and summary

### 3. AJAX Handlers

- **`ajax.load_alarms.php`**: Loads and displays all alarms in the UI
- **`ajax.save_alarm.php`**: Handles creating new alarms
- **`ajax.update_alarm.php`**: Handles updating existing alarms and toggling status
- **`ajax.delete_alarm.php`**: Handles deleting alarms
- **`ajax.load_alarm.php`**: Loads individual alarm data for editing

### 4. Frontend Integration

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
4. `AlarmManager::saveAlarm()` adds alarm to JSON file
5. Success response returned to frontend
6. UI refreshes to show new alarm

### Updating an Alarm

1. User clicks edit button on existing alarm
2. `ajax.load_alarm.php` loads alarm data
3. Form populated with existing values
4. User modifies values and submits
5. `ajax.update_alarm.php` updates JSON file
6. UI refreshes to show updated alarm

### Deleting an Alarm

1. User clicks delete button on existing alarm
2. Confirmation dialog shown
3. `ajax.delete_alarm.php` removes alarm from JSON file
4. UI refreshes to remove deleted alarm

## Migration from .conf Files

### Automatic Migration

The system automatically migrates existing `.conf` files when the `migrateFromConfFiles()` method is called:

1. **Detection**: Scans for existing `.conf` files in `/settings/alarms/`
2. **Conversion**: Parses each `.conf` file and converts to JSON structure
3. **Backup**: Creates timestamped backup directory with all old files
4. **Cleanup**: Removes old `.conf` files and empty directories
5. **Verification**: Confirms successful migration

### Manual Migration

To manually migrate existing alarms:

```bash
cd /path/to/phoniebox/scripts
php migrate_alarms_to_json.php
```

### Migration Safety

- All existing `.conf` files are automatically backed up before removal
- Backup directories are timestamped for easy identification
- Migration can be run multiple times safely
- Original data is never lost during the process

## Benefits of JSON Approach

1. **Efficiency**: Single file read/write operations instead of multiple file operations
2. **Performance**: Faster loading and saving of alarm data
3. **Atomicity**: All alarms are updated together, reducing corruption risk
4. **Maintainability**: Easier to backup, restore, and synchronize
5. **Human Readable**: JSON format is easy to read and edit manually
6. **Versioning**: Built-in version field for future compatibility
7. **Consistency**: All alarm data in one structured format
8. **Backup Friendly**: Single file makes backup operations simpler

## File Permissions

The alarms.json file should have appropriate permissions:

```bash
chmod 644 /settings/alarms.json
chown www-data:www-data /settings/alarms.json  # Adjust user/group as needed
```

## Backup and Sync

Alarm configurations can be backed up by copying the single `alarms.json` file. The existing sync-shared component can be easily extended to include alarm synchronization between multiple Phoniebox installations.

## Future Enhancements

1. **Alarm Scheduling**: Integration with cron or systemd timers
2. **Audio Playback**: Actual alarm sound triggering functionality
3. **Snooze Functionality**: Allow users to snooze alarms
4. **Alarm Categories**: Work alarms, weekend alarms, etc.
5. **Mobile Integration**: Control alarms from mobile devices
6. **Weather Integration**: Adjust alarm times based on weather conditions
7. **JSON Schema Validation**: Validate alarm data structure
8. **Compression**: Optional compression for large alarm collections

## Troubleshooting

### Common Issues

1. **Alarms Not Saving**: Check file permissions on `alarms.json`
2. **Alarms Not Loading**: Verify JSON file is valid format
3. **Permission Errors**: Ensure web server has read/write access to alarms.json
4. **Migration Failures**: Check backup directories for original .conf files

### Debug Mode

Enable debug logging in the Phoniebox settings to see detailed error messages.

### JSON Validation

Use online JSON validators or command-line tools to verify `alarms.json` format:

```bash
python -m json.tool /settings/alarms.json
```

## Testing

The system includes comprehensive error handling and validation:

- Input validation for all alarm parameters
- JSON file operation error handling
- Migration safety with automatic backups
- JSON response formatting for AJAX requests
- User-friendly error messages

## Security Considerations

- Input validation prevents malicious data injection
- File operations are restricted to the alarms.json file
- No direct file path manipulation allowed
- Proper HTTP status codes returned for different error conditions
- JSON structure validation prevents malformed data

## Performance Considerations

- Single file operations reduce I/O overhead
- JSON parsing is efficient for typical alarm counts
- File locking mechanisms prevent concurrent write conflicts
- Automatic file creation and initialization 