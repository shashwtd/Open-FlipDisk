# Open-FlipDisc: 3x3 LED test grid on the driver board.
#
# LEDs stand in for the flip-disc coils. The board drives every row and column
# line high (12 V), low (GND) or floating, exactly as it would for a coil, and
# lights one row at a time fast enough that the whole grid looks steady.
#
# Runs on the Pico 2 W with MicroPython. Talks to controller.html over USB.
# Commands (one per line):
#   F<25 x 0/1>  set the whole 5x5 frame, rows R0-R4, columns C0-C4
#   C            clear
#   ?            print the current frame
# Buttons: CLEAR clears, FUNC1 shows the next pattern, FUNC2 starts/stops a chase.

import select
import sys
import time
from machine import Pin

# ---- Board pins (from the PCB) ----
SR_DATA = Pin(2, Pin.OUT, value=0)   # 74HC595 SER, first chip (U2)
SR_CLK = Pin(3, Pin.OUT, value=0)    # SRCLK, all three 74HC595s
SR_LATCH = Pin(4, Pin.OUT, value=0)  # RCLK, all three 74HC595s
STBY = Pin(5, Pin.OUT, value=0)      # TB6612 STBY (10k pull-down: drivers off until high)
ACT_LED = Pin(10, Pin.OUT, value=0)  # red ACTIVE LED
BUTTONS = [Pin(6, Pin.IN, Pin.PULL_UP),   # CLEAR
           Pin(7, Pin.IN, Pin.PULL_UP),   # FUNC1
           Pin(8, Pin.IN, Pin.PULL_UP)]   # FUNC2

# Each matrix line is output 1 of one TB6612 channel. The pairs are the
# (IN1, IN2) bit positions in the 24-bit shift-register word:
# U2 = bits 0-7 (QA-QH), U3 = bits 8-15, U4 = bits 16-23.
ROWS = [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9)]            # R0-R4 = J2 pins 1-5
COLS = [(10, 11), (15, 14), (13, 12), (16, 17), (18, 19)]  # C0-C4 = J3 pins 1-5

# Lines wired to the breadboard. The other lines are never driven.
ACTIVE_ROWS = [2, 3, 4]  # R2, R3, R4 = J2 pins 3, 4, 5
ACTIVE_COLS = [0, 1, 2]  # C0, C1, C2 = J3 pins 1, 2, 3

ROW_TIME_US = 1500  # time each row stays lit per scan
CHASE_MS = 400      # FUNC2 chase speed: bigger = slower
ACT_FLASH_MS = 150  # how long the red ACTIVE LED flashes on each change
DEBOUNCE_MS = 250

PATTERNS = ["111111111", "101010101", "010111010", "111101111", "010101010", "000010000"]
RING = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (1, 0)]

frame = [[0] * 5 for _ in range(5)]


# A line whose IN1 and IN2 bits are both 0 floats (TB6612 "stop").
def high(word, line):
    return word | (1 << line[0])  # IN1=1, IN2=0: output at 12 V


def low(word, line):
    return word | (1 << line[1])  # IN1=0, IN2=1: output at GND


def build_words():
    """One shift-register word per active row: that row high, its lit columns low."""
    words = []
    for r in ACTIVE_ROWS:
        word = 0
        lit = [c for c in ACTIVE_COLS if frame[r][c]]
        if lit:
            word = high(word, ROWS[r])
            for c in lit:
                word = low(word, COLS[c])
        words.append(word)
    return words


def shift_out(word):
    data = SR_DATA.value
    clk = SR_CLK.value
    for bit in range(23, -1, -1):  # first bit ends up in U4 QH, last in U2 QA
        data((word >> bit) & 1)
        clk(1)
        clk(0)
    SR_LATCH.value(1)
    SR_LATCH.value(0)


def clear():
    for row in frame:
        for c in range(5):
            row[c] = 0


def show_3x3(bits):
    for i, r in enumerate(ACTIVE_ROWS):
        for j, c in enumerate(ACTIVE_COLS):
            frame[r][c] = 1 if bits[i * 3 + j] == "1" else 0


def frame_string():
    return "F" + "".join(str(frame[r][c]) for r in range(5) for c in range(5))


def handle(cmd):
    """Apply one command. Returns True if the frame changed."""
    # No "OK" replies: if nothing reads them, USB writes can stall the scan.
    if cmd.startswith("F") and len(cmd) == 26 and all(ch in "01" for ch in cmd[1:]):
        for i in range(25):
            frame[i // 5][i % 5] = 1 if cmd[1 + i] == "1" else 0
        return True
    if cmd == "C":
        clear()
        return True
    if cmd == "?":
        print(frame_string())
        return False
    print("ERR " + cmd)
    return False


def main():
    poll = select.poll()
    poll.register(sys.stdin, select.POLLIN)
    rx = ""
    last_press = [0, 0, 0]
    was_down = [False, False, False]
    pattern = -1
    chasing = False
    chase_step = 0
    last_chase = time.ticks_ms()
    act_until = 0

    shift_out(0)   # every line floating before the drivers wake up
    STBY.value(1)
    print("OPENFLIPDISC READY rows R2-R4, cols C0-C2")
    words = build_words()
    row = 0
    try:
        while True:
            shift_out(words[row % len(words)])
            row += 1
            changed = False
            now = time.ticks_ms()

            while poll.poll(0):  # commands from controller.html
                ch = sys.stdin.read(1)
                if ch in ("\n", "\r"):
                    if rx:
                        if handle(rx.strip()):
                            changed = True
                            chasing = False
                        rx = ""
                else:
                    rx = (rx + ch)[-40:]

            for i, btn in enumerate(BUTTONS):  # buttons on the board
                down = btn.value() == 0
                if down and not was_down[i] and time.ticks_diff(now, last_press[i]) > DEBOUNCE_MS:
                    last_press[i] = now
                    changed = True
                    if i == 0:
                        clear()
                        chasing = False
                    elif i == 1:
                        pattern = (pattern + 1) % len(PATTERNS)
                        show_3x3(PATTERNS[pattern])
                        chasing = False
                    else:
                        chasing = not chasing
                        clear()
                was_down[i] = down

            if chasing and time.ticks_diff(now, last_chase) > CHASE_MS:
                last_chase = now
                i, j = RING[chase_step % len(RING)]
                chase_step += 1
                clear()
                frame[ACTIVE_ROWS[i]][ACTIVE_COLS[j]] = 1
                changed = True

            if changed:
                words = build_words()
                ACT_LED.value(1)  # red ACTIVE LED blinks on every change
                act_until = time.ticks_add(now, ACT_FLASH_MS)
            elif ACT_LED.value() and time.ticks_diff(now, act_until) > 0:
                ACT_LED.value(0)

            time.sleep_us(ROW_TIME_US)
    finally:
        shift_out(0)
        STBY.value(0)
        ACT_LED.value(0)


if __name__ == "__main__":
    main()
