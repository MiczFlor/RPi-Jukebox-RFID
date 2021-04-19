<?php
namespace JukeBox\Api;

require_once("PhonieboxRpcClient.php");

/*
* debug? Conf file line:
* DEBUG_WebApp_API="TRUE"
*/
$debugLoggingConf = parse_ini_file("../../settings/debugLogging.conf");
if($debugLoggingConf['DEBUG_WebApp_API'] == "TRUE") {
    file_put_contents("../../logs/debug.log", "\n# WebApp API # " . __FILE__ , FILE_APPEND | LOCK_EX);
    file_put_contents("../../logs/debug.log", "\n  # \$_SERVER['REQUEST_METHOD']: " . $_SERVER['REQUEST_METHOD'] , FILE_APPEND | LOCK_EX);
}

/***
 * Starts to play a playlist for a put request.
 * Retrieves information about a playlist for a GET request.
 */
include 'common.php';

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    handleGet();
} else if ($_SERVER['REQUEST_METHOD'] === 'PUT') {
    handlePut();
} else {
    http_response_code(405);
}

function handleGet() {
    $playlist_json = PhonieboxRpcEnquene(array('object'=>'player','method'=>'playlistinfo','param'=>''));
    $playList = array("tracks" => json_decode ( $playlist_json,true)['resp']);

    /* sample array, uncomment for checking frontend *
    $playList = array(
        "tracks" => array(
            "0" => array(
                "pos" => "0",
                "title" => "Title Track 0",
                "artist" => "Artist Name",
                "album" => "Album Name"
            ),
            "1" => array(
                "pos" => "1",
                "file" => "File 1 Name.mp3"
            ),
            "2" => array(
                "pos" => "2",
                "title" => "Title Track 2",
                "artist" => "Artist Name",
                "album" => "Album Name"
            ),
        ),
    );
    /**/

    //    file_put_contents("../../logs/debug.log", "\n  # \$playlistINFO:" . print_R($playList,true) , FILE_APPEND | LOCK_EX);

    header('Content-Type: application/json');
    echo json_encode($playList);
}

function handlePut() {
    global $debugLoggingConf;
    if($debugLoggingConf['DEBUG_WebApp_API'] == "TRUE") {
        file_put_contents("../../logs/debug.log", "\n  # function handlePut() " , FILE_APPEND | LOCK_EX);
    }
    $body = file_get_contents('php://input');
    $json = json_decode(trim($body), TRUE);

    http_response_code(400);
    echo "Not yet implemented";

    /*
    if (validateRequest($json)) {
        $playlist = $json['playlist'];
        if($debugLoggingConf['DEBUG_WebApp_API'] == "TRUE") {
            file_put_contents("../../logs/debug.log", "\n  # \$playlist:" . $playlist , FILE_APPEND | LOCK_EX);
        }
        if($json['recursive'] === "true") {
            execScript("rfid_trigger_play.sh -d='{$playlist}' -v='recursive'");
        } else {
            execScript("rfid_trigger_play.sh -d='{$playlist}'");
        }
    }
    */
}

function validateRequest($json) {
    if ($json['playlist'] == null) {
        http_response_code(400);
        echo "playlist attribute missing";
        return false;
    } else if ($json['recursive'] == null) {
        http_response_code(400);
        echo "recursive attribute missing";
        return false;
    }
    return true;
}

?>
