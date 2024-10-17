<?php

use PHPUnit\Framework\TestCase;

class ValidationTest extends TestCase
{
    public function testValidateFilePath()
    {
        $this->assertTrue(validateFilePath('valid/file/path.mp3'));
        $this->assertFalse(validateFilePath('invalid/file/path;rm -rf /'));
        $this->assertFalse(validateFilePath('invalid/file/path/../etc/passwd'));
        $this->assertTrue(validateFilePath('another/valid-file_path.mp3'));
    }

    public function testSanitizeInput()
    {
        $this->assertEquals('valid/file/path.mp3', sanitizeInput('valid/file/path.mp3'));
        $this->assertEquals('invalid/file/pathrm -rf /', sanitizeInput('invalid/file/path;rm -rf /'));
        $this->assertEquals('invalid/file/path../etc/passwd', sanitizeInput('invalid/file/path/../etc/passwd'));
        $this->assertEquals('another/valid-file_path.mp3', sanitizeInput('another/valid-file_path.mp3'));
    }
}
