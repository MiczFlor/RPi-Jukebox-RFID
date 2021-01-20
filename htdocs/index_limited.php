<?php

include("inc.header.php");

/*******************************************
* START HTML
*******************************************/

html_bootstrap3_createHeader("en","Phoniebox",$conf['base_url']);

?>
<style>
.filterDiv {
  display: none;
}

.filtershow {
  display: block;
}

.filtercontainer {
  margin-top: 20px;
  overflow: hidden;
}

/* Style the buttons */
.filterbtn {
  border: none;
  outline: none;
  padding: 12px 16px;
  margin-bottom: 3px;
  background-color: #464545;
  color: white;
  cursor: pointer;
  border-top-right-radius: 4px;
  border-top-left-radius: 4px;
  border-bottom-right-radius: 4px;
  border-bottom-left-radius: 4px;
}

.filterbtn:hover {
  background-color: #f1f1f1;
  color: black;
}

.filterbtn.active {
  background-color: #0ce3ac;
  color: white;
}
</style>
<body>
  <div class="container">

<?php
//include("inc.navigation.php");

if($debug == "true") {
    print "<pre>";
    print "_POST: \n";
    print_r($_POST);
    print "</pre>";
}

?>

    <div class="row playerControls">
      <div class="col-lg-12">
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
      </div><!-- / .col-lg-12 -->
    </div><!-- /.row -->
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
