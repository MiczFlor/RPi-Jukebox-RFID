<?php
namespace JukeBox\Api;

use PHPUnit\Framework\TestCase;
use phpmock\phpunit\PHPMock;

class PlayListTest extends TestCase {

    use PHPMock;

    public function setUp(): void {
        $parse_ini_file = $this->getFunctionMock(__NAMESPACE__, 'parse_ini_file');
        $parse_ini_file->expects($this->atLeastOnce())->willReturn(
            array(
                "DEBUG_WebApp" => "FALSE",
                "DEBUG_WebApp_API" => "FALSE"
            ));
        $_SERVER['REQUEST_METHOD'] = '';
        require_once 'htdocs/api/playlist.php';
    }

    /**
     * @runInSeparateProcess
     */
    public function testReturnHandleGet() {
        $exec = $this->getFunctionMock(__NAMESPACE__, 'exec');
        $exec->expects($this->once())->willReturnCallback(
            function ($command, &$output, &$returnValue) {
                $this->assertEquals(addslashes("sudo echo 'playlistinfo\nclose' | nc -w 1 localhost 6600"),addslashes($command));
                $output = array(
                    "OK MPD 0.21.4",
                    "file: First track",
                    "Pos: 0",
                    "Time: 111",
                    "file: Second track",
                    "Pos: 1",
                    "Time: 222",
                    "file: Third track",
                    "Pos: 2",
                    "Time: 333",
                    "Ok"
                );
                $returnValue = 0;
            }
        );
        $header = $this->getFunctionMock(__NAMESPACE__, 'header');
        $header->expects($this->once());
        $this->expectOutputString('{"tracks":[{"file":"First track","pos":"0","time":"111"},{"file":"Second track","pos":"1","time":"222"},{"file":"Third track","pos":"2","time":"333"}],"albumLength":666}');
        handleGet();
    }

    /**
     * @runInSeparateProcess
     */
    public function testHandlePutFails() {
        $file_get_contents = $this->getFunctionMock(__NAMESPACE__, 'file_get_contents');
        $file_get_contents->expects($this->atLeastOnce())->will($this->returnValue(null));

        $this->expectOutputString('playlist attribute missing');
        handlePut();
    }

    /**
     * @runInSeparateProcess
     */
    public function testHandlePutSuccess() {
        $file_get_contents = $this->getFunctionMock(__NAMESPACE__, 'file_get_contents');
        $file_get_contents->expects($this->atLeastOnce())->will($this->returnValue('{"playlist":"The playlist I want to hear", "recursive":"true"}'));

        $exec = $this->getFunctionMock(__NAMESPACE__, 'exec');
        $exec->expects($this->atLeastOnce())->willReturnCallback(
            function ($command, &$output, &$returnValue) {
                $output = '';
                $returnValue = 0;
            }
        );

        $this->expectOutputString('');
        handlePut();
    }

    /**
     * @runInSeparateProcess
     */
    public function testValidateFilePath() {
        $this->assertTrue(validateFilePath('valid/file/path.mp3'));
        $this->assertFalse(validateFilePath('invalid/file/path;rm -rf /'));
    }

    /**
     * @runInSeparateProcess
     */
    public function testSanitizeFilePath() {
        $this->assertEquals('valid/file/path.mp3', sanitizeFilePath('valid/file/path.mp3'));
        $this->assertEquals('invalid/file/pathrm -rf /', sanitizeFilePath('invalid/file/path;rm -rf /'));
    }

    /**
     * @runInSeparateProcess
     */
    public function testExecFunctionWithSanitizedInput() {
        $file_get_contents = $this->getFunctionMock(__NAMESPACE__, 'file_get_contents');
        $file_get_contents->expects($this->atLeastOnce())->will($this->returnValue('{"playlist":"The playlist I want to hear", "recursive":"true"}'));

        $exec = $this->getFunctionMock(__NAMESPACE__, 'exec');
        $exec->expects($this->atLeastOnce())->willReturnCallback(
            function ($command, &$output, &$returnValue) {
                $this->assertStringNotContainsString(';', $command);
                $output = '';
                $returnValue = 0;
            }
        );

        $this->expectOutputString('');
        handlePut();
    }

    /**
     * @runInSeparateProcess
     */
    public function testValidateAndSanitizeGetFileParameter() {
        $_GET['file'] = 'valid/file/path.mp3';
        $this->assertTrue(validateFilePath($_GET['file']));
        $this->assertEquals('valid/file/path.mp3', sanitizeFilePath($_GET['file']));

        $_GET['file'] = 'invalid/file/path;rm -rf /';
        $this->assertFalse(validateFilePath($_GET['file']));
        $this->assertEquals('invalid/file/pathrm -rf /', sanitizeFilePath($_GET['file']));
    }

    /**
     * @runInSeparateProcess
     */
    public function testExecFunctionWithSanitizedGetFileParameter() {
        $_GET['file'] = 'valid/file/path.mp3';
        $exec = $this->getFunctionMock(__NAMESPACE__, 'exec');
        $exec->expects($this->atLeastOnce())->willReturnCallback(
            function ($command, &$output, &$returnValue) {
                $this->assertStringNotContainsString(';', $command);
                $output = '';
                $returnValue = 0;
            }
        );

        $this->expectOutputString('');
        handlePut();
    }
}
