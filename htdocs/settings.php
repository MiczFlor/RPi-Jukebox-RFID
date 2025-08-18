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
              <button id="show-add-alarm-form" class="btn btn-primary btn">
                <i class='mdi mdi-plus'></i> <?php print $lang['globalAddAlarm']; ?>
              </button>
            </div>
            
            <!-- Add New Alarm Form (Hidden by default) -->
            <div id="add-alarm-form" style="display: none; margin-top: 20px;">
              <div class="panel panel-default">
                <div class="panel-heading">
                  <h5 class="panel-title"><?php print $lang['globalAddAlarm']; ?></h5>
                </div>
                <div class="panel-body">
                  <form id="alarm-form" method="post">
                    <!-- Grid Headers -->
                    <div class="row" style="margin-bottom: 15px;">
                      <div class="col-md-3">
                        <h5 style="margin: 0; color: white; font-weight: bold;">Time</h5>
                      </div>
                      <div class="col-md-3">
                        <h5 style="margin: 0; color: white; font-weight: bold;">Sound</h5>
                      </div>
                      <div class="col-md-4">
                        <h5 style="margin: 0; color: white; font-weight: bold;">Recurrence</h5>
                      </div>
                      <div class="col-md-2">
                        <h5 style="margin: 0; color: white; font-weight: bold;">Volume</h5>
                      </div>
                    </div>
                    
                    <!-- Grid Content -->
                    <div class="row">
                      <div class="col-md-3">
                        <div class="form-group">
                          <div class="row">
                            <div class="col-xs-4">
                              <select id="alarm-hour" name="alarm-hour" class="form-control alarm-time-select">
                                <?php for($i = 1; $i <= 12; $i++): ?>
                                  <option value="<?php print $i; ?>"><?php print $i; ?></option>
                                <?php endfor; ?>
                              </select>
                            </div>
                            <div class="col-xs-4">
                              <select id="alarm-minute" name="alarm-minute" class="form-control alarm-time-select">
                                <?php for($i = 0; $i <= 59; $i++): ?>
                                  <option value="<?php print str_pad($i, 2, '0', STR_PAD_LEFT); ?>"><?php print str_pad($i, 2, '0', STR_PAD_LEFT); ?></option>
                                <?php endfor; ?>
                              </select>
                            </div>
                            <div class="col-xs-4">
                              <select id="alarm-ampm" name="alarm-ampm" class="form-control alarm-time-select">
                                <option value="AM">AM</option>
                                <option value="PM">PM</option>
                              </select>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div class="col-md-3">
                        <div class="form-group">
                          <div id="refresh_alarm_sound">
                            <input id="alarm-sound" name="alarm-sound" placeholder="<?php print $lang['globalAlarmScanCard']; ?>" class="form-control input-md" type="text" readonly>
                          </div>
                          <span class="help-block"><?php print $lang['globalAlarmScanCard']; ?></span>
                        </div>
                      </div>
                      <div class="col-md-4">
                        <div class="form-group">
                          <div class="btn-group">
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
                      <div class="col-md-2">
                        <div class="form-group">
                          <select id="alarm-volume" name="alarm-volume" class="form-control">
                            <?php for($i = 100; $i >= 5; $i -= 5): ?>
                              <option value="<?php print $i; ?>"<?php if($i == 70) print ' selected'; ?>><?php print $i; ?>%</option>
                            <?php endfor; ?>
                          </select>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Buttons Row -->
                    <div class="row" style="margin-top: 20px;">
                      <div class="col-md-12 alarm-form-buttons">
                        <button type="submit" class="btn btn-success">
                          <i class='mdi mdi-check'></i> Save
                        </button>
                        <button type="button" id="cancel-add-alarm" class="btn btn-default">
                          <i class='mdi mdi-close'></i> Cancel
                        </button>
                      </div>
                    </div>
                  </form>
                </div>
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

</body>
<script src="js/jukebox.js">
</script>

