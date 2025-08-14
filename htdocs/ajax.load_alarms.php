<?php
include("config.php");

// Sample alarms data (in a real implementation, this would come from a database or file)
$sample_alarms = array(
    array(
        'id' => 1,
        'hour' => 7,
        'minute' => 0,
        'ampm' => 'AM',
        'sound' => '1234567890',
        'days' => array('mon', 'tue', 'wed', 'thu', 'fri'),
        'enabled' => true
    ),
    array(
        'id' => 2,
        'hour' => 8,
        'minute' => 30,
        'ampm' => 'AM',
        'sound' => '0987654321',
        'days' => array('sat', 'sun'),
        'enabled' => false
    )
);

if (empty($sample_alarms)) {
    print "<p class='text-muted'>No alarms configured yet.</p>";
} else {
    print "<div class='table-responsive'>";
    print "<table class='table table-striped alarm-table'>";
    print "<thead>";
    print "<tr>";
    print "<th>Time</th>";
    print "<th>Sound</th>";
    print "<th>Days</th>";
    print "<th>Status</th>";
    print "<th>Actions</th>";
    print "</tr>";
    print "</thead>";
    print "<tbody>";
    
    foreach ($sample_alarms as $alarm) {
        print "<tr>";
        
        // Time column
        print "<td class='alarm-time-cell'>";
        print "<strong>" . $alarm['hour'] . ":" . str_pad($alarm['minute'], 2, '0', STR_PAD_LEFT) . " " . $alarm['ampm'] . "</strong>";
        print "</td>";
        
        // Sound column
        print "<td class='alarm-sound-cell'>";
        print "<code>" . $alarm['sound'] . "</code>";
        print "</td>";
        
        // Days column
        print "<td class='alarm-days-cell'>";
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
        print "</td>";
        
        // Status column
        print "<td class='alarm-status-cell'>";
        $status_class = $alarm['enabled'] ? 'success' : 'default';
        $status_text = $alarm['enabled'] ? 'Enabled' : 'Disabled';
        print "<span class='label label-" . $status_class . "'>" . $status_text . "</span>";
        print "</td>";
        
        // Actions column
        print "<td class='alarm-actions'>";
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
        print "</td>";
        
        print "</tr>";
    }
    
    print "</tbody>";
    print "</table>";
    print "</div>";
}
?> 