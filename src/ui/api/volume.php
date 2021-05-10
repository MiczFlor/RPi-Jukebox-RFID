<?php
namespace JukeBox\Api;

require_once("PhonieboxRpcClient.php");

/**
 * Retrieves and sets the volume.
 */
include 'common.php';

/*
* debug? Conf file line:
* DEBUG_WebApp_API="TRUE"
*/
$debugLoggingConf = parse_ini_file("../../settings/debugLogging.conf");
if($debugLoggingConf['DEBUG_WebApp_API'] == "TRUE") {
    file_put_contents("../../logs/debug.log", "\n# WebApp API api/volume.php# " . __FILE__ , FILE_APPEND | LOCK_EX);
    file_put_contents("../../logs/debug.log", "\n  # \$_SERVER['REQUEST_METHOD']: " . $_SERVER['REQUEST_METHOD'] , FILE_APPEND | LOCK_EX);
}

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $json_response = PhonieboxRpcEnquene(array('object'=>'volume','method'=>'get'));
    echo json_decode ( $json_response,true)['resp']['volume'];
} else if ($_SERVER['REQUEST_METHOD'] === 'PUT') {
    $body = file_get_contents('php://input');
    if (is_numeric($body)) {
        echo $body;
        PhonieboxRpcEnquene(array('object'=>'volume','method'=>'set','params'=>array('volume'=>(int)$body)));
    } else {
        http_response_code(400);
    }
} else {
    http_response_code(405);
}

?>
