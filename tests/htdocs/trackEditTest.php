<?php
namespace JukeBox;

require_once 'htdocs/utils/Files.php';
use JukeBox\Utils\Files;

use PHPUnit\Framework\TestCase;
use phpmock\phpunit\PHPMock;

class TrackEditTest extends TestCase {

    use PHPMock;

    const CONFIG_FILENAME = "config.php";
    const FILENAME = "file to move üöä.mp3";
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

        $file_exists = $this->getFunctionMock(__NAMESPACE__, 'file_exists');
        $file_exists->expects($this->atLeastOnce())->willReturn(true);

        $shell_exec = $this->getFunctionMock(__NAMESPACE__, 'shell_exec');
        $shell_exec->expects($this->atLeastOnce())->willReturn(true);

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
    }

    public function tearDown() : void {
        unlink(self::CONFIG_FILENAME);

        if (is_dir($this->sourceFolder)) {
            if (is_file($this->sourceFolder . DIRECTORY_SEPARATOR .  self::FILENAME)) {
                unlink($this->sourceFolder . DIRECTORY_SEPARATOR .  self::FILENAME);
            }
            rmdir($this->sourceFolder);
        }

        if(is_dir($this->targetFolder)) {
            if (is_file($this->targetFolder . DIRECTORY_SEPARATOR .  self::FILENAME)) {
                unlink($this->targetFolder . DIRECTORY_SEPARATOR .  self::FILENAME);
            }
            rmdir($this->targetFolder);
        }
    }

    /**
     * @runInSeparateProcess
     */
    public function testMoveTrack() {
        $_POST['ACTION'] = "trackMove";
        $_POST['filename'] = TrackEditTest::FILENAME;
        $_POST['folderNew'] = Files::buildPath(sys_get_temp_dir(), TrackEditTest::TARGET_FOLDER_NAME);
        $post['folder'] = Files::buildPath(sys_get_temp_dir(), TrackEditTest::SOURCE_FOLDER_NAME);
        $conf['base_url']= "localhost";

        require_once 'htdocs/trackEdit.php';
        $this->assertEquals($_POST['folderNew'], $post['folder']);
        $this->assertTrue(is_file($_POST['folderNew'] . DIRECTORY_SEPARATOR . TrackEditTest::FILENAME));
    }

    /**
     * @runInSeparateProcess
     */
    public function testUpdateTrack() {
        $_POST['ACTION'] = "trackUpdate";
        $_POST['folder'] = Files::buildPath(sys_get_temp_dir(), TrackEditTest::SOURCE_FOLDER_NAME);
        $_POST['filename'] = TrackEditTest::FILENAME;
        $conf['base_url']= "localhost";
        $post['trackArtist'] = "Lorem ipsum";
        $post['trackTitle'] = "dolor sit";
        $post['trackAlbum'] = "amet consectetur";
        $post['trackComposer'] = "adipisici elit äüö";

        $exec = $this->getFunctionMock(__NAMESPACE__, 'exec');
        $exec->expects($this->atLeastOnce())->willReturnCallback(
            function ($command) {
                $mid3v2 = "mid3v2 "
                    . "--artist='Lorem ipsum' "
                    . "--album='amet consectetur' "
                    . "--song='dolor sit' "
                    . "--TCOM='adipisici elit aeueoe' '/tmp/source_folder/file to move üöä.mp3'";
                $this->assertEquals(addslashes($mid3v2), addslashes($command));

            }
        );

        require_once 'htdocs/trackEdit.php';
    }
}
