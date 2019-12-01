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
    $statusCommand = "echo 'playlistinfo\nclose' | nc -w 1 localhost 6600";
    $playListInfoResponse = execSuccessfully($statusCommand);
    $playList = array();
    $albumLength = 0;
    $track = array();
    forEach($playListInfoResponse as $index => $record ) {
        preg_match("/(?P<key>.+?): (?P<value>.*)/", $record, $match);
        if ($match) {
            $key = strtolower($match['key']);
            $value = $match['value'];
            if ("file" == $key) {
                if ($track && $track['file'] != $value) {
                    $playList['tracks'][] = $track;
                }
                $track = array();
                $track[$key] = $value;

            } else {
                $track[$key] = $value;
                $albumLength += ("time" == $key) ? $value : 0;
            }
        }
        if ($index == array_key_last($playListInfoResponse) && !empty($track)) {
            $playList['tracks'][] = $track;
            $playList['albumLength'] = $albumLength;
        }
    }


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
