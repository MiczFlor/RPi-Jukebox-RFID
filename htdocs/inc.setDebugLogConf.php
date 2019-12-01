
<?php
if(
    isset($_POST['debugLogConf']) 
    && is_array($_POST['debugLogConf'])
    ) {
        // create file
        $debugLoggingConf = "";
        foreach($debugAvail as $debugItem) {
            if(
                isset($_POST['debugLogConf'][$debugItem])
                && $_POST['debugLogConf'][$debugItem] != ""
            ) {
                $debugLoggingConf .= $debugItem."=\"".$_POST['debugLogConf'][$debugItem]."\"\n";
            } else {
                $debugLoggingConf .= $debugItem."=\"FALSE\"\n";
            }
        }
        file_put_contents("../settings/debugLogging.conf", $debugLoggingConf);
        // read file
        $debugLoggingConf = parse_ini_file("../settings/debugLogging.conf");
        if($debug == "true") {
            print "<pre>".$debugLoggingConf."</pre>";
        }
}

?>

<div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title"><a name="DebugLogSettings"></a>
        <i class="mdi mdi-text"></i> <?php print $lang['infoDebugLogSettings']; ?></h4>
    </div><!-- /.panel-heading -->

      <div class="panel-body">

<form name="volume" method="post" action="settings.php">
    <fieldset>
        <!-- Form Name -->
        <legend><?php print $lang['infoDebugLogSettings']; ?></legend>
        <ul class="list-group">
            <li class="list-group-item">
                <div class="row">


<?php
foreach($debugAvail as $debugItem) {
    print '
                    <!-- Text input-->
                    <div class="form-group">
                      <label class="col-md-4 control-label" for="htdocs">'.$debugItem.'</label>
                      <div class="col-md-6">
                        <select id="'.$debugItem.'" name="debugLogConf['.$debugItem.']" class="form-control">';
    foreach($debugOptions as $debugOptionVal) {
                        print "
                        <option value='".$debugOptionVal."'";
                        if(trim($debugLoggingConf[$debugItem]) == trim($debugOptionVal)) {
                            print " selected='selected'";
                        }
                        print ">".$debugOptionVal."</option>\n";
    }
    print "            </select> \n<br>\n";
    print "
                      </div>
                    </div>";
}
?>
                </div><!-- /row -->
            </li>
        </ul>
    </fieldset>

    <!-- Button (Double) -->
    <div class="form-group">
        <label class="col-md-4 control-label" for="submit"></label>
        <div class="col-md-8">
            <button id="submitDebugSettings" name="submitDebugSettings" class="btn btn-success" value="submit">Submit</button>
            <br clear="all"><br>
        </div>
    </div>

</form>
      </div><!-- /.panel-body -->

  </div>
