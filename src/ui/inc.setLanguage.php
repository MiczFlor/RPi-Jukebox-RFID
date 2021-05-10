
<?php
/*
Checking if we need to change something and changing it is done
before loading the language in the file
inc.langLoad.php
called in inc.header.php
*/

/*
* Create up to date file if language was changed including the default English values
*/
if(
    isset($_POST['lang']) 
    && trim($_POST['lang']) != ""
    && trim($_POST['lang']) != "en-UK"
    ) {
    /**/

    $filename = realpath('lang/lang-'.$_POST['lang'].'.php');
    
    $langPHP = "<?php\n\$lang = array();\n";
    foreach($langDef as $langKey => $langVal) {
        //$langPHP .= "// ".$langKey." => ".$langVal."\n";
        if(isset($langCustom[$langKey])) {
            $langPHP .= "\$lang['".$langKey."'] = \"".str_replace('"', '\"', $langCustom[$langKey])."\";\n";
        } else {
            $langPHP .= "\$lang['".$langKey."'] = \"".str_replace('"', '\"', $langDef[$langKey])."\";\n";
            $messageLangfileNewItems = $lang['settingsMessageLangfileNewItems'];
        }
    }
    $langPHP .= "?>\n";

    // write new file only if there are new items
    if(isset($messageLangfileNewItems)) {
        file_put_contents($filename, $langPHP);
    }
    /*
    print "<pre>".$filename; print $langPHP; print "</pre>";
    if(file_exists($filename)) {
        print "File exists: ".$filename;
    }
    /**/
}

/*
* get available languages
*/
$langAvail = array();
foreach (glob("lang/*.php") as $filename) {
    //echo substr($filename,-9,5)." $filename - Größe: " . filesize($filename) . "\n";
    $langAvail[substr($filename,-9,5)] = substr($filename,-9,5);
}
?>
        <!-- input-group --> 
        <div class="col-md-4 col-sm-6">
              <h4><?php print $lang['globalLang']; ?></h4>
<?php
if(isset($messageLangfileNewItems)) {
    print "
              <h4>".$messageLangfileNewItems."</h4>
              ";
}
?>                
                <form name='lang' method='post' action='<?php print $_SERVER['PHP_SELF']; ?>'>
                  <div class="input-group my-group">
                    <select id="lang" name="lang" class="form-control">
<?php
foreach($langAvail as $langItem) {
                        print "
                        <option value='".$langItem."'";
                        if($conf['settings_lang'] == $langItem) {
                            print " selected";
                        }
                        print ">".$langItem;
                        print "</option>\n";
}
?>
                    </select> 
                    <span class="input-group-btn">
                        <input type='submit' class="btn btn-default" name='submit' value='<?php print $lang['globalSet']; ?>'/>
                    </span>
                  </div>
                </form>              
        </div>
        <!-- /input-group -->
