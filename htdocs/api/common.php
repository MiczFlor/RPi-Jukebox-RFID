<?php
namespace JukeBox\Api;

function execScript($command) {
    $absoluteCommand = realpath(dirname(__FILE__) .'/../../scripts') ."/{$command}";
    return execSuccessfully($absoluteCommand);
}

function execSuccessfully($command) {    
    global $debugLoggingConf;
    if($debugLoggingConf['DEBUG_WebApp_API'] == "TRUE") {
        file_put_contents("../../logs/debug.log", "\n  # function execSuccessfully: " . $command , FILE_APPEND | LOCK_EX);
    }

    exec("sudo ".$command, $output, $rc);
    if ($rc != 0) {
        $formattedOutput = implode('\n', $output);
        echo "Execution failed\nCommand: {$command}\nOutput: {$formattedOutput}\nRC: .${rc}";
        http_response_code(500);
        exit();
    }  
    return $output;
}

?>
