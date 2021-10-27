RDM6300 Reader
---------------

The RDM6300 / RDM630 connected via serial UART port

**place-capable**: yes

Options
^^^^^^^^^^^^^

Number Format

Board Connections
^^^^^^^^^^^^^^^^^^^^^^

The voltage level of the RX/TX is 3.3V despite the wide-spread belief that it is 5V. (At least on the boards I have).
I did check with an oscilloscope. And one can easily identify the AMS1117 LDO voltage regulator on the backside of the board.

No warranties: If you meddle with GPIOs you are old enough to know the risks of wrong voltage levels.
