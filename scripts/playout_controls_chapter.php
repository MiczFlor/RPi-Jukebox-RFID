<?php
ini_set('display_errors', 'on');
error_reporting(E_ALL);

use M4bTool\Executables\Mp4chaps;
use Sandreas\Time\TimeUnit;

$inputCommand = $argv[1] ?? "";
$inputValue = $argv[2] ?? "";
$inputChaptersFile = new SplFileInfo($argv[3] ?? "");
$inputElapsedTime = $argv[4] ?? "0";

$m4btoolPhar = realpath(__DIR__ . "/m4b-tool.phar");
if (!$m4btoolPhar) {
    echo $inputCommand . ";" . $inputValue;
    exit;
}
require_once "phar://" . $m4btoolPhar . "/vendor/autoload.php";

if (!in_array($inputCommand, ["playernext", "playerprev"]) || !$inputChaptersFile->isFile() || $inputChaptersFile->getSize() === 0) {
    echo $inputCommand . ";" . $inputValue;
    exit;
}
$inputElapsedTimeUnit = new TimeUnit((float)$inputElapsedTime, TimeUnit::SECOND);

$mp4chaps = new Mp4chaps();
$chapters = $mp4chaps->parseChaptersTxt(file_get_contents($inputChaptersFile));

// prev button skips to previous chapter within 5 seconds from start of current chapter
const PREV_TOLERANCE_MILLISECONDS = 5000;

$firstChapter = reset($chapters);
$lastChapter = end($chapters);

$prevChapter = $firstChapter;
$nextChapter = $lastChapter;

if ($inputElapsedTimeUnit->milliseconds() > $nextChapter->getEnd()->milliseconds() && $inputCommand === "playernext") {
    echo $inputCommand . ";" . $inputValue;
    exit;
}

foreach ($chapters as $chapter) {
    if ($chapter->getStart()->milliseconds() < $inputElapsedTimeUnit->milliseconds() - PREV_TOLERANCE_MILLISECONDS && $chapter->getStart()->milliseconds() >= $prevChapter->getEnd()->milliseconds()) {
        $prevChapter = $chapter;
    } else if ($chapter->getStart()->milliseconds() > $inputElapsedTimeUnit->milliseconds() && $chapter->getEnd()->milliseconds() < $nextChapter->getStart()->milliseconds()) {
        $nextChapter = $chapter;
        break;
    }
}

if ($inputCommand === "playerprev" && $prevChapter !== $firstChapter) {
    echo "playerseek;" . round($prevChapter->getStart()->milliseconds() / 1000, 3);
    exit;
}

if ($inputCommand === "playernext" && $nextChapter !== $lastChapter) {
    echo "playerseek;" . round($nextChapter->getStart()->milliseconds() / 1000, 3);
    exit;
}

echo $inputCommand . ";" . $inputValue;

