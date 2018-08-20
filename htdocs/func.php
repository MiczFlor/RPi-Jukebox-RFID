<?php

/*******************************************
* FUNCTIONS
*******************************************/

function html_bootstrap3_createHeader($lang="en",$title="Welcome",$url_absolute="") {
    /*
    * HTML for the header and body tag
    */
    print "<!DOCTYPE html>
<html lang=\"".$lang."\">
    <head>
        <meta charset=\"utf-8\">
        <meta http-equiv=\"X-UA-Compatible\" content=\"IE=edge\">
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
        <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
        
        <title>".$title."</title>
        
        <!-- Latest compiled and minified CSS -->
        <link rel=\"stylesheet\" href=\"".$url_absolute."_assets/bootstrap-3/css/bootstrap.cosmo.css\">
        <link rel=\"stylesheet\" href=\"".$url_absolute."_assets/css/circle.css\">
        
        <!-- Latest compiled and minified JavaScript -->
        <script src=\"".$url_absolute."_assets/js/jquery.1.12.4.min.js\"></script>
        <script src=\"".$url_absolute."_assets/bootstrap-3/js/bootstrap.min.js\"></script>
        <script src=\"".$url_absolute."_assets/bootstrap-3/js/collapse.js\"></script>
        <script src=\"".$url_absolute."_assets/bootstrap-3/js/transition.js\"></script>

        <link rel='stylesheet' href='".$url_absolute."_assets/font-awesome/css/font-awesome.min.css'>
        
        <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
        <!--[if lt IE 9]>
            <script src=\"".$url_absolute."_assets/bootstrap-3/js/html5shiv3.7.2.min.js\"></script>
            <script src=\"".$url_absolute."_assets/bootstrap-3/js/respond1.4.2.min.js\"></script>
        <![endif]-->
        
        <link rel=\"apple-touch-icon\" sizes=\"57x57\" href=\"".$url_absolute."_assets/icons/apple-icon-57x57.png\">
        <link rel=\"apple-touch-icon\" sizes=\"60x60\" href=\"".$url_absolute."_assets/icons/apple-icon-60x60.png\">
        <link rel=\"apple-touch-icon\" sizes=\"72x72\" href=\"".$url_absolute."_assets/icons/apple-icon-72x72.png\">
        <link rel=\"apple-touch-icon\" sizes=\"76x76\" href=\"".$url_absolute."_assets/icons/apple-icon-76x76.png\">
        <link rel=\"apple-touch-icon\" sizes=\"114x114\" href=\"".$url_absolute."_assets/icons/apple-icon-114x114.png\">
        <link rel=\"apple-touch-icon\" sizes=\"120x120\" href=\"".$url_absolute."_assets/icons/apple-icon-120x120.png\">
        <link rel=\"apple-touch-icon\" sizes=\"144x144\" href=\"".$url_absolute."_assets/icons/apple-icon-144x144.png\">
        <link rel=\"apple-touch-icon\" sizes=\"152x152\" href=\"".$url_absolute."_assets/icons/apple-icon-152x152.png\">
        <link rel=\"apple-touch-icon\" sizes=\"180x180\" href=\"".$url_absolute."_assets/icons/apple-icon-180x180.png\">
        <link rel=\"icon\" type=\"image/png\" sizes=\"192x192\"  href=\"".$url_absolute."_assets/icons/android-icon-192x192.png\">
        <link rel=\"icon\" type=\"image/png\" sizes=\"32x32\" href=\"".$url_absolute."_assets/icons/favicon-32x32.png\">
        <link rel=\"icon\" type=\"image/png\" sizes=\"96x96\" href=\"".$url_absolute."_assets/icons/favicon-96x96.png\">
        <link rel=\"icon\" type=\"image/png\" sizes=\"16x16\" href=\"".$url_absolute."_assets/icons/favicon-16x16.png\">
        <link rel=\"manifest\" href=\"".$url_absolute."_assets/icons/manifest.json\">
        <meta name=\"msapplication-TileColor\" content=\"#ffffff\">
        <meta name=\"msapplication-TileImage\" content=\"".$url_absolute."_assets/icons/ms-icon-144x144.png\">
        <meta name=\"theme-color\" content=\"#ffffff\">

        <style type='text/css'>
        .playerControls {
            margin-bottom: 1em;
        }
        .controlPlayer {
            margin-right: 1em;
        }
        .btnFolder, .folderContent {
            max-width: 100%;
            overflow: hidden;
        }
        .btn-player-xl {
            padding:4px 10px;
            font-size:38px;
            line-height:1;
            border-radius:6px;
        }
        .btn-player-l {
            padding:0px 16px;
            font-size:30px;
            line-height:1;
            border-radius:6px;
        }
        .btn-player-m {
            padding:15px 16px;
            font-size:18px;
            line-height:1;
            border-radius:6px;
        }
        .btn-player-s {
            padding:15px 5px;
            font-size:11px;
            line-height:1;
            border-radius:6px;
        }
        .playerWrapper {
            display: block!important;
            clear: both;
            height: auto;
            margin: 0 auto;
            text-align: center;
            margin-top: 1em;
            color: ;
        }
        .playerWrapper a {
            color: #456!important;
        }
        .playerWrapper a:hover {
            color: black!important;
        }
        .playerWrapperCover img {
            max-height: 200px;
        }
        .table td.text {
            max-width: 100px;
        }
        .table td.text span {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            display: inline-block;
            max-width: 100%;
        }
        </style>
        
    </head>\n";
}

function startsWith($haystack, $needle)
{
     $length = strlen($needle);
     return (substr($haystack, 0, $length) === $needle);
}

function replaceUmlaute($string) {
    $searchreplace = array(
        "/Ä/" => "Ae",
        "/Ö/" => "Oe",
        "/Ü/" => "Ue",
        "/ä/" => "ae",
        "/ö/" => "oe",
        "/ü/" => "ue",
        "/ß/" => "ss",
    );
    $search = array_keys($searchreplace);
    $replace = array_values($searchreplace);
    return(preg_replace($search, $replace, $string));
}
?>
