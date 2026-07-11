from machine import Pin
from time import sleep_ms


ACTIVITY_LED = Pin(10, Pin.OUT, value=0)

while True:
    ACTIVITY_LED.value(1)
    sleep_ms(250)

    ACTIVITY_LED.value(0)
    sleep_ms(750)
