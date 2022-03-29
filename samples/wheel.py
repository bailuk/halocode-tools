# API reference:
#  http://docs.makeblock.com/halocode/en/python-api/python-api.html

import event
import halo
import time


@event.start
def on_start():
    colors = [
        hexToColor('00ff00'),  # 1
        hexToColor('00ff00'),  # 2
        hexToColor('00ff00'),  # 3
        hexToColor('00ff00'),  # 4
        hexToColor('fcbe05'),  # 5
        hexToColor('f98909'),  # 6
        hexToColor('e509f9'),  # 7
        hexToColor('ff0000'),  # 8
        hexToColor('ff0000'),  # 9
        hexToColor('ff0000'),  # 10
        hexToColor('ff0000'),  # 11
        hexToColor('ff0000')   # 12
    ]

    led = 0

    while True:

        show_led(led, colors[led], 5)
        led = inc(led, 12)
        show_led(led, colors[led], 50)

        time.sleep(0.5)


def inc(led, limit):
    led = led + 1
    if led >= limit:
        led = 0
    return led

def show_led(index, color, percentage = 10):
    halo.led.show_single(index + 1, color[0], color[1], color[2], percentage)

def hexToColor(color):
    start = 0
    if color[0] == '#':
        start = 1

    r = '' + color[start] + color[start + 1]
    g = '' + color[start + 2] + color[start + 3]
    b = '' + color[start + 4] + color[start + 5]

    return [int(r, 16), int(g, 16), int(b, 16)]


@event.button_pressed
def on_pressed():
    halo.led.off_all()
