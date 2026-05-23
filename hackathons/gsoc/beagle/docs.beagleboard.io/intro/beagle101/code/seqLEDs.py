import time
import os

LEDs=4
LEDPATH='/sys/class/leds/beaglebone:green:usr'

Open a file for each LED
f = []
for i in range(LEDs):
    f.append(open(LEDPATH+str(i)+"/brightness", "w"))

Sequence
while True:
    for i in range(LEDs):
        f[i].seek(0)
        f[i].write("1")     # 1 turns the LED on
        time.sleep(0.25)
    for i in range(LEDs):
        f[i].seek(0)
        f[i].write("0")     # 0 turns the LED off
        time.sleep(0.25)
