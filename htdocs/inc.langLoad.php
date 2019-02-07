<?php
/*
* first see if we have something from the settings page form to do
* values come from inc.setLanguage.php
*/
if(isset($_POST['lang']) && trim($_POST['lang']) != "") {
    /*
    * write posted value to settings file
    */
    file_put_contents($conf['settings_abs'].'/Lang', trim($_POST['lang']));
    $conf['settings_lang'] = trim($_POST['lang']);
}

/*
* Lang files default (the complete set)
*/
include("lang/lang-en-UK.php");
$langDef = $lang;
/*
* see if we load a sepcific language file
*/
if(
    isset($conf['settings_lang'])
    && $conf['settings_lang'] != ""
    && $conf['settings_lang'] != "en-UK"
    && file_exists('lang/lang-'.$conf['settings_lang'].'.php')
    ) {
    include('lang/lang-'.$conf['settings_lang'].'.php');
    $langCustom = $lang;
}
/*
* create language from default and language file
* if language file does not have the string, use default string
*/
$lang = array();
foreach($langDef as $langKey => $langVal) {
    if(isset($langCustom[$langKey])) {
        $lang[$langKey] = $langCustom[$langKey];
    } else {
        $lang[$langKey] = $langDef[$langKey];
    }
}

/**
foreach($lang as $key => $value) {
    $lang[$key] = "#NEW#".$value;
}
/**/
?>