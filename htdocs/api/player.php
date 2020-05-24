<?php
namespace JukeBox\Api;

/***
 * Allows to control the player by sending a command via PUT like 'play' or 'pause'.
 * Retrieves information about the player by sending a GET request.
 */
include 'common.php';

/*
* debug? Conf file line:
* DEBUG_WebApp_API="TRUE"
*/
$debugLoggingConf = parse_ini_file("../../settings/debugLogging.conf");

if($debugLoggingConf['DEBUG_WebApp_API'] == "TRUE") {
    file_put_contents("../../logs/debug.log", "\n# WebApp API # " . __FILE__ , FILE_APPEND | LOCK_EX);
    file_put_contents("../../logs/debug.log", "\n  # \$_SERVER['REQUEST_METHOD']: " . $_SERVER['REQUEST_METHOD'] , FILE_APPEND | LOCK_EX);
}
if ($_SERVER['REQUEST_METHOD'] === 'PUT') {
    handlePut();
} else if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    handleGet();
} else {
    http_response_code(405);
}

function handlePut() {
    global $debugLoggingConf;
    if($debugLoggingConf['DEBUG_WebApp_API'] == "TRUE") {
        file_put_contents("../../logs/debug.log", "\n  # function handlePut() " , FILE_APPEND | LOCK_EX);
    }

    $body = file_get_contents('php://input');
    $json = json_decode(trim($body), TRUE);
    if($debugLoggingConf['DEBUG_WebApp_API'] == "TRUE") {
        file_put_contents("../../logs/debug.log", "\n  # \$json['command']:".$json['command'] , FILE_APPEND | LOCK_EX);
    }
    $inputCommand = $json['command'];
    if ($inputCommand != null) {
        $controlsCommand = determineCommand($inputCommand);
        $execCommand = "playout_controls.sh {$controlsCommand}";
        execScript($execCommand);
    } else {
        echo "Body is missing command";
        http_response_code(400);
    }
}

function handleGet() {
    global $debugLoggingConf;
    $statusCommand   = "echo 'status\ncurrentsong\nclose' | nc -w 1 localhost 6600";
    $commandResponseList = execSuccessfully($statusCommand);
    $responseList = array();
    forEach($commandResponseList as $commandResponse) {
        preg_match("/(?P<key>.+?): (?P<value>.*)/", $commandResponse, $match);
        if ($match) {
            $responseList[strtolower($match['key'])] = $match['value'];
        }
    }
    if($debugLoggingConf['DEBUG_WebApp_API'] == "TRUE") {
        file_put_contents("../../logs/debug.log", "\n  # function handleGet() " , FILE_APPEND | LOCK_EX);
        file_put_contents("../../logs/debug.log", "\n\$responseList: " . json_encode($responseList) . $_SERVER['REQUEST_METHOD'] , FILE_APPEND | LOCK_EX);
    }

    header('Content-Type: application/json');
    echo json_encode($responseList);
}

function determineCommand($body) {
    switch ($body) {
        case 'play':
            return '-c=playerplay';
        case 'next':
            return '-c=playernext';
        case 'prev':
            return '-c=playerprev';
        case 'replay':
            return '-c=playerreplay -v=playlist';
        case 'pause':
            return '-c=playerpause -v=single';
        case 'repeat':
            //return '-c=playerprev -c=playerrepeat -v=playlist';
            return '-c=playerrepeat -v=playlist';
        case 'single':
            //return '-c=playerprev -c=playerrepeat -v=single';
            return '-c=playerrepeat -v=single';
        case 'repeatoff':
            //return '-c=playerprev -c=playerrepeat -v=off';
            return '-c=playerrepeat -v=off';
        case 'seekBack':
            //return '-c=playerprev -c=playerseek -v=-15';
            return '-c=playerseek -v=-15';
        case 'seekAhead':
            //return '-c=playerprev -c=playerseek -v=+15';
            return '-c=playerseek -v=+15';
        case 'stop':
            return '-c=playerstop';
        case 'mute':
            return'-c=mute';
        case 'volumeup':
            return'-c=volumeup';
        case 'volumedown':
            return'-c=volumedown';
    }
    echo "Unknown command {$body}";
    http_response_code(400);
    exit;
}

?>
