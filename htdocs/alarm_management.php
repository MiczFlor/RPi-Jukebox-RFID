<?php
include("inc.header.php");

/*******************************************
* START HTML
*******************************************/

html_bootstrap3_createHeader("en","Alarm Management | Phoniebox",$conf['base_url']);

?>
<body>
  <div class="container">

<?php
include("inc.navigation.php");

/*******************************************
* ACTIONS
*******************************************/

// Handle form submissions
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['action'])) {
        switch ($_POST['action']) {
            case 'add':
                // Add new alarm
                $alarm_data = array(
                    'hour' => $_POST['alarm-hour'],
                    'minute' => $_POST['alarm-minute'],
                    'ampm' => $_POST['alarm-ampm'],
                    'sound' => $_POST['alarm-sound'],
                    'days' => isset($_POST['days']) ? $_POST['days'] : array(),
                    'enabled' => true
                );
                
                // Here you would save to a database or file
                // For now, we'll just show a success message
                $messageSuccess = "Alarm added successfully!";
                break;
                
            case 'delete':
                // Delete alarm
                $alarm_id = $_POST['alarm_id'];
                // Here you would delete from database or file
                $messageSuccess = "Alarm deleted successfully!";
                break;
                
            case 'toggle':
                // Toggle alarm enabled/disabled
                $alarm_id = $_POST['alarm_id'];
                $enabled = $_POST['enabled'];
                // Here you would update database or file
                $messageSuccess = "Alarm " . ($enabled ? "enabled" : "disabled") . " successfully!";
                break;
        }
    }
}

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

?>

<div class="row">
  <div class="col-lg-12">
    <h2><i class='mdi mdi-alarm'></i> <?php print $lang['globalAlarms']; ?></h2>
  </div>
</div>

<?php if (isset($messageSuccess)): ?>
<div class="alert alert-success">
  <?php print $messageSuccess; ?>
</div>
<?php endif; ?>

