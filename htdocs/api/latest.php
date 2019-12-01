<?php
namespace JukeBox\Api;

/*
* debug? Conf file line:
* DEBUG_WebApp_API="TRUE"
*/
$debugLoggingConf = parse_ini_file("../../settings/debugLogging.conf");
if($debugLoggingConf['DEBUG_WebApp_API'] == "TRUE") {
    file_put_contents("../../logs/debug.log", "\n# WebApp API # " . __FILE__ , FILE_APPEND | LOCK_EX);
    file_put_contents("../../logs/debug.log", "\n  # \$_SERVER['REQUEST_METHOD']: " . $_SERVER['REQUEST_METHOD'] , FILE_APPEND | LOCK_EX);
}

/**
 * Returns the latest played file, folder and playlist.
 */

$result = array();
$result['folder'] = trim(file_get_contents('../../settings/Latest_Folder_Played'));
$result['file'] = trim(file_get_contents('../../settings/Latest_Played_File'));
$result['playlist'] = trim(file_get_contents('../../settings/Latest_Playlist_Played'));
echo json_encode($result, JSON_PRETTY_PRINT);

header('Content-Type: application/json');
?>
