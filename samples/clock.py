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

    s_id_old = 0
    m_id_old = 0
    h_id_old = 0


    while True:

        sec =  int(halo.get_timer())
        min =  int(sec / 60)
        hour = int(min / 60)

        min = min - (hour * 60)
        sec = sec - (min * 60)
        
        print('__')
        print(hour)
        print(min)
        print(sec)
        
        s_id = int(sec  * 0.2)
        m_id = int(min  * 0.2)
        h_id = int(hour * 0.2)

        led_off(s_id_old, s_id, m_id, h_id)
        led_off(m_id_old, s_id, m_id, h_id)
        led_off(h_id_old, s_id, m_id, h_id)

        if (h_id != m_id and h_id != s_id): show_led(h_id, colors[11], 5)
        if (m_id != s_id): show_led(m_id, colors[5],  5)
        show_led(s_id, colors[0],  5)

        s_id_old = s_id
        m_id_old = m_id
        h_id_old = h_id

        time.sleep(0.5)


def led_off(id, a, b, c):
    if id != a and id != b and id != c:
        halo.led.off_single(toLedId(id))


def toLedId(id):
    if id == 0:
        id = 12
    return id

def inc(led, limit):
    led = led + 1
    if led >= limit:
        led = 0
    return led

def show_led(id, color, percentage = 10):
    halo.led.show_single(toLedId(id), color[0], color[1], color[2], percentage)

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
