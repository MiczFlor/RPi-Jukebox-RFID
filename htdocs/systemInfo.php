<?php

include("inc.header.php");

/*******************************************
* START HTML
*******************************************/

html_bootstrap3_createHeader("en","Phoniebox",$conf['base_url']);

?>
<body>
  <div class="container">

<?php
include("inc.navigation.php");

// get Phoniebox Version
$exec = "cat ".$conf["base_path"]."/settings/version";
if($debug == "true") { 
		print "Command: ".$exec; 
} else {
		$version = exec($exec); 
}

// get System Information and parse into variables
$exec = "lsb_release -a";
if($debug == "true") { 
		print "Command: ".$exec; 
} else { 
		exec($exec, $res);
		$distributor = substr($res[0],strpos($res[0],":")+1,strlen($res[0])-strpos($res[0],":"));
		$description = substr($res[1],strpos($res[1],":")+1,strlen($res[1])-strpos($res[1],":"));
		$release = substr($res[2],strpos($res[2],":")+1,strlen($res[2])-strpos($res[2],":"));
		$codename = substr($res[3],strpos($res[3],":")+1,strlen($res[3])-strpos($res[3],":"));
}
?>
<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title">
         <i class='mdi mdi-settings'></i> <?php print $lang['globalSystem']; ?> 
      </h4>
    </div><!-- /.panel-heading -->

    <div class="panel-body">
  
        <div class="row">	
          <label class="col-md-4 control-label" for=""><?php print $lang['infoOsDistrib']; ?></label> 
          <div class="col-md-6"><?php echo trim($distributor); ?></div>
        </div><!-- / row -->
        <div class="row">	
          <label class="col-md-4 control-label" for=""><?php print $lang['globalDescription']; ?></label> 
          <div class="col-md-6"><?php echo trim($description); ?></div>
        </div><!-- / row -->
        <div class="row">	
          <label class="col-md-4 control-label" for=""><?php print $lang['globalRelease']; ?></label> 
          <div class="col-md-6"><?php echo trim($release); ?></div>
        </div><!-- / row -->
        <div class="row">	
          <label class="col-md-4 control-label" for=""><?php print $lang['infoOsCodename']; ?></label> 
          <div class="col-md-6"><?php echo trim($codename); ?></div>
        </div>     
	</div><!-- /.panel-body -->
  </div><!-- /.panel panel-default-->
</div><!-- /.panel-group -->

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title">
         <i class='mdi mdi-settings'></i> Phoniebox Setup
      </h4>
    </div><!-- /.panel-heading -->

    <div class="panel-body">
  
        <div class="row">	
          <label class="col-md-4 control-label" for=""><?php print $lang['globalVersion']; ?></label> 
          <div class="col-md-6"><?php echo $version; ?></div>
        </div><!-- / row -->
        <div class="row">	
          <label class="col-md-4 control-label" for=""><?php print $lang['globalEdition']; ?></label> 
          <div class="col-md-6"><?php echo $lang[$edition]; ?></div>
        </div><!-- / row -->
		<div class="row">	
          <label class="col-md-4 control-label" for="">
		  <?php
		  if ($edition == "classic") {
			  print $lang['infoMPDStatus']."</label> 
		  <div id='mpdstatus'></div>";
		  } elseif ($edition == "plusSpotify") {
			  print $lang['infoMopidyStatus']."</label> 
		  <div id='mopidystatus'></div>";
		  }
		  ?>
		</div>
		<!-- / row -->
      
	</div><!-- /.panel-body -->
  </div><!-- /.panel panel-default-->
</div><!-- /.panel-group -->


<?php
if ($edition == "classic") {
	print "<script>
$(document).ready(function() {
    $('#mpdstatus').load('ajax.loadMPDStatus.php');
    var refreshId = setInterval(function() {
        $('#mpdstatus').load('ajax.loadMPDStatus.php?' + 1*new Date());
    }, 5000);
});

</script>";
} elseif ($edition == "plusSpotify") {
	print "<script>
$(document).ready(function() {
    $('#mopidystatus').load('ajax.loadMopidyStatus.php');
    var refreshId = setInterval(function() {
        $('#mopidystatus').load('ajax.loadMopidyStatus.php?' + 1*new Date());
    }, 5000);
});

</script>";
}
?>

<?php
// get the information of storage usage
$exec = "df -H -B K / ";
    if($debug == "true") { 
        print "Command: ".$exec; 
    } else { 
				$exploded = preg_split("/ +/", exec($exec));
				// all values are in MeBit
        $all = round(Trim(substr($exploded[1],0,Strpos($exploded[1],"K")))/1024, 2);
        $used = round(Trim(substr($exploded[2],0,Strpos($exploded[2],"K")))/1024, 2);
        $free = round(Trim(substr($exploded[3],0,Strpos($exploded[3],"K")))/1024, 2);
	}
?>

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title">
        <i class='mdi mdi-server'></i> <?php print $lang['globalStorage']; ?> <small>(<?php echo round($all/1024,2); ?> GB)</small>
      </h4>
    </div><!-- /.panel-heading -->

		<div class="panel-body">

		<?php	
			// get information about the shared folder to calculate media size
			$exec = "du -H -B K -s ".$conf['base_path']."/shared/";
			if($debug == "true") { 
					print "Command: ".$exec; 
			} else { 
					$res = exec($exec);
					$exploded = explode("/", $res);
					$Media = round(Trim(substr($exploded[0],0,Strpos($exploded[0],"K")))/1024, 2);
			}
			// make some percentage calculation
			$percent = 100/$all;
			$reserved = $all - $used - $free;
			$system = $used - $Media;
		?>

			<h5><?php print $lang['infoStorageUsed']; ?> <small>(<?php echo round($free/1024,2); ?> GB free)</small></h5>
			<div class="row">
				<div class="col-xs-12">
					<div class="progress">
						<div class="progress-bar progress-bar-warning" role="progressbar" title="Reserved: <?php echo round($reserved*$percent, 2); ?>%" style="width:<?php echo round($reserved*$percent, 2); ?>%">Res.</div>
						<div class="progress-bar progress-bar-danger" role="progressbar" title="System: <?php echo round($system*$percent, 2); ?>%" style="width:<?php echo round($system*$percent, 2); ?>%">Sys.</div>
						<div class="progress-bar progress-bar progress-bar-info" role="progressbar" title="Media: <?php echo round($Media*$percent, 2); ?>%" style="width:<?php echo round($Media*$percent, 2); ?>%">Media</div>
						<div class="progress-bar progress-bar-success" role="progressbar" title="Free: <?php echo round($free*$percent, 2); ?>%" style="width:<?php echo round($free*$percent, 2); ?>%">Free</div>
					</div><!-- / .progress -->
				</div><!-- / .col-xs-12 -->
			</div><!-- / .row -->
			</div><!-- /.panel-body -->
  </div><!-- /.panel -->
</div><!-- /.panel-group -->
</div><!-- /.container -->

</body>
</html>
