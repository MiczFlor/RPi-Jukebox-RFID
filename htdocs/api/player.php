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
$globalConf = parse_ini_file("../../settings/global.conf");

if ($debugLoggingConf['DEBUG_WebApp_API'] == "TRUE") {
    file_put_contents("../../logs/debug.log", "\n# WebApp API # " . __FILE__, FILE_APPEND | LOCK_EX);
    file_put_contents("../../logs/debug.log", "\n  # \$_SERVER['REQUEST_METHOD']: " . $_SERVER['REQUEST_METHOD'], FILE_APPEND | LOCK_EX);
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
    if ($debugLoggingConf['DEBUG_WebApp_API'] == "TRUE") {
        file_put_contents("../../logs/debug.log", "\n  # function handlePut() ", FILE_APPEND | LOCK_EX);
    }

    $body = file_get_contents('php://input');
    $json = json_decode(trim($body), TRUE);
    if ($debugLoggingConf['DEBUG_WebApp_API'] == "TRUE") {
        file_put_contents("../../logs/debug.log", "\n  # \$json['command']:" . $json['command'], FILE_APPEND | LOCK_EX);
    }
    $inputCommand = $json['command'];
    $inputValue = $json['value'] ?? "";
    if ($inputCommand != null) {
        $controlsCommand = determineCommand($inputCommand);
        $controlsValue = $inputValue !== "" ? " -v=" . ((float)$inputValue) : "";
        $execCommand = "playout_controls.sh {$controlsCommand}{$controlsValue}";
        execScript($execCommand);
    } else {
        echo "Body is missing command";
        http_response_code(400);
    }
}

function handleGet() {
    global $debugLoggingConf;
    global $globalConf;    
    $statusCommand = "status\ncurrentsong\nclose";
    $commandResponseList = execMPDCommand($statusCommand);
    $responseList = array();
    forEach ($commandResponseList as $commandResponse) {
        preg_match("/(?P<key>.+?): (?P<value>.*)/", $commandResponse, $match);
        if ($match) {
            $responseList[strtolower($match['key'])] = $match['value'];
        }
    }
    
    // get volume separately from mpd, because we might use amixer to control volume
    if ($globalConf['VOLUMEMANAGER'] != "mpd"){
        $command = "playout_controls.sh -c=getvolume";
        $output = execScript($command);
        $responseList['volume'] = implode('\n', $output);
    }

    // get chapter info if file extension indicates supports
    $fileExtension = pathinfo ( $responseList['file'], PATHINFO_EXTENSION);         
    if (in_array($fileExtension, explode(',', $globalConf['CHAPTEREXTENSIONS']))) {
        $command = "playout_controls.sh -c=getchapters";
        $output = execScript($command);
        $jsonChapters = trim(implode("\n", $output));
        $chapters = @json_decode($jsonChapters, true);           
    }
    
 
    $currentChapterIndex = null;
    $mappedChapters = array_filter(array_map(function($chapter) use($responseList, &$currentChapterIndex) {
        static $i = 1;
        if(isset($chapter["start_time"], $chapter["end_time"])) {
            $start = (double)$chapter["start_time"];
            $end = (double)$chapter["end_time"];

            return [
                "name" => $chapter["tags"]["title"] ?? $i++,
                "start" => round($start, 3),
                "length" => round($end - $start, 3)
            ];
        }
        return null;
    }, $chapters["chapters"] ?? []));

    $responseList['chapters'] = $mappedChapters;

    if ($debugLoggingConf['DEBUG_WebApp_API'] == "TRUE") {
        file_put_contents("../../logs/debug.log", "\n  # function handleGet() ", FILE_APPEND | LOCK_EX);
        file_put_contents("../../logs/debug.log", "\n\$responseList: " . json_encode($responseList) . $_SERVER['REQUEST_METHOD'], FILE_APPEND | LOCK_EX);
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
        case 'seekPosition':
            return '-c=playerseek';
        case 'stop':
            return '-c=playerstop';
        case 'mute':
            return '-c=mute';
        case 'volumeup':
            return '-c=volumeup';
        case 'volumedown':
            return '-c=volumedown';
    }
    echo "Unknown command {$body}";
    http_response_code(400);
    exit;
}

?>
