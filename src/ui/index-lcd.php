<?php

include("inc.header.php");

/*******************************************
* START HTML
*******************************************/

html_bootstrap3_createHeader("en","Phoniebox",$conf['base_url']);

?>
<style type="text/css">
  .container {
    width: 100% !important;
    height: 100vh;
    overflow: hidden;
  }
  div#coverWrapper {
    right: 0;
    position: absolute;
    bottom: 0;
  }
  .row.playerControls {
    height: 100vh;
    margin-bottom: 0;
  }
  i.mdi, .mdi-48px.mdi-set, .mdi-48px.mdi:before, .mdi-72px, .mdi-72px.mdi:before, .mdi-72px.mdi-play, .mdi-72px.mdi-pause, .mdi-72px-mdi-set, .mdi-24px.mdi-set, .mdi-24px.mdi:before {
    font-size: 125px;
  }
  .btn-group.controlVolumeUpDown:nth-child(2) {
    margin-left: -105px;
  }
</style>
<body>
  <div class="container">



    <div class="row playerControls">
<?php
/*
* Do we need to voice a warning here?
*/
if(isset($warning)) {
    print '<div class="alert alert-warning">'.$warning.'</div>';
}

print '<div id="api-alert" class="alert alert-warning" style="display: none"></div>';
include("inc.controlPlayer.php");

?>

    </div><!-- /.row -->


    <div class="row">
      <div class="col-lg-12">
   
    </div><!-- ./col-lg-12 -->
    </div><!-- ./row -->

    <div class="row">
      <div class="col-lg-12">
      <div class="row">
<?php

// show currently played track

    print '
    <div class="row">
        <div class="col-lg-12">';
include("inc.loadedPlaylist.php");
    print '
        </div><!-- / .col-lg-12 -->
    </div><!-- /.row -->';
?>
    <div class="row">
      <div class="col-lg-12">
<?php
include("inc.setVolume.php");
?>
    </div><!-- ./col-lg-12 -->
    </div><!-- ./row -->

    <div class="row">
      <div class="col-lg-12">
        <h3><?php print $lang['indexAvailAudio']; ?></h3>
      <div class="row">

<?php

// read the shortcuts used
$shortcutstemp = array_filter(glob($conf['base_path'].'/shared/shortcuts/*'), 'is_file');
$shortcuts = array(); // the array with pairs of ID => foldername
// read files' content into array
foreach ($shortcutstemp as $shortcuttemp) {
    $shortcuts[basename($shortcuttemp)] = trim(file_get_contents($shortcuttemp));
}
//print "<pre>"; print_r($shortcutstemp); print "</pre>"; //???
//print "<pre>"; print_r($shortcuts); print "</pre>"; //???

// read the subfolders of $Audio_Folders_Path
$audiofolders = array_filter(glob($Audio_Folders_Path.'/*'), 'is_dir');
usort($audiofolders, 'strcasecmp');

// counter for ID of each folder
$idcounter = 0;

// go through all folders
foreach($audiofolders as $audiofolder) {
    // increase ID counter
    $idcounter++;
    
    include('inc.viewFolderTree.php');
    
}

?>

      </div><!-- / .col-lg-12 -->

	      
    </div><!-- /.row -->
    
    <!-- Modal -->
    <div class="modal fade" id="myModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
            <h4 class="modal-title" id="myModalLabel"><?php print $lang['globalLastUsedCard']; ?></h4>
          </div>
          <div class="modal-body">
<pre>
<!--?php
print file_get_contents($conf['base_path'].'/shared/latestID.txt', true);
?-->
</pre>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-default" data-dismiss="modal"><!--?php print $lang['globalClose']; ?--></button>
          </div>
    
        </div><!-- / .modal-content -->
      </div><!-- /.modal-dialog -->
    </div><!-- /.modal -->


  </div><!-- /.container -->

</body>

<script src="js/jukebox.js">
</script>
<script>
	JUKEBOX.lang = <?php echo json_encode($lang );?>
</script>
</html>
