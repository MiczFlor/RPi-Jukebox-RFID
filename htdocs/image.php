<?php
  header('Content-Type: image/jpg');
  readfile($_GET['img']);
?>