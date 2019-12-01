<?php
namespace JukeBox\Api;

use PHPUnit\Framework\TestCase;
use phpmock\phpunit\PHPMock;

class PlayListTest extends TestCase {

    use PHPMock;

    public function setUp(): void {
        $_SERVER['REQUEST_METHOD'] = '';
        require_once 'htdocs/api/playlist.php';
    }

    public function testReturnHandleGet() {
        $exec = $this->getFunctionMock(__NAMESPACE__, 'exec');
        $exec->expects($this->once())->willReturnCallback(
            function ($command, &$output, &$returnValue) {
                $this->assertEquals(addslashes("echo 'playlistinfo\nclose' | nc -w 1 localhost 6600"),addslashes($command));
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

    public function testHandlePutFails() {
        $file_get_contents = $this->getFunctionMock(__NAMESPACE__, 'file_get_contents');
        $file_get_contents->expects($this->atLeastOnce())->will($this->returnValue(null));

        $this->expectOutputString('playlist attribute missing');
        handlePut();
    }

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
}
