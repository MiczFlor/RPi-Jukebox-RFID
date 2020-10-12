<?php
namespace JukeBox\Api;

/**
 * Moves a song within the current playlist down.
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
    if($debugLoggingConf['DEBUG_WebApp_API'] == "TRUE") {
        file_put_contents("../../../logs/debug.log", "\n  # \$body: " . $body , FILE_APPEND | LOCK_EX);
    }
    if (is_numeric($body)) {
        // This script always returns with returncode 1, so we cannot check that the returncode is 0
        execScriptWithoutCheck("playout_controls.sh -c=playermovedown -v='{$body}'");
    } else {
        http_response_code(400);
    }
} else {
    http_response_code(405);
}

?>