<script>
$(document).ready(function() {
    // Load existing alarms
    $('#existing-alarms').load('ajax.load_alarms.php');
    
    // Initialize alarm sound field refresh
    $('#refresh_alarm_sound').load('ajax.refresh_alarm_sound.php');
    var refreshAlarmSound = setInterval(function() {
        $('#refresh_alarm_sound').load('ajax.refresh_alarm_sound.php?' + 1*new Date());
    }, 1000);
    
    // Show/hide add alarm form
    $('#show-add-alarm-form').click(function() {
        $('#add-alarm-form').show();
        $(this).hide();
    });
    
    // Cancel add alarm form
    $('#cancel-add-alarm').click(function() {
        $('#add-alarm-form').hide();
        $('#show-add-alarm-form').show();
        // Reset form
        $('#alarm-form')[0].reset();
        $('.day-btn').removeClass('btn-primary active').addClass('btn-default');
    });
    
    // Handle day button toggles
    $('.day-btn').click(function(e) {
        e.preventDefault(); // Prevent any default behavior
        
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
        
        // Debug logging
        console.log('Day button clicked:', $this.data('day'), 'New state:', newState);
    });
    
    // Handle form submission
    $('#alarm-form').submit(function(e) {
        e.preventDefault();
        
        var formData = $(this).serialize();
        var selectedDays = $('input[name="days[]"]:checked').map(function() {
            return this.value;
        }).get();
        
        if (selectedDays.length === 0) {
            alert('Please select at least one day for the alarm to recur.');
            return;
        }
        
        // Send the data to save the alarm
        $.ajax({
            url: 'ajax.save_alarm.php',
            type: 'POST',
            data: formData,
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    // Reset form and hide it
                    $('#alarm-form')[0].reset();
                    $('.day-btn').removeClass('btn-primary active').addClass('btn-default');
                    $('#add-alarm-form').hide();
                    $('#show-add-alarm-form').show();
                    
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
    
    $(document).on('click', '.edit-alarm', function() {
        var alarmId = $(this).data('id');
        
        // Load alarm data and populate the form
        $.ajax({
            url: 'ajax.load_alarm.php',
            type: 'GET',
            data: {
                alarm_id: alarmId
            },
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    var alarm = response.alarm;
                    
                    // Populate the form with alarm data
                    $('#alarm-hour').val(alarm.hour);
                    // Ensure minute is properly formatted to match select option values
                    $('#alarm-minute').val(String(alarm.minute).padStart(2, '0'));
                    $('#alarm-ampm').val(alarm.ampm);
                    $('#alarm-sound').val(alarm.sound);
                    $('#alarm-volume').val(alarm.volume);
                    
                    // Reset and set day buttons
                    $('.day-btn').removeClass('btn-primary active').addClass('btn-default');
                    $('input[name="days[]"]').prop('checked', false);
                    
                    alarm.days.forEach(function(day) {
                        $('input[name="days[]"][value="' + day + '"]').prop('checked', true);
                        $('.day-btn[data-day="' + day + '"]').removeClass('btn-default').addClass('btn-primary active');
                    });
                    
                    // Add hidden field for alarm ID and change form action
                    if (!$('#alarm-id').length) {
                        $('#alarm-form').append('<input type="hidden" id="alarm-id" name="alarm_id" value="' + alarmId + '">');
                    } else {
                        $('#alarm-id').val(alarmId);
                    }
                    
                    // Change form submission to update instead of create
                    $('#alarm-form').off('submit').on('submit', function(e) {
                        e.preventDefault();
                        
                        var formData = $(this).serialize();
                        var selectedDays = $('input[name="days[]"]:checked').map(function() {
                            return this.value;
                        }).get();
                        
                        if (selectedDays.length === 0) {
                            alert('Please select at least one day for the alarm to recur.');
                            return;
                        }
                        
                        // Send the data to update the alarm
                        $.ajax({
                            url: 'ajax.update_alarm.php',
                            type: 'POST',
                            data: formData,
                            dataType: 'json',
                            success: function(response) {
                                if (response.success) {
                                    // Reset form and hide it
                                    $('#alarm-form')[0].reset();
                                    $('.day-btn').removeClass('btn-primary active').addClass('btn-default');
                                    $('#add-alarm-form').hide();
                                    $('#show-add-alarm-form').show();
                                    
                                    // Remove hidden field and restore original form submission
                                    $('#alarm-id').remove();
                                    $('#alarm-form').off('submit').on('submit', function(e) {
                                        // Re-attach the original submit handler
                                        $('#alarm-form').trigger('submit');
                                    });
                                    
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
                    
                    // Show the form
                    $('#add-alarm-form').show();
                    $('#show-add-alarm-form').hide();
                } else {
                    alert('Error: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                alert('Error loading alarm data');
            }
        });
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
