<?php

include("inc.header.php");

/*******************************************
* START HTML
*******************************************/

html_bootstrap3_createHeader("en","Settings | Phoniebox",$conf['base_url']);

?>
<body>
  <div class="container">

<?php
include("inc.navigation.php");

if($debug == "true") {
    print "<pre>";
    print "_POST:\n";
    print_r($_POST);
    print "</pre>";
}

?>

<div class="row">
  <div class="col-lg-12">
  <strong><?php print $lang['globalJumpTo']; ?>:</strong>
        <a href="#RFID" class="xbtn xbtn-default ">
        <i class='mdi mdi-cards-outline'></i> <?php print $lang['globalRFIDCards']; ?>
        </a> |
        <a href="#alarms" class="xbtn xbtn-default ">
        <i class='mdi mdi-alarm'></i> <?php print $lang['globalAlarms']; ?>
        </a> |
        <a href="#language" class="xbtn xbtn-default ">
        <i class='mdi mdi-emoticon'></i> <?php print $lang['globalLanguageSettings']; ?>
        </a> |
        <a href="#volume" class="xbtn xbtn-default ">
        <i class='mdi mdi-volume-high'></i> <?php print $lang['globalVolumeSettings']; ?>
        </a> |
        <a href="#autoShutdown" class="xbtn xbtn-default ">
        <i class='mdi mdi-clock-end'></i> <?php print $lang['globalIdleShutdown']." / ".$lang['globalSleepTimer']; ?>
        </a> |
        <a href="#wifi" class="xbtn xbtn-default ">
        <i class='mdi mdi-wifi'></i> <?php print $lang['globalWifiSettings']; ?>
        </a> |
        <!--a href="#wlanIpEmail" class="xbtn xbtn-default ">
        <i class='mdi mdi-wifi'></i> <?php print $lang['settingsWlanSendNav']; ?>
        </a>  |-->
        <a href="#wlanIpRead" class="xbtn xbtn-default ">
        <i class='mdi mdi-wifi'></i> <?php print $lang['settingsWlanReadNav']; ?>
        </a>  |
        <a href="#webInterface" class="xbtn xbtn-default ">
        <i class='mdi mdi-cards-outline'></i> <?php print $lang['settingsWebInterface']; ?>
        </a>  |
        <a href="#externalInterfaces" class="xbtn xbtn-default ">
        <i class='mdi mdi-usb'></i> <?php print $lang['globalExternalInterfaces']; ?>
        </a>  |
        <a href="#secondSwipe" class="xbtn xbtn-default ">
        <i class='mdi mdi-cards-outline'></i> <?php print $lang['settingsSecondSwipe']; ?>
        </a> |
        <a href="#DebugLogSettings" class="xbtn xbtn-default ">
        <i class='mdi mdi-text'></i> <?php print $lang['infoDebugLogSettings']; ?>
        </a>

  </div>
</div>
        <br/>
<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="RFID"></a>
         <i class='mdi mdi-cards-outline'></i> <?php print $lang['indexManageFilesChips']; ?>
      </h4>
    </div><!-- /.panel-heading -->

      <div class="panel-body">
        <div class="row">
          <div class="col-lg-12">
                <a href="cardRegisterNew.php" class="btn btn-primary btn">
                <i class='mdi mdi-cards-outline'></i> <?php print $lang['globalRegisterCard']; ?>
                </a>
          </div><!-- / .col-lg-12 -->
        </div><!-- /.row -->
      </div><!-- /.panel-body -->

    </div><!-- /.panel -->
