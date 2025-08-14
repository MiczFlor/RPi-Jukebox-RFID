# Phoniebox Alarms Feature

This document describes the new Alarms functionality added to the Phoniebox RFID Jukebox system.

## Overview

The Alarms feature allows users to set up recurring alarms that will play audio files at specified times. Users can configure:
- Alarm time (hour, minute, AM/PM)
- Recurrence pattern (which days of the week)
- Audio source (via RFID card scanning)

## Features

### 1. Alarm Configuration
- **Time Selection**: Choose hour (1-12), minute (00-59), and AM/PM
- **Recurrence**: Select which days of the week the alarm should trigger
- **Audio Source**: Scan an RFID card to automatically set the alarm sound

### 2. Day Selection Interface
- Seven circular buttons representing days of the week (Mon, Tue, Wed, Thu, Fri, Sat, Sun)
- Visual feedback: buttons toggle between filled (active) and unfilled (inactive) states
- At least one day must be selected for the alarm to be valid

### 3. RFID Integration
- Automatic detection of scanned RFID cards
- Real-time updates when cards are scanned
- Uses the same mechanism as the existing card registration system

### 4. Management Interface
- View all configured alarms
- Enable/disable individual alarms
- Delete alarms
- Add new alarms

## Installation

The alarms feature is integrated into the existing Phoniebox system and requires no additional installation steps beyond the standard Phoniebox setup.

## Usage

### Setting Up an Alarm

1. Navigate to **Settings** → **Alarms** section
2. Set the desired alarm time using the hour, minute, and AM/PM dropdowns
3. Select which days of the week the alarm should recur by clicking the day buttons
4. Scan an RFID card to set the alarm sound (the card should be linked to an audio folder)
5. Click "Add New Alarm" to save the configuration

### Managing Alarms

1. Click "Manage Alarms" to access the full alarm management interface
2. View all configured alarms in a table format
3. Enable/disable alarms using the toggle buttons
4. Delete alarms using the delete button
5. Add new alarms using the form at the bottom

### Day Selection

- Click on day buttons to toggle them on/off
- Active days are highlighted in blue
- Inactive days remain in the default gray state
- At least one day must be selected for the alarm to be valid

## Technical Details

### Files Added/Modified

#### New Files
- `htdocs/alarm_management.php` - Main alarm management interface
- `htdocs/ajax.refresh_alarm_sound.php` - AJAX handler for RFID card scanning

#### Modified Files
- `htdocs/settings.php` - Added alarms section to settings page
- `htdocs/func.php` - Added CSS styling for alarm interface
- `htdocs/lang/lang-*.php` - Added multilingual support for all supported languages

### Language Support

The alarms feature supports all four languages included with Phoniebox:
- English (UK)
- German (DE)
- French (FR)
- Dutch (NL)

### CSS Styling

The day selection buttons are styled as circular buttons with:
- 40px × 40px dimensions
- Rounded borders
- Visual feedback for active/inactive states
- Hover effects

### JavaScript Functionality

- Real-time RFID card detection
- Day button toggle handling
- Form validation
- AJAX updates for dynamic content

## Configuration

### Alarm Storage

Currently, the alarms are stored in memory as sample data. In a production implementation, you would want to:

1. Create a database table for alarms
2. Implement persistent storage (JSON file, SQLite, MySQL, etc.)
3. Add cron jobs or systemd timers to trigger alarms
4. Implement the actual alarm playback functionality

### RFID Card Requirements

For alarms to work properly:
1. RFID cards must be registered in the system
2. Cards must be linked to audio folders or playlists
3. The audio content should be appropriate for alarm sounds

## Future Enhancements

Potential improvements for the alarms system:

1. **Alarm Volume Control**: Separate volume setting for alarms
2. **Snooze Functionality**: Allow users to snooze alarms
3. **Multiple Audio Sources**: Support for different sounds on different days
4. **Alarm Categories**: Work alarms, weekend alarms, etc.
5. **Mobile App Integration**: Control alarms from mobile devices
6. **Weather Integration**: Adjust alarm times based on weather conditions
7. **Calendar Integration**: Sync with external calendar systems

## Troubleshooting

### Common Issues

1. **RFID Card Not Detected**
   - Ensure the RFID reader is properly connected and working
   - Check that the card is registered in the system
   - Verify the card has audio content linked to it

2. **Day Buttons Not Working**
   - Check that JavaScript is enabled in the browser
   - Verify that jQuery and Bootstrap are loading properly
   - Check browser console for JavaScript errors

3. **Alarms Not Saving**
   - Ensure the form validation passes (at least one day selected)
   - Check that all required fields are filled
   - Verify the form submission is working

### Debug Information

Enable debug logging in the Phoniebox settings to get more detailed information about system operations.

## Support

For issues related to the alarms feature:
1. Check the Phoniebox main documentation
2. Review the browser console for JavaScript errors
3. Check the Phoniebox logs for PHP errors
4. Ensure all required dependencies are properly installed

## License

This feature follows the same license as the main Phoniebox project. 