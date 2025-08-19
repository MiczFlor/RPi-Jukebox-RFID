# Phoniebox Alarms Migration Guide

This guide explains how to migrate your existing Phoniebox alarms from the old `.conf` file format to the new single `alarms.json` format.

## What Changed?

The alarms system has been updated to use a single JSON file (`alarms.json`) instead of individual configuration files (`alarm_001.conf`, `alarm_002.conf`, etc.). This provides:

- **Better Performance**: Single file operations instead of multiple file operations
- **Easier Backup**: One file to backup instead of many
- **Better Reliability**: Reduced risk of file corruption
- **Easier Management**: All alarms in one structured format

## Migration Process

### Automatic Migration (Recommended)

The system automatically migrates existing alarms when you first use the new system:

1. **No Action Required**: Simply use the alarms system as normal
2. **Automatic Detection**: The system detects existing `.conf` files
3. **Safe Conversion**: Converts all alarms to the new JSON format
4. **Automatic Backup**: Creates a backup of all old files
5. **Cleanup**: Removes old files after successful migration

### Manual Migration

If you prefer to manually control the migration process:

```bash
# Navigate to the scripts directory
cd /path/to/phoniebox/scripts

# Run the migration script
php migrate_alarms_to_json.php
```

## What Gets Migrated

The migration process converts all alarm properties:

| Old .conf Format | New JSON Format | Notes |
|------------------|-----------------|-------|
| `id=001` | `"id": 1` | Converted to integer |
| `hour=7` | `"hour": 7` | Converted to integer |
| `minute=30` | `"minute": 30` | Converted to integer |
| `ampm=AM` | `"ampm": "AM"` | Preserved as string |
| `sound=1234567890` | `"sound": "1234567890"` | Preserved as string |
| `days=mon,tue,wed` | `"days": ["mon", "tue", "wed"]` | Converted to array |
| `volume=80` | `"volume": 80` | Converted to integer |
| `enabled=true` | `"enabled": true` | Converted to boolean |

## Backup and Safety

### Automatic Backup

During migration, the system automatically creates a backup:

- **Location**: `/settings/alarms_backup_YYYY-MM-DD_HH-MM-SS/`
- **Contents**: All original `.conf` files
- **Timestamp**: Unique timestamp for each migration run
- **Safety**: Original files are never deleted without backup

### Manual Backup (Optional)

If you want to create a manual backup before migration:

```bash
# Create a manual backup
cp -r /settings/alarms /settings/alarms_manual_backup

# Or create a timestamped backup
cp -r /settings/alarms /settings/alarms_manual_backup_$(date +%Y-%m-%d_%H-%M-%S)
```

## Migration Verification

After migration, verify that everything worked correctly:

### 1. Check the New JSON File

```bash
# View the new alarms.json file
cat /settings/alarms.json

# Validate JSON format
python -m json.tool /settings/alarms.json
```

### 2. Verify Alarm Count

Compare the number of alarms in the new system with your original count:

```bash
# Count original .conf files (if backup still exists)
ls /settings/alarms_backup_*/alarm_*.conf | wc -l

# Count alarms in new JSON file
grep -c '"id"' /settings/alarms.json
```

### 3. Test Functionality

- Open the Phoniebox web interface
- Navigate to Settings → Alarms
- Verify all your alarms are displayed correctly
- Test creating, editing, and deleting alarms

## Rollback (If Needed)

If you need to rollback to the old system:

### 1. Restore from Backup

```bash
# Find your backup directory
ls -la /settings/alarms_backup_*

# Restore the old files
cp -r /settings/alarms_backup_YYYY-MM-DD_HH-MM-SS/* /settings/alarms/

# Remove the new JSON file
rm /settings/alarms.json
```

### 2. Revert Code Changes

If you need to revert the code changes, restore the original `inc.alarmManager.php` file from your version control system.

## Troubleshooting

### Migration Fails

If the migration script fails:

1. **Check Permissions**: Ensure the web server can read/write to `/settings/`
2. **Check Disk Space**: Ensure there's enough space for the new file
3. **Check File Locks**: Ensure no other processes are using the alarm files
4. **Review Logs**: Check web server error logs for specific error messages

### Alarms Not Displaying

If alarms don't appear after migration:

1. **Check JSON Format**: Validate the `alarms.json` file format
2. **Check File Permissions**: Ensure `alarms.json` is readable by the web server
3. **Check File Path**: Verify the file is in the correct location
4. **Clear Browser Cache**: Refresh the web interface

### Missing Alarms

If some alarms are missing:

1. **Check Backup**: Look in the backup directory for missing alarms
2. **Check File Corruption**: Original `.conf` files might have been corrupted
3. **Manual Recovery**: Manually recreate missing alarms if necessary

## Post-Migration

After successful migration:

### 1. Remove Old Directories (Optional)

Once you're confident everything works:

```bash
# Remove old alarms directory (if empty)
rmdir /settings/alarms

# Remove old backup directories (if no longer needed)
rm -rf /settings/alarms_backup_*
```

### 2. Update Documentation

Update any custom documentation or scripts that reference the old alarm file locations.

### 3. Test All Functionality

- Create new alarms
- Edit existing alarms
- Delete alarms
- Toggle alarm status
- Verify alarm scheduling

## Support

If you encounter issues during migration:

1. **Check this guide** for common solutions
2. **Review the logs** for error messages
3. **Check file permissions** and disk space
4. **Use the test script** to verify functionality: `php test_alarm_manager.php`
5. **Create an issue** in the project repository with detailed error information

## Benefits After Migration

Once migrated, you'll enjoy:

- **Faster Performance**: Single file operations
- **Easier Backup**: One file to backup
- **Better Reliability**: Reduced corruption risk
- **Easier Management**: Structured JSON format
- **Future Compatibility**: Version field for future updates
- **Better Integration**: Easier to sync between devices

## File Locations

| File | Purpose | Location |
|------|---------|----------|
| `alarms.json` | Main alarm storage | `/settings/alarms.json` |
| `alarms.json.sample` | Example format | `/settings/alarms.json.sample` |
| `inc.alarmManager.php` | Core functionality | `/htdocs/inc.alarmManager.php` |
| `migrate_alarms_to_json.php` | Migration script | `/scripts/migrate_alarms_to_json.php` |
| `test_alarm_manager.php` | Test script | `/scripts/test_alarm_manager.php` |

---

**Note**: This migration is designed to be safe and reversible. Your original alarm data will never be lost during the process. 