# Additional Matrix Display for Phoniebox :tv:

## Items needed :shopping_cart:

* [NodeMCU ESP8266, CPU/WLAN](https://de.aliexpress.com/w/wholesale-nodemcu-v3-esp8266-ch340.html?spm=2114.010208.0.0.2zt6Ca&initiative_id=SB_20170101021508&site=deu&groupsort=1&SortType=price_asc&g=y&SearchText=nodemcu+v3+esp8266+ch340)
* [MAX7219 dot matrix module microcontroller module 4 in one display](https://www.aliexpress.com/item/32689479860.html?spm=a2g0s.9042311.0.0.519b4c4dhHfWJJ)

## Configuration :wrench:

In the [display.ino](display.ino#L48-L50) there is following configuration part:

    const char* ssid = "foo";
    const char* password = "foo";
    const char* host = "192.168.42.42";

`ssid` is your local WiFi network. `password` is the password for your WiFi network. `host` is the **static** IP of your Phoniebox.
For flashing the ESP, you can use the [Arduino IDE](https://en.wikipedia.org/wiki/Arduino_IDE). But there are a few more other possibilities to do this.

## Pics :camera:

![still](still.jpg)
![ticker](ticker.gif)
