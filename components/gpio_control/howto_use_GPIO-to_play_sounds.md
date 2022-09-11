To use GPIO-Pins to play music, use the "functionCall_1" to "functionCall_9" directives . Afterward the connected buttons will appear as new rfid-Cards (1 to 9).
So you can use them to mach folders or sounds to them.

Example:

[PressOne]
enabled: True
Type: Button
Pin: 27
pull_up_down: pull_down
functionCall: functionCall_1


[PressTwo]
enabled: True
Type: Button
Pin: 22
pull_up_down: pull_down
functionCall: functionCall_2

[PressThree]
enabled: True
Type: Button
Pin: 23
pull_up_down: pull_down
functionCall: functionCall_3

[PressFour]
enabled: True
Type: Button
Pin: 24
pull_up_down: pull_down
functionCall: functionCall_4

[PressFive]
enabled: True
Type: Button
Pin: 13
pull_up_down: pull_down
functionCall: functionCall_5

[PressSix]
enabled: True
Type: Button
Pin: 06
pull_up_down: pull_down
functionCall: functionCall_6

[PressSeven]
enabled: True
Type: Button
Pin: 25
pull_up_down: pull_down
functionCall: functionCall_7

[PressEight]
enabled: True
Type: Button
Pin: 5
pull_up_down: pull_down
functionCall: functionCall_8

[PlayPause]
enabled: True
Type: Button
Pin: 19
pull_up_down: pull_down
functionCall: functionCallPlayerPause

