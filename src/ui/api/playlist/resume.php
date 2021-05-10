<?php
namespace JukeBox\Api;

/**
 * Enables or disabled resume for a playlist.
 */
include('../common.php');

/*
* debug? Conf file line:
* DEBUG_WebApp_API="TRUE"
*/
$debugLoggingConf = parse_ini_file("../../../settings/debugLogging.conf");
if($debugLoggingConf['DEBUG_WebApp_API'] == "TRUE") {
    file_put_contents("../../../logs/debug.log", "\n# WebApp API # " . __FILE__ , FILE_APPEND | LOCK_EX);
    file_put_contents("../../../logs/debug.log", "\n  # \$_SERVER['REQUEST_METHOD']: " . $_SERVER['REQUEST_METHOD'] , FILE_APPEND | LOCK_EX);
}

if ($_SERVER['REQUEST_METHOD'] === 'PUT') {
    $body = file_get_contents('php://input');
    $json = json_decode(trim($body), TRUE);
    if($debugLoggingConf['DEBUG_WebApp_API'] == "TRUE") {
        file_put_contents("../../../logs/debug.log", "\n# WebApp API # " . __FILE__ , FILE_APPEND | LOCK_EX);
    }
    if (validateRequest($json)) {
        $playlist = $json['playlist'];
        $resume = $json['resume'];
        if($debugLoggingConf['DEBUG_WebApp_API'] == "TRUE") {
            file_put_contents("../../../logs/debug.log", "\n  # attempting to toggle resume: playlist (".$json['playlist'].") and resume (".$json['resume'].")" , FILE_APPEND | LOCK_EX);
        }
        if ($resume === 'true') {
            if($debugLoggingConf['DEBUG_WebApp_API'] == "TRUE") {
                file_put_contents("../../../logs/debug.log", "\n  # attempting enableresume '$playlist'" , FILE_APPEND | LOCK_EX);
            }
            execScript("resume_play.sh -c=enableresume -d='{$playlist}'");
        } else {
            if($debugLoggingConf['DEBUG_WebApp_API'] == "TRUE") {
                file_put_contents("../../../logs/debug.log", "\n  # attempting disableresume '$playlist'" , FILE_APPEND | LOCK_EX);
            }
            execScript("resume_play.sh -c=disableresume -d='{$playlist}'");
        }
    }
} else {
    http_response_code(405);
}


function validateRequest($json) {
    global $debugLoggingConf;
    $tempDebug = "attributes playlist (".$json['playlist'].") and resume (".$json['resume'].")";
    if ($json['playlist'] == null) {
        http_response_code(400);
        echo "playlist attribute missing";
        return false;
    } else if ($json['resume'] == null) {
        http_response_code(400);
        echo "resume attribute missing";
        return false;
    } else {
        if($debugLoggingConf['DEBUG_WebApp_API'] == "TRUE") {
            file_put_contents("../../../logs/debug.log", "\n  # function validateRequest: " . $tempDebug , FILE_APPEND | LOCK_EX);
        }
    }
    return true;
}

?>
