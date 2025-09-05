<?php
include("config.php");
include("inc.alarmManager.php");

// Initialize the alarm manager
$alarmManager = new AlarmManager();

// Get all alarms from configuration files
$alarms = $alarmManager->getAllAlarms();

if (empty($alarms)) {
    print "<p class='text-muted'>No alarms configured yet.</p>";
} else {
    print "<div class='table-responsive'>";
    print "<table class='table table-striped alarm-table'>";
    print "<thead>";
    print "<tr>";
    print "<th>Time</th>";
    print "<th>Sound</th>";
    print "<th>Days</th>";
    print "<th>Volume</th>";
    print "<th>Status</th>";
    print "<th>Actions</th>";
    print "</tr>";
    print "</thead>";
    print "<tbody>";
    
    foreach ($alarms as $alarm) {
        print "<tr data-alarm-id='" . $alarm['id'] . "'>";
        
        // Time column
        print "<td class='alarm-time-cell'>";
        print "<div class='alarm-display'>";
        print "<strong>" . $alarm['hour'] . ":" . str_pad($alarm['minute'], 2, '0', STR_PAD_LEFT) . " " . $alarm['ampm'] . "</strong>";
        print "</div>";
        print "<div class='alarm-edit' style='display: none;'>";
        print "<div class='alarm-time-group'>";
        print "<div class='row'>";
        print "<div class='col-xs-4'>";
        print "<select class='form-control input-sm edit-hour' data-original='" . $alarm['hour'] . "'>";
        for($i = 1; $i <= 12; $i++) {
            $selected = ($i == $alarm['hour']) ? ' selected' : '';
            print "<option value='" . $i . "'" . $selected . ">" . $i . "</option>";
        }
        print "</select>";
        print "</div>";
        print "<div class='col-xs-4'>";
        print "<select class='form-control input-sm edit-minute' data-original='" . $alarm['minute'] . "'>";
        for($i = 0; $i <= 59; $i++) {
            $selected = (str_pad($i, 2, '0', STR_PAD_LEFT) == $alarm['minute']) ? ' selected' : '';
            print "<option value='" . str_pad($i, 2, '0', STR_PAD_LEFT) . "'" . $selected . ">" . str_pad($i, 2, '0', STR_PAD_LEFT) . "</option>";
        }
        print "</select>";
        print "</div>";
        print "<div class='col-xs-4'>";
        print "<select class='form-control input-sm edit-ampm' data-original='" . $alarm['ampm'] . "'>";
        $selected_am = ($alarm['ampm'] == 'AM') ? ' selected' : '';
        $selected_pm = ($alarm['ampm'] == 'PM') ? ' selected' : '';
        print "<option value='AM'" . $selected_am . ">AM</option>";
        print "<option value='PM'" . $selected_pm . ">PM</option>";
        print "</select>";
        print "</div>";
        print "</div>";
        print "</div>";
        print "</div>";
        print "</td>";
        
        // Sound column
        print "<td class='alarm-sound-cell'>";
        print "<div class='alarm-display'>";
        print "<code>" . $alarm['sound'] . "</code>";
        print "</div>";
        print "<div class='alarm-edit' style='display: none;'>";
        print "<code>" . $alarm['sound'] . "</code>";
        print "</div>";
        print "</td>";
        
        // Days column
        print "<td class='alarm-days-cell'>";
        print "<div class='alarm-display'>";
        $day_names = array(
            'mon' => 'Mon', 'tue' => 'Tue', 'wed' => 'Wed', 
            'thu' => 'Thu', 'fri' => 'Fri', 'sat' => 'Sat', 'sun' => 'Sun'
        );
        $display_days = array();
        foreach ($alarm['days'] as $day) {
            if (isset($day_names[$day])) {
                $display_days[] = $day_names[$day];
            }
        }
        print implode(', ', $display_days);
        print "</div>";
        print "<div class='alarm-edit' style='display: none;'>";
        print "<div class='alarm-recurrence-group'>";
        $days = array('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun');
        foreach ($days as $day) {
            $checked = in_array($day, $alarm['days']) ? ' checked' : '';
            $active_class = in_array($day, $alarm['days']) ? ' btn-primary active' : ' btn-default';
            print "<label class='btn" . $active_class . " day-btn edit-day-btn' data-day='" . $day . "'>";
            print "<input type='checkbox' class='edit-day-checkbox' value='" . $day . "'" . $checked . " autocomplete='off'> " . $day_names[$day];
            print "</label>";
        }
        print "</div>";
        print "</div>";
        print "</td>";
        
        // Volume column
        print "<td class='alarm-volume-cell'>";
        print "<div class='alarm-display'>";
        print "<span class='volume-display'>" . $alarm['volume'] . "%</span>";
        print "</div>";
        print "<div class='alarm-edit' style='display: none;'>";
        print "<select class='form-control input-sm edit-volume' data-original='" . $alarm['volume'] . "'>";
        for($i = 100; $i >= 5; $i -= 5) {
            $selected = ($i == $alarm['volume']) ? ' selected' : '';
            print "<option value='" . $i . "'" . $selected . ">" . $i . "%</option>";
        }
        print "</select>";
        print "</div>";
        print "</td>";
        
        // Status column - Keep the toggle functionality, don't make it editable inline
        print "<td class='alarm-status-cell'>";
        $status_class = $alarm['enabled'] ? 'success' : 'default';
        $status_text = $alarm['enabled'] ? 'Enabled' : 'Disabled';
        print "<span class='label label-" . $status_class . "'>" . $status_text . "</span>";
        print "</td>";
        
        // Actions column
        print "<td class='alarm-actions'>";
        print "<div class='alarm-display'>";
        print "<button class='btn btn-sm btn-" . ($alarm['enabled'] ? 'warning' : 'success') . " toggle-alarm' data-id='" . $alarm['id'] . "' data-enabled='" . ($alarm['enabled'] ? '1' : '0') . "'>";
        print "<i class='mdi mdi-" . ($alarm['enabled'] ? 'pause' : 'play') . "'></i> ";
        print ($alarm['enabled'] ? 'Disable' : 'Enable');
        print "</button> ";
        print "<button class='icon-btn edit edit-alarm' data-id='" . $alarm['id'] . "' title='Edit Alarm'>";
        print "<i class='mdi mdi-pencil'></i>";
        print "</button> ";
        print "<button class='icon-btn delete delete-alarm' data-id='" . $alarm['id'] . "' title='Delete Alarm'>";
        print "<i class='mdi mdi-delete'></i>";
        print "</button>";
        print "</div>";
        print "<div class='alarm-edit' style='display: none;'>";
        print "<button class='btn btn-sm btn-success save-alarm' data-id='" . $alarm['id'] . "' title='Save Changes'>";
        print "<i class='mdi mdi-check'></i> Save";
        print "</button> ";
        print "<button class='btn btn-sm btn-default cancel-edit' data-id='" . $alarm['id'] . "' title='Cancel Edit'>";
        print "<i class='mdi mdi-close'></i> Cancel";
        print "</button>";
        print "</div>";
        print "</td>";
        
        print "</tr>";
    }
    
    print "</tbody>";
    print "</table>";
    print "</div>";
}
?> 