<?php
namespace JukeBox\Api;

/**
 * Appends a given file to the current playlist (and starts playing)
 */
require_once("../zmq.php");

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
    $body = str_replace("'","'\''",file_get_contents('php://input'));
    if($debugLoggingConf['DEBUG_WebApp_API'] == "TRUE") {
        file_put_contents("../../../logs/debug.log", "\n  # \$body: " . $body , FILE_APPEND | LOCK_EX);
    }
    phonie_enquene(['object'=>'player','method'=>'playlistappend','param'=>['songid'=>$body ]]);
} else {
  $file = $_GET["file"];
  if ($file !== "") {
    print "Playing file " . $file;
    phonie_enquene(['object'=>'player','method'=>'playlistappend','param'=>['songid'=>$file ]]);

    require_once("../zmq.php");
  }else{
    http_response_code(405);
  }
}

?>