<div class="row">
  <div class="col-lg-12">
    <!-- Existing Alarms -->
    <div class="panel panel-default">
      <div class="panel-heading">
        <h4 class="panel-title">Existing Alarms</h4>
      </div>
      <div class="panel-body">
        <?php if (empty($sample_alarms)): ?>
          <p>No alarms configured yet.</p>
        <?php else: ?>
          <div class="table-responsive">
            <table class="table table-striped">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Sound</th>
                  <th>Days</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <?php foreach ($sample_alarms as $alarm): ?>
                <tr>
                  <td>
                    <?php print $alarm['hour'] . ':' . str_pad($alarm['minute'], 2, '0', STR_PAD_LEFT) . ' ' . $alarm['ampm']; ?>
                  </td>
                  <td>
                    <code><?php print $alarm['sound']; ?></code>
                  </td>
                  <td>
                    <?php 
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
                    ?>
                  </td>
                  <td>
                    <span class="label label-<?php print $alarm['enabled'] ? 'success' : 'default'; ?>">
                      <?php print $alarm['enabled'] ? 'Enabled' : 'Disabled'; ?>
                    </span>
                  </td>
                  <td>
                    <form method="post" style="display: inline;">
                      <input type="hidden" name="action" value="toggle">
                      <input type="hidden" name="alarm_id" value="<?php print $alarm['id']; ?>">
                      <input type="hidden" name="enabled" value="<?php print $alarm['enabled'] ? '0' : '1'; ?>">
                      <button type="submit" class="btn btn-sm btn-<?php print $alarm['enabled'] ? 'warning' : 'success'; ?>">
                        <i class='mdi mdi-<?php print $alarm['enabled'] ? 'pause' : 'play'; ?>'></i>
                        <?php print $alarm['enabled'] ? 'Disable' : 'Enable'; ?>
                      </button>
                    </form>
                    <form method="post" style="display: inline;" onsubmit="return confirm('Are you sure you want to delete this alarm?');">
                      <input type="hidden" name="action" value="delete">
                      <input type="hidden" name="alarm_id" value="<?php print $alarm['id']; ?>">
                      <button type="submit" class="btn btn-sm btn-danger">
                        <i class='mdi mdi-delete'></i> Delete
                      </button>
                    </form>
                  </td>
                </tr>
                <?php endforeach; ?>
              </tbody>
            </table>
          </div>
        <?php endif; ?>
      </div>
    </div>
    
    <!-- Add New Alarm Form -->
    <div class="panel panel-default">
      <div class="panel-heading">
        <h4 class="panel-title"><?php print $lang['globalAddAlarm']; ?></h4>
      </div>
      <div class="panel-body">
        <form method="post">
          <input type="hidden" name="action" value="add">
          
          <div class="row">
            <div class="col-md-6">
              <div class="form-group">
                <label for="alarm-hour"><?php print $lang['globalAlarmTime']; ?></label>
                <div class="row">
                  <div class="col-xs-4">
                    <select id="alarm-hour" name="alarm-hour" class="form-control" required>
                      <?php for($i = 1; $i <= 12; $i++): ?>
                        <option value="<?php print $i; ?>"><?php print $i; ?></option>
                      <?php endfor; ?>
                    </select>
                  </div>
                  <div class="col-xs-4">
                    <select id="alarm-minute" name="alarm-minute" class="form-control" required>
                      <?php for($i = 0; $i <= 59; $i++): ?>
                        <option value="<?php print str_pad($i, 2, '0', STR_PAD_LEFT); ?>"><?php print str_pad($i, 2, '0', STR_PAD_LEFT); ?></option>
                      <?php endfor; ?>
                    </select>
                  </div>
                  <div class="col-xs-4">
                    <select id="alarm-ampm" name="alarm-ampm" class="form-control" required>
                      <option value="AM">AM</option>
                      <option value="PM">PM</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
            <div class="col-md-6">
              <div class="form-group">
                <label for="alarm-sound"><?php print $lang['globalAlarmSound']; ?></label>
                <div id="refresh_alarm_sound">
                  <input id="alarm-sound" name="alarm-sound" placeholder="<?php print $lang['globalAlarmScanCard']; ?>" class="form-control input-md" type="text" readonly required>
                </div>
                <span class="help-block"><?php print $lang['globalAlarmScanCard']; ?></span>
              </div>
            </div>
          </div>
          
          <div class="form-group">
            <label><?php print $lang['globalAlarmRecurrence']; ?></label>
            <div class="row">
              <div class="col-md-12">
                <div class="btn-group" data-toggle="buttons">
                  <label class="btn btn-default day-btn" data-day="mon">
                    <input type="checkbox" name="days[]" value="mon" autocomplete="off"> Mon
                  </label>
                  <label class="btn btn-default day-btn" data-day="tue">
                    <input type="checkbox" name="days[]" value="tue" autocomplete="off"> Tue
                  </label>
                  <label class="btn btn-default day-btn" data-day="wed">
                    <input type="checkbox" name="days[]" value="wed" autocomplete="off"> Wed
                  </label>
                  <label class="btn btn-default day-btn" data-day="thu">
                    <input type="checkbox" name="days[]" value="thu" autocomplete="off"> Thu
                  </label>
                  <label class="btn btn-default day-btn" data-day="fri">
                    <input type="checkbox" name="days[]" value="fri" autocomplete="off"> Fri
                  </label>
                  <label class="btn btn-default day-btn" data-day="sat">
                    <input type="checkbox" name="days[]" value="sat" autocomplete="off"> Sat
                  </label>
                  <label class="btn btn-default day-btn" data-day="sun">
                    <input type="checkbox" name="days[]" value="sun" autocomplete="off"> Sun
                  </label>
                </div>
              </div>
            </div>
          </div>
          
          <div class="form-group">
            <button type="submit" class="btn btn-primary">
              <i class='mdi mdi-plus'></i> <?php print $lang['globalAddAlarm']; ?>
            </button>
            <a href="settings.php" class="btn btn-default">
              <i class='mdi mdi-arrow-left'></i> Back to Settings
            </a>
          </div>
        </form>
      </div>
    </div>
  </div>
</div>

<script>
$(document).ready(function() {
    // Initialize alarm sound field refresh
    $('#refresh_alarm_sound').load('ajax.refresh_alarm_sound.php');
    var refreshAlarmSound = setInterval(function() {
        $('#refresh_alarm_sound').load('ajax.refresh_alarm_sound.php?' + 1*new Date());
    }, 1000);
    
    // Handle day button toggles
    $('.day-btn').click(function() {
        var $this = $(this);
        var $checkbox = $this.find('input[type="checkbox"]');
        
        if ($checkbox.is(':checked')) {
            $this.removeClass('btn-default').addClass('btn-primary active');
        } else {
            $this.removeClass('btn-primary active').addClass('btn-default');
        }
    });
    
    // Handle form submission
    $('form').submit(function() {
        var selectedDays = $('input[name="days[]"]:checked').map(function() {
            return this.value;
        }).get();
        
        if (selectedDays.length === 0) {
            alert('Please select at least one day for the alarm to recur.');
            return false;
        }
        
        return true;
    });
});
</script>

</div><!-- /.container -->

</body>
</html> 