</div><!-- /.panel-group -->

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="alarms"></a>
         <i class='mdi mdi-alarm'></i> <?php print $lang['globalAlarms']; ?>
      </h4>
    </div><!-- /.panel-heading -->

      <div class="panel-body">
        <div class="row">
          <div class="col-lg-12">
            <!-- Existing Alarms Display -->
            <div id="existing-alarms">
              <!-- Alarms will be loaded here via AJAX -->
            </div>
            
            <!-- Add New Alarm Button -->
            <div style="margin-top: 20px;">
              <button id="show-new-alarm-table" class="btn btn-primary btn">
                <i class='mdi mdi-plus'></i> <?php print $lang['globalAddAlarm']; ?>
              </button>
            </div>
            
            <!-- New Alarm Table -->
            <div id="new-alarm-table-container" style="margin-top: 20px; display: none;">
              <div class="table-responsive">
                <table class="table table-striped alarm-table">
                  <thead>
                    <tr>
                      <th>Time</th>
                      <th>Sound</th>
                      <th>Days</th>
                      <th>Volume</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr id="new-alarm-row">
                      <td class="alarm-time-cell">
                        <div class="alarm-time-group">
                          <div class="row">
                            <div class="col-xs-4">
                              <select class="form-control input-sm new-hour">
                                <?php for($i = 1; $i <= 12; $i++): ?>
                                  <option value="<?php echo $i; ?>"><?php echo $i; ?></option>
                                <?php endfor; ?>
                              </select>
                            </div>
                            <div class="col-xs-4">
                              <select class="form-control input-sm new-minute">
                                <?php for($i = 0; $i <= 59; $i++): ?>
                                  <option value="<?php echo str_pad($i, 2, '0', STR_PAD_LEFT); ?>"><?php echo str_pad($i, 2, '0', STR_PAD_LEFT); ?></option>
                                <?php endfor; ?>
                              </select>
                            </div>
                            <div class="col-xs-4">
                              <select class="form-control input-sm new-ampm">
                                <option value="AM">AM</option>
                                <option value="PM">PM</option>
                              </select>
                            </div>
                          </div>
                        </div>
                      </td>
                      
                      <td class="alarm-sound-cell">
                        <div id="refresh_alarm_sound"></div>
                      </td>
                      
                      <td class="alarm-days-cell">
                        <div class="alarm-recurrence-group">
                          <?php 
                          $days = array('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun');
                          $day_names = array(
                            'mon' => 'Mon', 'tue' => 'Tue', 'wed' => 'Wed', 
                            'thu' => 'Thu', 'fri' => 'Fri', 'sat' => 'Sat', 'sun' => 'Sun'
                          );
                          foreach ($days as $day): ?>
                            <label class="btn btn-default day-btn new-day-btn" data-day="<?php echo $day; ?>">
                              <input type="checkbox" class="new-day-checkbox" value="<?php echo $day; ?>" autocomplete="off"> <?php echo $day_names[$day]; ?>
                            </label>
                          <?php endforeach; ?>
                        </div>
                      </td>
                      
                      <td class="alarm-volume-cell">
                        <select class="form-control input-sm new-volume">
                          <?php for($i = 100; $i >= 5; $i -= 5): ?>
                            <option value="<?php echo $i; ?>" <?php echo ($i == 70) ? 'selected' : ''; ?>><?php echo $i; ?>%</option>
                          <?php endfor; ?>
                        </select>
                      </td>
                      
                      <td class="alarm-actions">
                        <button class="btn btn-sm btn-success save-new-alarm" title="Save New Alarm">
                          <i class="mdi mdi-check"></i> Save
                        </button>
                        <button class="btn btn-sm btn-default cancel-new-alarm" title="Cancel">
                          <i class="mdi mdi-close"></i> Cancel
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div><!-- / .col-lg-12 -->
        </div><!-- /.row -->
      </div><!-- /.panel-body -->

    </div><!-- /.panel -->
</div><!-- /.panel-group -->

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="language"></a>
         <i class='mdi mdi-emoticon'></i> <?php print $lang['globalLanguageSettings']; ?>
      </h4>
    </div><!-- /.panel-heading -->

    <div class="panel-body">
      <div class="row">
<?php
include("inc.setLanguage.php");
?>
      </div><!-- / .row -->
    </div><!-- /.panel-body -->

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="language"></a>
         <i class='mdi mdi-emoticon'></i> <?php print $lang['settingsPlayoutBehaviourCard']; ?>
      </h4>
    </div><!-- /.panel-heading -->
    
    <div class="panel-body">
      <div class="row">
