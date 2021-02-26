<?php

  // Returns a slighlty formatted string of "mpc outputs"
  // Give nice names to you audio sinks in mpd.conf: they will turn up here :-)

  $btOutputs = nl2br(trim(shell_exec("mpc outputs")));
  $btOutputs = str_replace("enabled", "<b>enabled</b>", $btOutputs);
  $btOutputs = str_replace("disabled", "<b>disabled</b>", $btOutputs);
  print "$btOutputs"; 

?>
