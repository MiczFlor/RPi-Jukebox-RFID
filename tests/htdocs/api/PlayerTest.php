<?php
namespace JukeBox\Api;

use PHPUnit\Framework\TestCase;
use phpmock\phpunit\PHPMock;

class PlayerTest extends TestCase {

    use PHPMock;

    public function setUp(): void {
        $parse_ini_file = $this->getFunctionMock(__NAMESPACE__, 'parse_ini_file');
        $parse_ini_file->expects($this->atLeastOnce())->willReturn(
            array(
                "DEBUG_WebApp" => "FALSE",
                "DEBUG_WebApp_API" => "FALSE"
            ));
        $_SERVER['REQUEST_METHOD'] = '';
        require_once 'htdocs/api/player.php';
    }

    public function testReturnHandleGet() {
        $exec = $this->getFunctionMock(__NAMESPACE__, 'exec');
        $exec->expects($this->once())->willReturnCallback(
            function ($command, &$output, &$returnValue) {
                $this->assertEquals(addslashes("sudo echo 'status\ncurrentsong\nclose' | nc -w 1 localhost 6600"),addslashes($command));
                $output = array("MPD", "OK", "key_one: Value one", "key_two: Value two with spaces", "KEY_three: Value three with uppercase key" );
                $returnValue = 0;
            }
        );
        $header = $this->getFunctionMock(__NAMESPACE__, 'header');
        $header->expects($this->once());
        $this->expectOutputString('{"key_one":"Value one","key_two":"Value two with spaces","key_three":"Value three with uppercase key"}');
        handleGet();
    }
}
