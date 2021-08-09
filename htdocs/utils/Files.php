<?php
namespace JukeBox\Utils;

/**
 * Util class containing File functions
 * @package JukeBox\Utils
 */
class Files {

    /**
     * Build path depending on the system directory separator
     * @param   string  $pieces     the file pieces
     * @return  string              the filepath
     */
    public static function buildPath(...$pieces) {
        return implode(DIRECTORY_SEPARATOR, $pieces);
    }
}