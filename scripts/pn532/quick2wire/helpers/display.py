class AnalogueDisplay():
    def __init__(self, max, *pins):
        self._pins = pins
        self._pin_levels = [(pins[index], index * max / len(pins)) for index in range(len(pins))]

    def display(self, value):
        for (pin, level) in self._pin_levels:
            pin.value = 1 if value < level else 0

