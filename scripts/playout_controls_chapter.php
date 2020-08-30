<?php
ini_set('display_errors', 'on');
error_reporting(E_ALL);

use M4bTool\Audio\Chapter;
use M4bTool\Executables\Mp4chaps;
use Sandreas\Time\TimeUnit;

// prev button skips to previous chapter within 5 seconds from start of current chapter
const PREV_TOLERANCE_MILLISECONDS = 5000;
const COMMAND_PLAYER_SEEK = "playerseek";
const COMMAND_PLAYER_NEXT = "playernext";
const COMMAND_PLAYER_PREV = "playerprev";
const SEMICOLON = ";";
const GREEK_QUESTION_MARK = ";";


echo implode(SEMICOLON, rewriteCommandValueIfRequired($argv));

function rewriteCommandValueIfRequired($scriptArguments)
{
    $command = $scriptArguments[1] ?? "";
    $value = $scriptArguments[2] ?? "";
    $chaptersFile = new SplFileInfo($scriptArguments[3] ?? "");
    $elapsedTime = $scriptArguments[4] ?? "0";

    $originalCommandValue = [$command, $value, ""];

    if (!includeM4bToolAutoload() || !shouldRewriteCommand($command, $chaptersFile)) {
        return $originalCommandValue;
    }

    $chapterObjects = parseChapters($chaptersFile);
    $elapsedTimeUnit = new TimeUnit((float)$elapsedTime, TimeUnit::SECOND);

    list($prevChapter, $currentChapter, $nextChapter) = findPrevAndNextChapterForCurrentPosition($chapterObjects, $elapsedTimeUnit);

    $chapters = buildChaptersForJson($chapterObjects, $currentChapter);

    $originalCommandValue[2] = json_encode($chapters);

    if ($command === COMMAND_PLAYER_PREV && ($prevChapter || $currentChapter)) {
        if (isChapterBetterMatchForPrevChapter($currentChapter, $prevChapter, $elapsedTimeUnit)) {
            return rewriteCommandSeek($currentChapter, $chapters);
        }
        return rewriteCommandSeek($prevChapter, $chapters);
    }

    if ($command === COMMAND_PLAYER_NEXT && $nextChapter !== null) {
        return rewriteCommandSeek($nextChapter, $chapters);
    }

    return $originalCommandValue;
}

function buildChaptersForJson($chapterObjects, Chapter $currentChapter)
{

    return array_map(function (Chapter $chapter) use ($currentChapter) {
        static $index = 0;
        if ($chapter === null) {
            return null;
        }
        return [
            "index" => $index++,
            "start" => $chapter->getStart()->milliseconds(),
            "length" => $chapter->getLength()->milliseconds(),
            // trick to keep the visual appearance of the chapter name if it contains a semicolon
            // is replacing it with the greek question mark, which is a different char but looks the same
            // this is done to prevent problems with the separator char ;
            "name" => str_replace(SEMICOLON, GREEK_QUESTION_MARK, $chapter->getName()),
            "current" => ($chapter === $currentChapter)
        ];
    }, array_values($chapterObjects));


}

function includeM4bToolAutoload()
{
    $m4btoolPhar = realpath(__DIR__ . "/m4b-tool.phar");
    if (!$m4btoolPhar) {
        return false;
    }
    require_once "phar://" . $m4btoolPhar . "/vendor/autoload.php";
    return true;
}

function shouldRewriteCommand($command, SplFileInfo $chaptersFile)
{
    return $chaptersFile->isFile() && $chaptersFile->getSize() > 0;
}

function parseChapters(SplFileInfo $chaptersFile)
{
    $mp4chaps = new Mp4chaps();
    return $mp4chaps->parseChaptersTxt(file_get_contents($chaptersFile));
}

// sudo /usr/bin/php /home/pi/RPi-Jukebox-RFID/scripts/playout_controls_chapter.php 'getchapterdetails' '' '/home/pi/RPi-Jukebox-RFID/shared/audiofolders/audiobooks/Kai Meyer/Wellenläufer/1 - Wellenläufer.chapters.txt' '528.230'

function findPrevAndNextChapterForCurrentPosition($chapterObjects, TimeUnit $inputElapsedTimeUnit)
{
    $prevChapter = null;
    $nextChapter = null;
    $currentChapter = null;

    // convert keys that contain start times in ms to real array integer index keys
    /** @var Chapter[] $chapterValues */
    $chapterValues = array_values($chapterObjects);
    foreach ($chapterValues as $key => $chapter) {
        if ($chapter->getStart()->milliseconds() <= $inputElapsedTimeUnit->milliseconds() && $chapter->getEnd()->milliseconds() >= $inputElapsedTimeUnit->milliseconds()) {
            $currentChapter = $chapter;
            $prevChapter = $chapterValues[$key - 1] ?? null;
            $nextChapter = $chapterValues[$key + 1] ?? null;
        }
        if ($chapter->getStart()->milliseconds() > $inputElapsedTimeUnit->milliseconds()) {
            break;
        }
    }
    return [$prevChapter, $currentChapter, $nextChapter];
}

function isChapterBetterMatchForPrevChapter(Chapter $chapter, Chapter $prevChapter = null, TimeUnit $inputElapsedTimeUnit = null)
{
    return $chapter->getStart()->milliseconds() < $inputElapsedTimeUnit->milliseconds() - PREV_TOLERANCE_MILLISECONDS && ($prevChapter === null || $chapter->getStart()->milliseconds() >= $prevChapter->getEnd()->milliseconds());
}


function rewriteCommandSeek(Chapter $chapter, $chapterDetails = [])
{
    $seekPosition = round($chapter->getStart()->milliseconds() / 1000, 3);

    return [COMMAND_PLAYER_SEEK, $seekPosition, json_encode($chapterDetails)];
}



