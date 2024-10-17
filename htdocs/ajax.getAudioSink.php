<?php

  // Returns a slighlty formatted string of "mpc outputs"
  // Give nice names to you audio sinks in mpd.conf: they will turn up here :-)

  function validateInput($input) {
    // Ensure the input only contains valid characters
    return preg_match('/^[a-zA-Z0-9_\-\/\.]+$/', $input);
  }

  function sanitizeInput($input) {
    // Remove any potentially harmful characters from the input
    return escapeshellcmd($input);
  }

  $btOutputs = nl2br(trim(shell_exec("mpc outputs")));
  $btOutputs = str_replace("enabled", "<b>enabled</b>", $btOutputs);
  $btOutputs = str_replace("disabled", "<b>disabled</b>", $btOutputs);
  print "$btOutputs"; 

?>
