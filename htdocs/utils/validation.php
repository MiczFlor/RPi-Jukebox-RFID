<?php

function validateFilePath($filePath) {
    // Check if the file path is valid
    return preg_match('/^[a-zA-Z0-9_\-\/]+$/', $filePath);
}

function sanitizeInput($input) {
    // Remove any potentially harmful characters
    return htmlspecialchars($input, ENT_QUOTES, 'UTF-8');
}

?>
