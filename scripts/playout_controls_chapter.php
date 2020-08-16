<?php
$inputCommand = $argv[1];
$inputValue = $argv[2];
$inputChaptersFile = $argv[3];
$inputElapsedTime = $argv[4];

if(!in_array($inputCommand, ["playernext", "playerprev"]) || !file_exists($inputChaptersFile) || filesize($inputChaptersFile) === 0) {
    echo $inputCommand.";".$inputValue;
    exit;
}

$chapters = array_map(function($chaptertime) {return (float)$chaptertime;}, file($inputChaptersFile));
$elapsedTime = (float)$inputElapsedTime;

$prevToleranceSeconds = 5;
$prevChapter = reset($chapters);
$nextChapter = end($chapters);

if($inputElapsedTime > $nextChapter && $inputCommand === "playernext") {
    echo $inputCommand.";".$inputValue;
    exit;
}

foreach($chapters as $chapter) {
    if($chapter <= $elapsedTime - $prevToleranceSeconds && $chapter > $prevChapter) {
        $prevChapter = $chapter;
    } else if($chapter >= $elapsedTime && $chapter < $nextChapter) {
        $nextChapter = $chapter;
        break;
    }
}


if($inputCommand === "playerprev") {
    echo "playerseek;".($prevChapter);
    exit;
}

if($inputCommand === "playernext") {
    echo "playerseek;".($nextChapter);
    exit;
}

echo $inputCommand.";".$inputValue;

