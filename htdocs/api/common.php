<?php

function execAndEcho($command) {
    $output = execScript($command);
    echo(implode('\n', $output));
}

function execScript($command) {
    $absoluteCommand = realpath(dirname(__FILE__) .'/../../scripts') ."/{$command}";
    return execSuccessfully($absoluteCommand);
}

function execScriptWithoutCheck($command) {
    $absoluteCommand = realpath(dirname(__FILE__) .'/../../scripts') ."/{$command}";
    exec($absoluteCommand);
}

function execSuccessfully($command) {
    exec($command, $output, $rc);
    if ($rc != 0) {
        $formattedOutput = implode('\n', $output);
        echo "Execution failed\nCommand: {$command}\nOutput: {$formattedOutput}\nRC: .${rc}";
        http_response_code(500);
        exit();
    }
    return $output;
}

?>