<?php
include("inc.setPlayerBehaviourRFID.php");
?>
      </div><!-- / .row -->
    </div><!-- /.panel-body -->

  </div><!-- /.panel -->
</div><!-- /.panel-group -->

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="volume"></a>
         <i class='mdi mdi-volume-high'></i> <?php print $lang['globalVolumeSettings']; ?>
      </h4>
    </div><!-- /.panel-heading -->

    <div class="panel-body">
      <div class="row">
<?php
include("inc.setVolume.php");
include("inc.setMaxVolume.php");
include("inc.setVolumeStep.php");
include("inc.setStartupVolume.php");
include("inc.setBootVolume.php");
?>
      </div><!-- / .row -->
    </div><!-- /.panel-body -->

  </div><!-- /.panel -->
</div><!-- /.panel-group -->


<?php
$filename = $conf['settings_abs'].'/bluetooth-sink-switch';
if (file_exists($filename)) {
   if (strcmp(strtolower(trim(file_get_contents($filename))), "enabled") === 0) {
      include('inc.bluetooth.php');
   }
}
?>


<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="autoShutdown"></a>
        <i class='mdi mdi-clock-end'></i> <?php print $lang['globalAutoShutdown']." ".$lang['globalSettings']; ?>
      </h4>
    </div><!-- /.panel-heading -->
    <div class="panel-body">

        <div class="row">

<?php
include("inc.setStoptimer.php");
include("inc.setSleeptimer.php");
include("inc.setShutdownVolumeReduction.php");
include("inc.setIdleShutdown.php");
?>
        </div><!-- / .row -->

    </div><!-- /.panel-body -->

  </div><!-- /.panel -->
</div><!-- /.panel-group -->

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="wifi"></a>
        <i class='mdi mdi-wifi'></i> <?php print $lang['globalWifiSettings']; ?>
      </h4>
    </div><!-- /.panel-heading -->

      <div class="panel-body">
<?php
include("inc.setWifi.php");
?>
      </div><!-- /.panel-body -->

  </div><!-- /.panel -->
</div><!-- /.panel-group -->

<?php
/*
* This is work in progress. 
* If you were to have a local mailserver installed, 
* Phoniebox could send you the IP address over email.
* Useful if you move your Phoniebox into a new Wifi which
* assigns a dynmamic IP.
*/
include("inc.setWlanIpRead.php");
?>

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="webInterface"></a>
        <i class='mdi mdi-cards-outline'></i> <?php print $lang['settingsWebInterface']; ?>
      </h4>
    </div><!-- /.panel-heading -->

      <div class="panel-body">

<?php
include("inc.setWebUI.php");
?>

      </div><!-- /.panel-body -->
  </div><!-- /.panel -->
</div><!-- /.panel-group -->

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="externalInterfaces"></a>
        <i class='mdi mdi-usb'></i> <?php print $lang['globalExternalInterfaces']; ?>
      </h4>
    </div><!-- /.panel-heading -->

      <div class="panel-body">
<?php
include("inc.setInputDevices.php");
?>
      </div><!-- /.panel-body -->
  </div><!-- /.panel -->
</div><!-- /.panel-group -->

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="secondSwipe"></a>
        <i class='mdi mdi-cards-outline'></i> <?php print $lang['settingsSecondSwipe']; ?>
      </h4>
    </div><!-- /.panel-heading -->

      <div class="panel-body">
<?php
include("inc.setSecondSwipe.php");
include("inc.setSecondSwipePause.php");
include("inc.setSecondSwipePauseControls.php");
?>
      </div><!-- /.panel-body -->

  </div><!-- /.panel -->
</div><!-- /.panel-group -->

<?php include("inc.setDebugLogConf.php"); ?>

</div><!-- /.container -->

<style>
/* Inline editing styles - preserve existing styling */
.alarm-edit {
    margin: 0;
}

.alarm-edit .form-control {
    margin-bottom: 0;
}

