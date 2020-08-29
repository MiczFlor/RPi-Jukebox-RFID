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


echo implode(";", rewriteCommandValueIfRequired($argv));

function rewriteCommandValueIfRequired($scriptArguments)
{
    $command = $scriptArguments[1] ?? "";
    $value = $scriptArguments[2] ?? "";
    $chaptersFile = new SplFileInfo($scriptArguments[3] ?? "");
    $elapsedTime = $scriptArguments[4] ?? "0";

    $originalCommandValue = [$command, $value];

    if (!includeM4bToolAutoload() || !shouldRewriteCommand($command, $chaptersFile)) {
        return $originalCommandValue;
    }

    $chapters = parseChapters($chaptersFile);
    $elapsedTimeUnit = new TimeUnit((float)$elapsedTime, TimeUnit::SECOND);

    if (isLastChapterAlreadyPlaying($chapters, $elapsedTimeUnit, $command)) {
        return $originalCommandValue;
    }


    list($prevChapter, $nextChapter) = findPrevAndNextChapter($chapters, $elapsedTimeUnit);

    if ($command === COMMAND_PLAYER_PREV && $prevChapter !== null) {
        return rewriteCommand($prevChapter);
    }

    if ($command === COMMAND_PLAYER_NEXT && $nextChapter !== null) {
        return rewriteCommand($nextChapter);
    }

    return [$command, $value];
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
    return in_array($command, [COMMAND_PLAYER_NEXT, COMMAND_PLAYER_PREV]) && $chaptersFile->isFile() && $chaptersFile->getSize() > 0;
}

function parseChapters(SplFileInfo $chaptersFile)
{
    $mp4chaps = new Mp4chaps();
    return $mp4chaps->parseChaptersTxt(file_get_contents($chaptersFile));
}

function isLastChapterAlreadyPlaying($chapters, TimeUnit $elapsedTimeUnit, $command)
{
    if ($command !== COMMAND_PLAYER_NEXT) {
        return false;
    }
    $lastChapter = end($chapters);
    return $elapsedTimeUnit->milliseconds() > $lastChapter->getEnd()->milliseconds();
}


function findPrevAndNextChapter($chapters, TimeUnit $inputElapsedTimeUnit)
{
    $prevChapter = null;
    $nextChapter = null;

    foreach ($chapters as $chapter) {
        if (isChapterBetterMatchForPrevChapter($chapter, $prevChapter, $inputElapsedTimeUnit)) {
            $prevChapter = $chapter;
        } else if (isChapterBetterMatchForNextChapter($chapter, $nextChapter, $inputElapsedTimeUnit)) {
            $nextChapter = $chapter;
            // if we found a better match next chapter, we can stop searching
            break;
        }
    }
    return [$prevChapter, $nextChapter];
}

function isChapterBetterMatchForPrevChapter(Chapter $chapter, Chapter $prevChapter = null, TimeUnit $inputElapsedTimeUnit = null)
{
    return $chapter->getStart()->milliseconds() < $inputElapsedTimeUnit->milliseconds() - PREV_TOLERANCE_MILLISECONDS && ($prevChapter === null || $chapter->getStart()->milliseconds() >= $prevChapter->getEnd()->milliseconds());
}

function isChapterBetterMatchForNextChapter(Chapter $chapter, Chapter $nextChapter = null, TimeUnit $inputElapsedTimeUnit = null)
{
    return $chapter->getStart()->milliseconds() > $inputElapsedTimeUnit->milliseconds() && ($nextChapter === null || $chapter->getEnd()->milliseconds() < $nextChapter->getStart()->milliseconds());
}


function rewriteCommand(Chapter $chapter)
{
    return [COMMAND_PLAYER_SEEK, round($chapter->getStart()->milliseconds() / 1000, 3)];
}



