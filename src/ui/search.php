<?php

include("inc.header.php");

/*******************************************
* START HTML
*******************************************/

html_bootstrap3_createHeader("en","Search | Phoniebox",$conf['base_url']);

?>
<body>
  <div class="container">

<?php
include("inc.navigation.php");
?>
<!-- file search -->

<form name='volume' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>

<div class="panel-group">
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title">
        <i class='mdi mdi-text'></i> <?php print $lang['searchTitle']; ?>
        <br><br>
	<input value="" id="searchText" name="searchText" placeholder="<?php print $lang[searchExample]; ?>" class="form-control input-md" type="text">
	<br>
	<button id="submitSearch" name="submitSearch" class="btn btn-success" value="submit"><?php print $lang['searchSend']; ?></button>
      </h4>
    </div><!-- /.panel-heading -->

    <div class="panel-body">
	<?php
	if(isset($_POST["submitSearch"]) && $_POST["submitSearch"] == "submit") {
	  foreach ( $_POST as $post_key => $post_value ) {
	    if ( $post_key == "searchText" ) {
	      // implement search for string
		function iterate_dir($path) {
		    $files = array( );
		    if (is_dir($path) & is_readable($path)) {
		        $dir = dir($path);
		        while (false !== ($file = $dir->read( ))) {
		            // skip . and .. 
		            if (('.' == $file) || ('..' == $file)) {
		                continue;
		            }
		            if (is_dir("$path/$file")) {
		                $files = array_merge($files, iterate_dir("$path/$file"));
		            } else {
		                array_push($files, $path . "/" . $file);
		            }
		        }
		        $dir->close( );
		    }
		    return $files;
		}
		$files = iterate_dir($Audio_Folders_Path);

		// print the results
                print $lang['searchResult'] . "<br><br>";
                print "<ol class='list-group'>";

		foreach ($files as $file) {
		  if (preg_match("/".$post_value."/i", basename($file))) {

		    // Option 1: regular links (dirty)
//		    print "<a href=\"playsinglefile.php?file=$file\"><strong>" . basename($file) . "</strong></a><br>";

		    // Option 2: php-call with arrow (not nice)
//                    print "<li class='list-group-item'>" .
//		    "<a onclick='api/playlist/playsinglefile.php?file=$file' class='btn-panel-small btn-panel-col' title='Play song' style='cursor: pointer'>

		    // Option 3: with small arrow file using java-functions
                    print "<li class='list-group-item'>" . 
		    "<a onclick='playSingleFile(\"$file\");' class='btn-panel-small btn-panel-col' title='Play song' style='cursor: pointer'>
		    <i class='mdi mdi-play-circle-outline'></i></a>
                    <a onclick='appendFileToPlaylist(\"$file\");' class='btn-panel-small btn-panel-col' title='Append song to playlist'
                    style='cursor: pointer'> <i class='mdi mdi-plus-circle-outline'></i></a>
                    <strong>".basename($file)."</strong>";
                    print "&nbsp;&nbsp; <a href='trackEdit.php?folder=".dirname($file)."&filename=".basename($file)."'><i class='mdi mdi-text'></i> Edit</a>";
                    print "</li>";
		  }
		}

                print "</ol>";
	    }
	  }
	}
	$_POST=array(); //clear
	?>

	</div><!-- /.panel-body -->
  </div><!-- /.panel -->
</div><!-- /.panel-group -->

</form>

</div><!-- /.container -->

</body>
</html>

<script src="js/jukebox.js">
</script>
<script>
        JUKEBOX.lang = <?php echo json_encode($lang );?>
</script>

