<!--
    (1) Bluetooth device status and audio sink status
    (2) Button for toggling between HAT speakers and bluetooth speakers/headphones

    Ajax calls refresh bluetooth and audio sink state periodically to reflect
    connection of bluetooth device or changes done by other user interfaces
-->

<script>
    $(document).ready(function() {
      $('#btstatus_id').load('ajax.getBluetoothStatus.php')});
    var refreshId = setInterval(function() {
        $('#btstatus_id').load('ajax.getBluetoothStatus.php');
      }, 2000);
    $(document).ready(function() {
      $('#audiosink_id').load('ajax.getAudioSink.php')});
    var refreshId = setInterval(function() {
        $('#audiosink_id').load('ajax.getAudioSink.php');
      }, 2000);
</script>

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title">
         <i class='mdi mdi-volume-high'></i> <?php print $lang['globalAudioSink']; ?> 
      </h4>
      <?php
	if(isset($_POST['btToggle'])) {
  	  $btswitch = shell_exec($conf['scripts_abs']."/playout_controls.sh -c=bluetoothtoggle -v=toggle");
	  print "<br>";
	  print "<div class=\"row\">";
          print "  <div class=\"col-md-12\">";
          if (strpos($btswitch, "Default") === false) {
            print "    <div class=\"alert alert-success\">";
          }  else {
            print "    <div class=\"alert alert-warning\">"; 
          }
	  print "Message: $btswitch</div>";
          print "  </div>";
          print "</div>";
	}
      ?>
    </div><!-- /.panel-heading -->


    <div class="panel-body">    	
        <div class="row">	
          <label class="col-md-4 control-label" for=""><?php print $lang['infoBluetoothStatus']; ?></label> 
          <div class="col-md-6"><span id="btstatus_id"></span></div>
        </div>
        <div class="row">	
          <label class="col-md-4 control-label" for=""><?php print $lang['infoAudioActive']; ?></label> 
          <div class="col-md-6"><span id="audiosink_id"></span>
	  </div>
        </div>
        <div class="row">
	  <div class="col-md-12">
   	    <form method="post">
              <button id="btToggle" name="btToggle" class="btn btn-info" value="submit">Toggle audio sink</button>
            </form>
	  </div>
	</div><!-- ./row -->
    </div><!-- /.panel-body -->	
  </div><!-- /.panel panel-default-->
</div><!-- /.panel-group -->

