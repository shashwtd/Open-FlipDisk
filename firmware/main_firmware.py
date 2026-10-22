"""Production button-controlled firmware for the Open FlipDisk 5x5 display."""

from machine import Pin
from time import sleep_ms, ticks_diff, ticks_ms


PULSE_MS = 20
INTER_PULSE_MS = 10
DEBOUNCE_MS = 35

# bytes go to U4, U3, then U2
# each entry is (byte, IN1 bit, IN2 bit)
ROW_LINES = (
    (2, 0, 1),  # R0
    (2, 2, 3),  # R1
    (2, 4, 5),  # R2
    (2, 6, 7),  # R3
    (1, 0, 1),  # R4
)

COLUMN_LINES = (
    (1, 2, 3),  # C0
    (1, 7, 6),  # C1
    (1, 5, 4),  # C2
    (0, 0, 1),  # C3
    (0, 2, 3),  # C4
)

BLANK = (
    "00000",
    "00000",
    "00000",
    "00000",
    "00000",
)

SMILEY = (
    "00000",
    "01010",
    "00000",
    "10001",
    "01110",
)

CHECKERBOARD = (
    "10101",
    "01010",
    "10101",
    "01010",
    "10101",
)

INVERSE_CHECKERBOARD = (
    "01010",
    "10101",
    "01010",
    "10101",
    "01010",
)


class FlipDiskDisplay:
    def __init__(self):
        # keep the drivers off while everything starts up
        self.standby = Pin(5, Pin.OUT, value=0)
        self.data = Pin(2, Pin.OUT, value=0)
        self.clock = Pin(3, Pin.OUT, value=0)
        self.latch = Pin(4, Pin.OUT, value=0)
        self.activity_led = Pin(10, Pin.OUT, value=0)

        # idk which way the discs face after boot
        self.state = [[None for _ in range(5)] for _ in range(5)]
        self.disable()

    def _latch_bytes(self, values):
        self.latch.value(0)

        for value in values:
            for bit in range(7, -1, -1):
                self.data.value((value >> bit) & 1)
                self.clock.value(1)
                self.clock.value(0)

        self.latch.value(1)
        self.latch.value(0)

    @staticmethod
    def _set_line(values, line, level):
        byte_index, in1_bit, in2_bit = line

        if level > 0:
            values[byte_index] |= 1 << in1_bit
        elif level < 0:
            values[byte_index] |= 1 << in2_bit

    def disable(self):
        # turn the drivers off before clearing their inputs
        self.standby.value(0)
        self._latch_bytes((0, 0, 0))
        self.activity_led.value(0)

    def pulse(self, row, column, on):
        if not 0 <= row < 5 or not 0 <= column < 5:
            raise ValueError("row and column must be between 0 and 4")

        values = [0, 0, 0]
        polarity = 1 if on else -1
        self._set_line(values, ROW_LINES[row], polarity)
        self._set_line(values, COLUMN_LINES[column], -polarity)

        try:
            self._latch_bytes(values)
            self.activity_led.value(1)
            self.standby.value(1)
            sleep_ms(PULSE_MS)
        finally:
            self.disable()

        self.state[row][column] = bool(on)
        sleep_ms(INTER_PULSE_MS)

    def show(self, pattern, force=False):
        if len(pattern) != 5 or any(len(row) != 5 for row in pattern):
            raise ValueError("pattern must contain five rows of five pixels")

        for row in range(5):
            for column in range(5):
                on = pattern[row][column] == "1"
                if force or self.state[row][column] is None:
                    self.pulse(row, column, on)
                elif self.state[row][column] != on:
                    self.pulse(row, column, on)


class DebouncedButton:
    def __init__(self, gpio):
        self.pin = Pin(gpio, Pin.IN, Pin.PULL_UP)
        self.raw_state = self.pin.value()
        self.stable_state = self.raw_state
        self.changed_at = ticks_ms()

    def pressed(self):
        now = ticks_ms()
        raw_state = self.pin.value()

        if raw_state != self.raw_state:
            self.raw_state = raw_state
            self.changed_at = now

        if (
            raw_state != self.stable_state
            and ticks_diff(now, self.changed_at) >= DEBOUNCE_MS
        ):
            self.stable_state = raw_state
            return raw_state == 0

        return False


def run():
    display = FlipDiskDisplay()
    clear_button = DebouncedButton(6)
    function_1_button = DebouncedButton(7)
    function_2_button = DebouncedButton(8)
    checkerboard_inverted = False

    print("Open FlipDisk ready")
    print("CLEAR: blank | FUNC1: smiley | FUNC2: checkerboard")

    try:
        while True:
            if clear_button.pressed():
                print("Clearing display")
                display.show(BLANK, force=True)

            elif function_1_button.pressed():
                print("Showing smiley")
                display.show(SMILEY)

            elif function_2_button.pressed():
                checkerboard_inverted = not checkerboard_inverted
                print("Showing checkerboard")
                display.show(
                    INVERSE_CHECKERBOARD
                    if checkerboard_inverted
                    else CHECKERBOARD
                )

            sleep_ms(10)
    finally:
        display.disable()


run()