/* Smooth transitions */
.alarm-display, .alarm-edit {
    transition: opacity 0.2s ease;
}

/* Ensure edit mode doesn't interfere with Bootstrap table styling */
.alarm-edit {
    background-color: transparent !important;
}

/* Preserve Bootstrap table striping */
.alarm-table tbody tr {
    background-color: inherit !important;
}

/* Make sure edit controls are properly sized */
.alarm-edit select,
.alarm-edit input {
    height: 30px;
    padding: 5px 8px;
}

/* Preserve existing day button styling from func.php */
.alarm-edit .day-btn,
.new-day-btn {
    width: 35px;
    height: 35px;
    border-radius: 50% !important;
    margin: 1px;
    padding: 0;
    line-height: 33px;
    text-align: center;
    font-size: 10px;
    font-weight: bold;
    border: 2px solid #ddd;
}

.alarm-edit .day-btn.active,
.alarm-edit .day-btn.btn-primary,
.new-day-btn.active,
.new-day-btn.btn-primary {
    background-color: #337ab7;
    border-color: #337ab7;
    color: white;
}

.alarm-edit .day-btn:hover,
.new-day-btn:hover {
    border-color: #337ab7;
}

.alarm-edit .day-btn input[type="checkbox"],
.new-day-btn input[type="checkbox"] {
    display: none;
}

/* Make inline editing more compact */
.alarm-edit .alarm-time-group,
.alarm-edit .alarm-recurrence-group {
    margin-bottom: 0;
}

/* Compact time selector styling with proper spacing */
.alarm-time-group .row {
    margin-left: -2.5px;
    margin-right: -2.5px;
    min-width: 165px;
}

.alarm-time-group .col-xs-4 {
    padding-left: 2.5px;
    padding-right: 2.5px;
    width: 55px;
}

.alarm-time-group .form-control {
    width: 100%;
    min-width: 48px;
    padding: 4px 6px;
    font-size: 12px;
}

/* Volume selector styling */
.alarm-volume-cell .form-control {
    width: 70px;
    min-width: 70px;
}

.alarm-edit .form-control {
    height: 28px;
    padding: 4px 6px;
    font-size: 12px;
}

/* New alarm row styling */
#refresh_alarm_sound {
    max-width: 120px;
}

#refresh_alarm_sound .form-control {
    width: 100%;
    height: 28px;
    padding: 4px 6px;
    font-size: 12px;
}

/* Old fixed-width rules removed - now using percentage-based widths above */

/* Table layout with percentage-based widths */
.alarm-table {
    table-layout: auto;
    width: 100%;
}

.alarm-table td {
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Percentage-based column widths with min-width constraints */
.alarm-table .alarm-time-cell {
    width: 20%;
    min-width: 165px;
}

.alarm-table .alarm-sound-cell {
    width: 15%;
    min-width: 120px;
}

.alarm-table .alarm-days-cell {
    width: 35%;
    min-width: 275px;
}

.alarm-table .alarm-volume-cell {
    width: 8%;
    min-width: 65px;
}

.alarm-table .alarm-status-cell {
    width: 10%;
    min-width: 80px;
}

.alarm-table .alarm-actions {
    width: 12%;
    min-width: 120px;
}

/* New alarm table specific styling */
#new-alarm-table-container {
    width: 100%;
}

#new-alarm-table-container .table-responsive {
    width: 100%;
}

#new-alarm-table-container .alarm-table {
    width: 100%;
    margin-bottom: 0;
}

/* New alarm table uses the same percentage-based widths as existing alarms */
</style>

</body>
<script src="js/jukebox.js">
</script>

