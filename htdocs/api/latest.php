<?php
namespace JukeBox\Api;

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
