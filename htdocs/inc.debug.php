<?php

function validateInput($input) {
    // Ensure the input only contains valid characters
    return preg_match('/^[a-zA-Z0-9_\-\/\.]+$/', $input);
}

function sanitizeInput($input) {
    // Remove any potentially harmful characters from the input
    return htmlspecialchars($input, ENT_QUOTES, 'UTF-8');
}

foreach ($_GET as $key => $value) {
    if (!validateInput($value)) {
        die("Invalid input detected.");
    }
    $_GET[$key] = sanitizeInput($value);
}

foreach ($_POST as $key => $value) {
    if (!validateInput($value)) {
        die("Invalid input detected.");
    }
    $_POST[$key] = sanitizeInput($value);
}

phpinfo();

?>
