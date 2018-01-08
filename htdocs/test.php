<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<title>PHP Test</title>
</head>
<body>
<pre>

<?php

if(file_exists("config.php")) {
    include("config.php");
    print "File 'config.php' found and included.\n";
} else {
    print "File 'config.php' not found.\n";
}

$conf['url_abs']    = "http://".$_SERVER['HTTP_HOST'].$_SERVER['PHP_SELF']; // URL to PHP_SELF

print "\nVariable \$conf['url_abs'] = ".$conf['url_abs']."\n";

print "\n\$conf array:\n";
print_r($conf); print "\n";

if(file_exists("func.php")) {
    include("func.php");
    print "\nFile 'func.php' found and included.\n";
} else {
    print "\nFile 'func.php' not found.\n";
}

if (function_exists('html_bootstrap3_createHeader')) {
    echo "\nFunction 'html_bootstrap3_createHeader' exists.\n";
} else {
    echo "\nFunction 'html_bootstrap3_createHeader' does not exist.\n";
}

print "\nCalling 'html_bootstrap3_createHeader(\"en\",\"RPi Jukebox\",".$conf['base_url'].");'\n";

if(file_exists("page_home.php")) {
    print "\nFile 'page_home.php' found.\n";
} else {
    print "\nFile 'page_home.php' not found.\n";
}

if(file_exists($conf['base_path']."/shared/shortcuts/")) {
    print "\nFolder '".$conf['base_path']."/shared/shortcuts/' found.\n";
} else {
    print "\nFolder '".$conf['base_path']."/shared/shortcuts/' not found.\n";
}

// read the shortcuts used
$shortcutstemp = array_filter(glob($conf['base_path'].'/shared/shortcuts/*'), 'is_file');
$shortcuts = array(); // the array with pairs of ID => foldername
// read files' content into array
foreach ($shortcutstemp as $shortcuttemp) {
    $shortcuts[basename($shortcuttemp)] = trim(file_get_contents($shortcuttemp));
}
print "\nShortcuts temporary file:\n";
print_r($shortcutstemp); print "\n";
print "\nShortcuts resolved file:\n";
print_r($shortcuts); print "\n";


if(file_exists($conf['base_path']."/shared/audiofolders/")) {
    print "\nFolder '".$conf['base_path']."/shared/audiofolders/' found.\n";
} else {
    print "\nFolder '".$conf['base_path']."/shared/audiofolders/' not found.\n";
}

// read the subfolders of shared/audiofolders
$audiofolders = array_filter(glob($conf['base_path'].'/shared/audiofolders/*'), 'is_dir');
print "\nAudio folders:\n";
print "<pre>"; print_r($audiofolders); print "\n";

?>
</pre>


</body>
</html>
