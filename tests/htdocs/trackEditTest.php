<?php
namespace JukeBox;

require_once 'htdocs/utils/Files.php';
use JukeBox\Utils\Files;

use PHPUnit\Framework\TestCase;
use phpmock\phpunit\PHPMock;

class TrackEditTest extends TestCase {

    use PHPMock;

    const CONFIG_FILENAME = "config.php";
    const FILENAME = "file to move üöä";
    const SOURCE_FOLDER_NAME = "source_folder";
    const TARGET_FOLDER_NAME = "target_folder";
    private $sourceFolder;
    private $targetFolder;

    public function __construct($name = null, array $data = [], $dataName = '') {
        $this->sourceFolder = Files::buildPath(sys_get_temp_dir(), TrackEditTest::SOURCE_FOLDER_NAME);
        $this->targetFolder = Files::buildPath(sys_get_temp_dir(), TrackEditTest::TARGET_FOLDER_NAME);

        parent::__construct($name, $data, $dataName);
    }

    public function setUp(): void {
        if (!is_dir($this->sourceFolder)) {
            mkdir($this->sourceFolder);
        }

        if(!is_dir($this->targetFolder)) {
            mkdir($this->targetFolder);
        }

        fopen($this->sourceFolder . DIRECTORY_SEPARATOR . self::FILENAME, "w");
        fopen(self::CONFIG_FILENAME, "w");
        $_SERVER['HTTP_HOST'] = 'localhost';
    }

    public function tearDown() : void {
        unlink($this->targetFolder . DIRECTORY_SEPARATOR .  self::FILENAME);
        unlink(self::CONFIG_FILENAME);

        if (is_dir($this->sourceFolder)) {
            rmdir($this->sourceFolder);
        }

        if(is_dir($this->targetFolder)) {
            rmdir($this->targetFolder);
        }
    }

    public function testMoveTrack() {
        $file_exists = $this->getFunctionMock(__NAMESPACE__, 'file_exists');
        $file_exists->expects($this->atLeastOnce())->willReturn(true);

        $file_get_contents = $this->getFunctionMock(__NAMESPACE__, 'file_get_contents');
        $file_get_contents->expects($this->atLeastOnce())->willReturn(sys_get_temp_dir());

        $parse_ini_file = $this->getFunctionMock(__NAMESPACE__, 'parse_ini_file');
        $parse_ini_file->expects($this->atLeastOnce())->willReturn(
            array(
            "DEBUG_WebApp" => "FALSE",
            "DEBUG_WebApp_API" => "FALSE",
            "SECONDSWIPE" => "FALSE",
            "SHOWCOVER" => "FALSE",
            "VERSION" => "FALSE",
            "EDITION" => "FALSE",
            "AUDIOVOLMAXLIMIT" => "FALSE",
            "LANG" => "FALSE",
            "AUDIOFOLDERSPATH" => sys_get_temp_dir()
        ));

        $_POST['ACTION'] = "trackMove";
        $_POST['filename'] = TrackEditTest::FILENAME;
        $_POST['folderNew'] = Files::buildPath(sys_get_temp_dir(), TrackEditTest::TARGET_FOLDER_NAME);
        $post['folder'] = Files::buildPath(sys_get_temp_dir(), TrackEditTest::SOURCE_FOLDER_NAME);
        $conf['base_url']= "localhost";

        require_once 'htdocs/trackEdit.php';
        $this->assertEquals($_POST['folderNew'], $post['folder']);
        $this->assertTrue(is_file($_POST['folderNew'] . DIRECTORY_SEPARATOR . TrackEditTest::FILENAME));
    }
}
