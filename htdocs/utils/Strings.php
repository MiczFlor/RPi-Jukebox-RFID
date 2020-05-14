<?php
namespace JukeBox\Utils;

/**
 * Util class containing String functions
 * @package JukeBox\Utils
 */
class Strings {

    /**
     * Check if the ...
     * @param   string  $haystack      contains the ...
     * @param   string  $needle        and
     * @return  bool                   return true if found
     */
    public static function startsWith($haystack, $needle) {

        $length = strlen($needle);
        return (substr($haystack, 0, $length) === $needle);
    }
}