<?php
namespace JukeBox\Api;

include ("zmq.php");

/***
 * Allows to control the player by sending a command via PUT like 'play' or 'pause'.
 * Retrieves information about the player by sending a GET request.
 */
include 'common.php';

$command_map = array(        
        'play'=>['player','play',''],
        'next'=>['player','next',''],
        'prev'=>['player','prev',''],
        'replay'=>'-c=playerreplay -v=playlist',
        'pause'=> ['player','pause',''],
        'repeat'=>'-c=playerrepeat -v=playlist',
        'single'=> 'playerrepeat -v=single',
        'repeatoff'=>'playerrepeat -v=off',
        'seekBack'=> ['player','seek',['time' => '-15']],
        'seekAhead'=> ['player','seek',['time' => '+15']],
        'seekPosition' => 'playerseek',
        'stop'=>['player','stop',''],
        'mute'=> ['volume','mute',''],
        'volumeup'=> ['volume','inc',['step' => 5]],
        'volumedown'=> ['volume','dec',['step' => 5]],
);


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
    global $command_map;
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

        if (array_key_exists($inputCommand,$command_map)==True)
        {
            $cmd = $command_map[$inputCommand];
            $response = phonie_enquene(array('object'=>$cmd[0],'method'=>$cmd[1],'params'=>$cmd[2]));
        }
        else
        {
            echo "Unknown command {$inputCommand}";
            http_response_code(400);
        }

    } else {
        echo "Body is missing command";
        http_response_code(400);
    }
}

function handleGet() {
    global $debugLoggingConf;
    global $globalConf;    

    $json_response = phonie_enquene(array('object'=>'player','method'=>'playerstatus','param'=>''));
    $responseList = json_decode ( $json_response,true)['resp'];

    //so solltes es aussehen:
    //$responseList: {"volume":"3","repeat":"0","random":"0","single":"0","consume":"0","partition":"default","playlist":"4","playlistlength":"14","mixrampdb":"0.000000","state":"play","song":"1","songid":"2","time":"282","elapsed":"1.329","bitrate":"128","duration":"282.064","audio":"44100:16:2","nextsong":"2","nextsongid":"3","file":"Billy Idol\/Billy Idol - Cradle Of Love.mp3","last-modified":"2021-01-02T21:04:29Z","pos":"1","id":"2","chapters":[]}GET

    // get chapter info if file extension indicates supports
    /*$fileExtension = pathinfo ( $responseList['file'], PATHINFO_EXTENSION);         
    if (in_array($fileExtension, explode(',', $globalConf['CHAPTEREXTENSIONS']))) {
        $command = "playout_controls.sh -c=getchapters";
        #$output = execScript($command);
        $jsonChapters = trim(implode("\n", $output));
        $chapters = @json_decode($jsonChapters, true);           
    }*/
    
    /*
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
    */

    if ($debugLoggingConf['DEBUG_WebApp_API'] == "TRUE") {
        file_put_contents("../../logs/debug.log", "\n  # function handleGet() ", FILE_APPEND | LOCK_EX);
        file_put_contents("../../logs/debug.log", "\n\$responseList: " . json_encode($responseList) . $_SERVER['REQUEST_METHOD'], FILE_APPEND | LOCK_EX);
    }

    header('Content-Type: application/json');
    echo json_encode($responseList);
}







?>
