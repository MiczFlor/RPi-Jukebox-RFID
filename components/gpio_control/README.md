# GPIO CONTROL

This service enables the control of different GPIO input & output devices for controlling the Phoniebox.
It uses to a configuration file to configure the active devices.

## How to create and run the service?
* The service can be activated during installation with the installscript.
* If the service was not activated during installation, you can alternatively use `sudo install.sh` in this folder (`components/gpio_control`).

## How to edit configuration files?
The configuration file is located here: `~/RPi-Jukebox-RFID/settings/gpio_settings.ini` 
Editing the configuration file and restarting the service with `sudo systemctl restart phoniebox-gpio-control` will activate the new settings.

In the following the different devices are described. 
Each device can have actions which correspond to function calls.
Up to now the following input devices are implemented:
* **Button**: 
   A simple button with optional long-press actions like hold and repeat functionality or delayed action. 
   Its main parameters are: `Pin` (use GPIO number here) and `functionCall`. For additional options, see [extended documentation below](#doc_button).

* **ShutdownButton**: 
   A specialized implementation for a shutdown button with integrated (but optional) LED support. It initializes a shutdown if the button is pressed more than `time_pressed` seconds and a (optional) LED on GPIO `led_pin` is flashing until that time is reached. For additional information, see [extended documentation below](#doc_sdbutton).

* **RotaryEncoder**:
    Control of a rotary encoder, for example KY040, see also in [Wiki](https://github.com/MiczFlor/RPi-Jukebox-RFID/wiki/Audio-RotaryKnobVolume).
    It can be configured using `pinUp` and `PiNDown` (use GPIO numbers here), `functionCallUp`, `functionCallDown`, and `timeBase` see [extended documentation below](#doc_rotary).

* **TwoButtonControl**:
    This Device uses two Buttons and implements a third action if both buttons are pressed together. See [extended documentation below](#doc_twobutton).

* **StatusLED**:
    A LED which will light up once the Phoniebox has fully booted up and is ready to be used. For additional information, see [extended documentation below](#doc_sled).

Each section needs to be activated by setting `enabled: True`.

Many example files are located in `~/RPi-Jukebox-RFID/components/gpio_control/example_configs/`.

# Extended documentation
This section provides some extended documentation and guideline. Especially some exemplary configurations are introduced showing how these controls can be set up in the configuration file `~/RPi-Jukebox-RFID/settings/gpio_settings.ini`.

## Button<a name="doc_button"></a> 
At the most basic level, a button can be created using an `ini` entry like this:
```
[PlayPause]
enabled: True
Type: Button
Pin: 27
functionCall: functionCallPlayerPause
```
* **enabled**: This needs to be `True` for the button to work.
* **Pin**: GPIO number
* **functionCall**: The function that you want to be called on a button press. See  [function documentation below](#doc_funcs).

However, a button has more parameters than these. In the following comprehensive list you can also find the default values which are used automatically if you leave out these settings:
* **hold_mode**: Specifies what shall happen if the button is held pressed for longer than `hold_time`:
  *  `None` (Default): Nothing special will happen.
  *  `Repeat`: The configured `functionCall` is repeated after each `hold_time` interval.
  *  `Postpone`: The function will not be called before `hold_time`, i.e. the button needs to be pressed this long to activate the function
  *  `SecondFunc`: Holding the button for at least `hold_time` will additionally execute the function `functionCall2`.
  *  `SecondFuncRepeat`: Like SecondFunc, but `functionCall2` is repeated after each `hold_time` interval.
  
  In every `hold_mode` except `Postpone`, the main action `functionCall` gets executed instantly.
  
  Holding the button even longer than `hold_time` will cause no further action unless you are in the `Repeat` or `SecondFuncRepeat` mode.
  
* **hold_time**: Reference time for this buttons `hold_mode` feature in seconds. Default is `0.3`. This setting is ignored if `hold_mode` is unset or `None`
* **functionCall2**: Secondary function; default is `None`. This setting is ignored unless `hold_mode` is set to `SecondFunc` or `SecondFuncRepeat`.
* **pull_up_down**: Configures the internal Pull up/down resistors. Valid settings:
  * `pull_up` (Default). Internal pull-up resistors are activated. Use this if you attached a button to `GND` to the GPIO pin without any external pull-up resistor.
  * `pull_down`. Use this if you need the internal pull-down resistor activated.
  * `pull_off`. Use this to deactivate internal pull-up/pulldown resistors. This is useful if your wiring includes your own (external) pull up / down resistors.
* **edge**: Configures the events in which the GPIO library shall trigger the callback function. Valid settings:
  * `falling` (Default). Triggers if the GPIO voltage goes down.
  * `rising`. Trigegrs only if the GPIO voltage goes up.
  * `both`. Triggers in both cases.
* **bouncetime**: This is a setting of the GPIO library to limit bouncing effects during button usage. Default is `500` ms.
* **antibouncehack**: Despite the integrated bounce reduction of the GPIO library some users may notice false triggers of their buttons (e.g. unrequested / double actions when releasing the button. If you encounter such problems, try setting this setting to `True` to activate an additional countermeasure.

Note: If you prefer, you may also use `Type: SimpleButton` instead of `Type: Button` - this makes no difference.

## ShutdownButton<a name="doc_sdbutton"></a> 
An extended ShutdownButton can be created using an `ini` entry like these:
```
[Shutdown_without_LED]
enabled: True
Type:  ShutdownButton
Pin: 3

[Shutdown_with_LED]
enabled: True
Type:  ShutdownButton
Pin: 3
led_pin: 17
```
* **enabled**: This needs to be `True` for the extended shutdown button to work.
* **Pin**: GPIO number of the button
* **led_pin**: GPIO number of the LED (Default is `None`). Note that you should not attach LEDs to GPIO ports without a matching resistor in line.

Again, there are more parameters than these. In the following comprehensive list you can also find the default values which are used automatically if you leave out these settings:
* **hold_time**: This parameter controls how many seconds (default: `3.0`) the button has to be hold until shutdown will be initiated.
* **iteration_time**: This parameter determines the flashing speed of the LED indicator. Default value is `0.2` seconds.
* **functionCall**: While the default action is `functionCallShutdown`, you might use this button type even with other functions than system shutdown (again, see [function documentation below](#doc_funcs) for a list of available functions).

Furthermore, the following settings can be used as described for the [regular buttons](#doc_button): **pull_up_down**, **edge**, **bouncetime**, **antibouncehack**

Note that using a ShutdownButton without a LED can also be implemented with a normal button like this:

```
[Shutdown]
enabled: True
Type: Button
Pin: 3
hold_mode: Postpone
hold_time: 3.0
functionCall: functionCallShutdown
```

## TwoButtonControl<a name="doc_twobutton"></a> 
A  TwoButtonControl can be created using an `ini` entry like this:

```
[PrevNextStop]
enabled: True
Type: TwoButtonControl
Pin1: 24
Pin2: 25
functionCall1: functionCallPlayerNext
functionCall2: functionCallPlayerPrev
functionCallTwoButtons: functionCallPlayerStop
```
In this example, you can navigate to the previous or, respectively next track by pushing the respective button. If you push both buttons simultaneously, the player stops.

It is possible to combine the TwoButtonControl with the Repeat mode, e.g. to increment the volume further while the button keeps getting held:
```
[VolumeControl]
enabled: True
Type: TwoButtonControl
Pin1: 5
Pin2: 6
hold_time: 0.3
hold_mode: Repeat
functionCall1: functionCallVolD
functionCall2: functionCallVolU
functionCallTwoButtons: functionCallVol0
```
In this example, the volume will be in-/decreased step-wise using intervals of 0.3 seconds while the respective button is held. If both buttons are pushed simultaneously, the player is muted (volume 0).

Furthermore, the following settings can be used as described for the [regular buttons](#doc_button): **pull_up_down**, **edge**, **bouncetime**, **antibouncehack**


## RotaryEncoder<a name="doc_rotary"></a> 
A  RotaryEncoder can be created using an `ini` entry like this:
```
enabled: True
Type: RotaryEncoder
PinUp: 7
PinDown: 8
timeBase: 0.02
functionCallDown: functionCallVolD
functionCallUp: functionCallVolU
```

## StatusLED<a name="doc_sled"></a> 
A  StatusLED can be created using an `ini` entry like this:
```
[StatusLED]
enable: True
Type: StatusLED
Pin: 14
```
* **Pin**: GPIO number of the LED (mandatory option). Note that you should not attach LEDs to GPIO ports without a matching resistor in line.

Note: If you prefer, you may also use `Type: MPDStatusLED` instead of `Type: StatusLED` - this makes no difference.

## Further examples
By tapping the potential of the features presented above, you can create buttons like this:

### Play random tracks or folders
If you have buttons to navigate to the next/previous track it might be a good idea to define that holding these buttons for a certain time (e.g. 2 seconds) will activate a random (surpise!) track or even folder/card. This might look like this

```
[NextOrRand]
enabled: True
Type:  Button
Pin: 24
pull_up_down: pull_up
hold_time: 2.0
hold_mode: SecondFunc
functionCall: functionCallPlayerNext
functionCall2: functionCallPlayerRandomTrack

[PrevOrRand]
enabled: True
Type:  Button
Pin: 25
pull_up_down: pull_up
hold_time: 2.0
hold_mode: SecondFunc
functionCall: functionCallPlayerPrev
functionCall2: functionCallPlayerRandomFolder
```

### Short and long jumps
If you are using two buttons to jump backwards or forwards within the current track, you can use the repeated hold action to allow larger jumps:
```
[SkipForward]
enabled: True
Type:  Button
Pin: 24
pull_up_down: pull_up
hold_time: 5.0
hold_mode: SecondFuncRepeat
functionCall: functionCallPlayerSeekFwd
functionCall2: functionCallPlayerSeekFarFwd
```
In this example, a short press initiates a short jump forward by 10 seconds (functionCallPlayerSeekFwd) while holding the button will cause further, longer jumps. In this case it will cause a jump of 1 minute forward  (functionCallPlayerSeekFarFwd) every 5 seconds. If you wish, you can adjust these values in `components/gpio_control/function_calls.py`.
For jumping backwards, this can be done equivalently (see [function list below](#doc_funcs)).


## Functions<a name="doc_funcs"></a> 
The available functions are defined/implemented in `components/gpio_control/function_calls.py`:
* **functionCallShutdown**: System shutdown
* **functionCallVolU**: Volume up
* **functionCallVolD**: Volume down
* **functionCallVol0**: Mute
* **functionCallPlayerNext**: Next track
* **functionCallPlayerPrev**: Previous track
* **functionCallPlayerPauseForce**: Pause (forced)
* **functionCallPlayerPause**: Pause
* **functionCallRecordStart**: Start recording
* **functionCallRecordStop**: Stop recording
* **functionCallRecordPlayLatest**: Play latest recording
* **functionCallToggleWifi**: Toggle WIFI
* **functionCallPlayerStop**: Stop Player
* **functionCallPlayerSeekFwd**: Seek 10 seconds forward
* **functionCallPlayerSeekBack**: Seek 10 seconds backward
* **functionCallPlayerSeekFarFwd**: Seek 1 minute forward
* **functionCallPlayerSeekFarBack**: Seek 1 minute backward
* **functionCallPlayerRandomTrack**: Jumps to random track (within current playlist)
* **functionCallPlayerRandomCard**: Activate a random card
* **functionCallPlayerRandomFolder**: Play a random folder

## Troubleshooting<a name="doc_trouble"></a> 
If you encounter bouncing effects with your buttons like unrequested/double actions after releasing a button, you can try to set `antibouncehack` to True:

```
[NextSong]
enabled: True
Type:  Button
Pin: 26
functionCall: functionCallPlayerNext
antibouncehack: True
```

Instead of adding this to each button, you can also define it as default for all elements, by inserting the statement into the `Default` section which can be found at the beginning of the `~/RPi-Jukebox-RFID/settings/gpio_settings.ini` file:


```
[DEFAULT]
enabled: True
antibouncehack: True
```
