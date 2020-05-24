// https://arduino-esp8266.readthedocs.io/en/latest/esp8266wifi/client-examples.html#request-the-data
// https://github.com/markruys/arduino-Max72xxPanel
// https://github.com/adafruit/Adafruit-GFX-Library

//DOT Matrix:       ESP8266 NodeMCU:
//VCC               5V (VUSB)
//GND               GND
//DIN               D7 (GPIO13)
//CS                D3 (GPIO0)
//CLK               D5 (GPIO14)

#include <ESP8266WiFi.h>

#include <Adafruit_GFX.h>
#include <Max72xxPanel.h>

unsigned long act_milli;

int pinCS = 0;                          
int numberOfHorizontalDisplays = 4;     
int numberOfVerticalDisplays = 1; 

Max72xxPanel matrix = Max72xxPanel(pinCS, numberOfHorizontalDisplays, numberOfVerticalDisplays);

String Ticker = "domies ";

int wait = 50;                  
int brightness = 3;             //0 to 15
int spacer = 1;                 
int width = 5 + spacer;     

/*****************************************************************
/* Debug output                                                  *
/*****************************************************************/
void debug_out(const String& text, const bool linebreak) {
	if (linebreak) {
		Serial.println(text);
	} else {
		Serial.print(text);
	}
}

const unsigned long pause_between_update_attempts = 86400000;

/*****************************************************************
/* Configuration part start                                      *
/*****************************************************************/
const char* ssid = "foo";
const char* password = "foo";
const char* host = "192.168.42.42";
int port = 80;
/*****************************************************************
/* Configuration part end                                        *
/*****************************************************************/

int playsNow(){
	WiFiClient client;
	int isPlaying = 1;
	
	Serial.printf("\n[Connecting to %s ... ", host);
	if (client.connect(host, port)){
		Serial.println("connected]");
		
		Serial.println("[Sending a request]");
		
		client.print(String("GET /ajax.loadOverallTime.php") + " HTTP/1.1\r\n" +
                 "Host: " + host + ":" + port + "\r\n" +
                 "Connection: close\r\n" +
                 "\r\n"
                );
				
		Serial.println("[Response:]");		
		while (client.connected() || client.available()){
			if (client.available()){
				String line = client.readStringUntil('\n');
				Serial.println(line);
				if (line.indexOf("00:00") >= 0){
					isPlaying = 0;
					Serial.println(line);
				}
			}
		}
		client.stop();
		Serial.println("\n[Disconnected]");
	}
	else{
		Serial.println("connection failed!]");
		client.stop();
		Ticker = "booting ";
		show();
		isPlaying = 2;
	}
	
	return isPlaying;
}

void sendData(){
	WiFiClient client;
	
	int playsNowTemp = playsNow();
	
	Serial.printf("\n[Connecting to %s ... ", host);
	if (playsNowTemp == 1 && client.connect(host, port)){
		Serial.println("connected]");
		
		Serial.println("[Sending a request]");
		
		client.print(String("GET /ajax.loadInfo.php") + " HTTP/1.1\r\n" +
                 "Host: " + host + ":" + port + "\r\n" +
                 "Connection: close\r\n" +
                 "\r\n"
                );
				
		Serial.println("[Response:]");
		int isPlaying = 0;
		while (client.connected() || client.available()){
			if (client.available()){
				String line = client.readStringUntil('\n');
				Serial.println(line);
				if (line.indexOf("<strong>") >= 0 && line.indexOf("<strong></strong>") < 0){
					isPlaying = 1;
					line.replace("<strong>", " ");
					line.replace("</strong>", " ");
					line.replace("<br>", " ");
					line.replace("<i>", " ");
					line.replace("</i>", " ");
					Serial.println(line);
					Ticker = line;
				}
			}
		}
		client.stop();
		Serial.println("\n[Disconnected]");
		if (isPlaying == 0){
			delay (5000);
		}
		else{
			show();
		}
	}
	else{
		Serial.println("connection failed!]");
		client.stop();
		if (playsNowTemp != 2){
			delay (5000);
		}		
	}
}

void show() {
  for ( int i = 0 ; i < width * Ticker.length() + matrix.width() - 1 - spacer; i++ ) {

    matrix.fillScreen(LOW);

    int letter = i / width;
    int x = (matrix.width() - 1) - i % width;
    int y = (matrix.height() - 8) / 2; 

    while ( x + width - spacer >= 0 && letter >= 0 ) {
      if ( letter < Ticker.length() ) {
        matrix.drawChar(x, y, Ticker[letter], HIGH, LOW, 1);
      }
      letter--;
      x -= width;
    }

    matrix.write(); 
    delay(wait);    
  }
}

void setup() 
{
  Serial.begin(9600);
  
  Serial.printf("Connecting to %s ", ssid);
  
  matrix.setIntensity(brightness); 

  matrix.setRotation(0, 1);        
  matrix.setRotation(1, 1);        
  matrix.setRotation(2, 1);        
  matrix.setRotation(3, 1);
  
  WiFi.begin(ssid, password);
  int retry_count = 0;
  while ((WiFi.status() != WL_CONNECTED) && (retry_count < 20))
  {
	  show();
	  Serial.print(".");
	  retry_count++;
  }
  
  if (retry_count == 20){
	  ESP.restart();
  }
  
  Serial.println(" connected");
  
  show();
}

void loop() 
{  
  act_milli = millis();
  
  sendData();
  
  if (act_milli > (2 * pause_between_update_attempts)) {
	ESP.restart();
  }
  
  if (WiFi.status() != WL_CONNECTED) {  // reconnect if connection lost
	int retry_count = 0;
	debug_out(F("Connection lost, reconnecting "),0);
	WiFi.reconnect();
	while ((WiFi.status() != WL_CONNECTED) && (retry_count < 20)) {
		delay(500);
		debug_out(".",0);
		retry_count++;
	}
	
	debug_out("",1);
  }
}
