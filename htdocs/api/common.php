<?php
namespace JukeBox\Api;

function execAndEcho($command) {
    $output = execScript($command);
    $result = implode('\n', $output); 
    echo $result;
    if($debugLoggingConf['DEBUG_WebApp_API'] == "TRUE") {
        file_put_contents("../../logs/debug.log", "\n  # function execAndEcho: " . $result , FILE_APPEND | LOCK_EX);
    }
}

function execScript($command) {
    $absoluteCommand = realpath(dirname(__FILE__) .'/../../scripts') ."/{$command}";
    return execSuccessfully($absoluteCommand);
}

function execScriptWithoutCheck($command) {
    // Access global configuration
    global $debugLoggingConf;

    // Validate the command to prevent command injection
    if (!preg_match('/^[a-zA-Z0-9_\-]+$/', $command)) {
        throw new InvalidArgumentException('Invalid command.');
    }

    // Debug logging
    if ($debugLoggingConf['DEBUG_WebApp_API'] === "TRUE") {
        $logMessage = "\n  # function execScriptWithoutCheck: " . $command;
        $logFilePath = __DIR__ . '/../../logs/debug.log';
        file_put_contents($logFilePath, $logMessage, FILE_APPEND | LOCK_EX);
    }

    // Construct the absolute path to the script
    $scriptDir = realpath(__DIR__ . '/../../scripts');
    $absoluteCommand = $scriptDir . '/' . escapeshellarg($command);

    // Execute the command using sudo
    exec("sudo " . $absoluteCommand);
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

function execMPDCommand($command) {    
    $socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
    $stream = socket_connect($socket,"localhost" ,6600);
    socket_write($socket, $command, strlen($command));
    socket_shutdown ($socket,1);
    $output = array();
    while ($out = socket_read($socket, 2048)) {
         $outputTemp .= $out;
    }
    $output = array_merge($output,explode("\n", $outputTemp));
    socket_close($socket);
    return $output;
}

?>
