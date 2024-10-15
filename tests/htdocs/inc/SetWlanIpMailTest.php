<?php
namespace JukeBox\Inc;

use PHPUnit\Framework\TestCase;
use phpmock\phpunit\PHPMock;

class SetWlanIpMailTest extends TestCase {

    use PHPMock;

    public function setUp(): void {
        $parse_ini_file = $this->getFunctionMock(__NAMESPACE__, 'parse_ini_file');
        $parse_ini_file->expects($this->atLeastOnce())->willReturn(
            array(
                "DEBUG_WebApp" => "FALSE",
                "DEBUG_WebApp_API" => "FALSE"
            ));
        $_SERVER['REQUEST_METHOD'] = '';
        require_once 'htdocs/inc.setWlanIpMail.php';
    }

    /**
     * @runInSeparateProcess
     */
    public function testValidateEmail() {
        $filter_var = $this->getFunctionMock(__NAMESPACE__, 'filter_var');
        $filter_var->expects($this->atLeastOnce())->willReturnCallback(
            function ($email, $filter) {
                $this->assertEquals(FILTER_VALIDATE_EMAIL, $filter);
                return filter_var($email, $filter);
            }
        );

        $this->assertTrue(filter_var('test@example.com', FILTER_VALIDATE_EMAIL));
        $this->assertFalse(filter_var('invalid-email', FILTER_VALIDATE_EMAIL));
    }

    /**
     * @runInSeparateProcess
     */
    public function testSanitizeEmail() {
        $htmlspecialchars = $this->getFunctionMock(__NAMESPACE__, 'htmlspecialchars');
        $htmlspecialchars->expects($this->atLeastOnce())->willReturnCallback(
            function ($string, $flags, $encoding) {
                $this->assertEquals(ENT_QUOTES, $flags);
                $this->assertEquals('UTF-8', $encoding);
                return htmlspecialchars($string, $flags, $encoding);
            }
        );

        $this->assertEquals('test@example.com', htmlspecialchars('test@example.com', ENT_QUOTES, 'UTF-8'));
        $this->assertEquals('test&lt;script&gt;@example.com', htmlspecialchars('test<script>@example.com', ENT_QUOTES, 'UTF-8'));
    }

    /**
     * @runInSeparateProcess
     */
    public function testExecFunctionReplacement() {
        $shell_exec = $this->getFunctionMock(__NAMESPACE__, 'shell_exec');
        $shell_exec->expects($this->atLeastOnce())->willReturnCallback(
            function ($command) {
                $this->assertStringContainsString('sudo', $command);
                return shell_exec($command);
            }
        );

        $this->assertNotNull(shell_exec('sudo echo "test"'));
    }
}