<script>
$(document).ready(function() {
    // Load existing alarms
    $('#existing-alarms').load('ajax.load_alarms.php');
    
    // Initialize alarm sound field refresh for new alarm row (same pattern as Register New Card)
    $('#refresh_alarm_sound').load('ajax.refresh_alarm_sound.php');
    var refreshNewAlarmSound = setInterval(function() {
        $('#refresh_alarm_sound').load('ajax.refresh_alarm_sound.php?' + 1*new Date());
    }, 1000);
    
    // Show/hide new alarm table
    $('#show-new-alarm-table').click(function() {
        $('#new-alarm-table-container').show();
        $(this).hide();
    });
    
    // Cancel new alarm
    $(document).on('click', '.cancel-new-alarm', function() {
        $('#new-alarm-table-container').hide();
        $('#show-new-alarm-table').show();
        // Reset new alarm row
        $('.new-hour').val('1');
        $('.new-minute').val('00');
        $('.new-ampm').val('AM');
        $('.new-volume').val('70');
        $('.new-day-checkbox').prop('checked', false);
        $('.new-day-btn').removeClass('btn-primary active').addClass('btn-default');
    });
    
    // Save new alarm
    $(document).on('click', '.save-new-alarm', function() {
        var selectedDays = $('.new-day-checkbox:checked').map(function() {
            return this.value;
        }).get();
        
        if (selectedDays.length === 0) {
            alert('Please select at least one day for the alarm to recur.');
            return;
        }
        
        var alarmData = {
            'alarm-hour': $('.new-hour').val(),
            'alarm-minute': $('.new-minute').val(),
            'alarm-ampm': $('.new-ampm').val(),
            'alarm-sound': $('#alarm-sound').val(),
            'alarm-volume': $('.new-volume').val(),
            'days': selectedDays
        };
        
        // Send the data to save the alarm
        $.ajax({
            url: 'ajax.save_alarm.php',
            type: 'POST',
            data: alarmData,
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    // Hide new alarm table and show button
                    $('#new-alarm-table-container').hide();
                    $('#show-new-alarm-table').show();
                    
                    // Reset new alarm row
                    $('.new-hour').val('1');
                    $('.new-minute').val('00');
                    $('.new-ampm').val('AM');
                    $('.new-volume').val('70');
                    $('.new-day-checkbox').prop('checked', false);
                    $('.new-day-btn').removeClass('btn-primary active').addClass('btn-default');
                    
                    // Reload the alarms list to show the new alarm
                    $('#existing-alarms').load('ajax.load_alarms.php');
                } else {
                    alert('Error: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                var response = JSON.parse(xhr.responseText);
                alert('Error: ' + (response.message || 'Failed to save alarm'));
            }
        });
    });
    
    // Handle alarm actions (delegate to handle dynamically loaded content)
    $(document).on('click', '.toggle-alarm', function() {
        var alarmId = $(this).data('id');
        var enabled = $(this).data('enabled');
        
        // Send the data to update the alarm
        $.ajax({
            url: 'ajax.update_alarm.php',
            type: 'POST',
            data: {
                alarm_id: alarmId,
                enabled: enabled ? '0' : '1'
            },
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    // Reload the alarms list
                    $('#existing-alarms').load('ajax.load_alarms.php');
                } else {
                    alert('Error: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                var response = JSON.parse(xhr.responseText);
                alert('Error: ' + (response.message || 'Failed to update alarm'));
            }
        });
    });
    
    // Edit alarm - switch to edit mode
    $(document).on('click', '.edit-alarm', function() {
        var $row = $(this).closest('tr');
        var alarmId = $(this).data('id');
        
        // Switch to edit mode
        $row.find('.alarm-display').hide();
        $row.find('.alarm-edit').show();
        
        // Store original values for cancel
        $row.data('original-values', {
            hour: $row.find('.edit-hour').val(),
            minute: $row.find('.edit-minute').val(),
            ampm: $row.find('.edit-ampm').val(),
            volume: $row.find('.edit-volume').val(),
            days: $row.find('.edit-day-checkbox:checked').map(function() { return this.value; }).get()
        });
    });
    
    // Cancel edit - restore original values and switch back to display mode
    $(document).on('click', '.cancel-edit', function() {
        var $row = $(this).closest('tr');
        var originalValues = $row.data('original-values');
        
        if (originalValues) {
            // Restore original values
            $row.find('.edit-hour').val(originalValues.hour);
            $row.find('.edit-minute').val(originalValues.minute);
            $row.find('.edit-ampm').val(originalValues.ampm);
            $row.find('.edit-volume').val(originalValues.volume);
            
            // Restore original day selections
            $row.find('.edit-day-checkbox').prop('checked', false);
            $row.find('.edit-day-btn').removeClass('btn-primary active').addClass('btn-default');
            originalValues.days.forEach(function(day) {
                $row.find('.edit-day-checkbox[value="' + day + '"]').prop('checked', true);
                $row.find('.edit-day-btn[data-day="' + day + '"]').removeClass('btn-default').addClass('btn-primary active');
            });
        }
        
        // Switch back to display mode
        $row.find('.alarm-display').show();
        $row.find('.alarm-edit').hide();
    });
    
    // Save alarm changes
    $(document).on('click', '.save-alarm', function() {
        var $row = $(this).closest('tr');
        var alarmId = $(this).data('id');
        
        var selectedDays = $row.find('.edit-day-checkbox:checked').map(function() {
            return this.value;
        }).get();
        
        if (selectedDays.length === 0) {
            alert('Please select at least one day for the alarm to recur.');
            return;
        }
        
        var alarmData = {
            'alarm_id': alarmId,
            'alarm-hour': $row.find('.edit-hour').val(),
            'alarm-minute': $row.find('.edit-minute').val(),
            'alarm-ampm': $row.find('.edit-ampm').val(),
            'alarm-sound': $row.find('.alarm-sound-cell .alarm-display code').text(),
            'alarm-volume': $row.find('.edit-volume').val(),
            'days': selectedDays
        };
        
        // Send the data to update the alarm
        $.ajax({
            url: 'ajax.update_alarm.php',
            type: 'POST',
            data: alarmData,
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    // Reload the alarms list to show updated values
                    $('#existing-alarms').load('ajax.load_alarms.php');
                } else {
                    alert('Error: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                var response = JSON.parse(xhr.responseText);
                alert('Error: ' + (response.message || 'Failed to update alarm'));
            }
        });
    });
    
    // Handle day button toggles for editing
    $(document).on('click', '.edit-day-btn', function(e) {
        e.preventDefault();
        
        var $this = $(this);
        var $checkbox = $this.find('input[type="checkbox"]');
        
        // Toggle the checkbox state
        var newState = !$checkbox.prop('checked');
        $checkbox.prop('checked', newState);
        
        // Update button styling based on new checkbox state
        if (newState) {
            $this.removeClass('btn-default').addClass('btn-primary active');
        } else {
            $this.removeClass('btn-primary active').addClass('btn-default');
        }
    });
    
    // Handle day button toggles for new alarm
    $(document).on('click', '.new-day-btn', function(e) {
        e.preventDefault();
        
        var $this = $(this);
        var $checkbox = $this.find('input[type="checkbox"]');
        
        // Toggle the checkbox state
        var newState = !$checkbox.prop('checked');
        $checkbox.prop('checked', newState);
        
        // Update button styling based on new checkbox state
        if (newState) {
            $this.removeClass('btn-default').addClass('btn-primary active');
        } else {
            $this.removeClass('btn-primary active').addClass('btn-default');
        }
    });
    
    $(document).on('click', '.delete-alarm', function() {
        var alarmId = $(this).data('id');
        
        if (confirm('Are you sure you want to delete this alarm?')) {
            // Send the data to delete the alarm
            $.ajax({
                url: 'ajax.delete_alarm.php',
                type: 'POST',
                data: {
                    alarm_id: alarmId
                },
                dataType: 'json',
                success: function(response) {
                    if (response.success) {
                        // Reload the alarms list
                        $('#existing-alarms').load('ajax.load_alarms.php');
                    } else {
                        alert('Error: ' + response.message);
                    }
                },
                error: function(xhr, status, error) {
                    var response = JSON.parse(xhr.responseText);
                    alert('Error: ' + (response.message || 'Failed to delete alarm'));
                }
            });
        }
    });
});
</script>
</html>
