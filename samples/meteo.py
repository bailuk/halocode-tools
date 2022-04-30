# Unit tests:
#  To each pure function belongs a unit test.
#  Unit tests have the prefix 'test_' they are right below
#  the definiton of the function to be tested and they are
#  allways called on startup (from global scope).
#  
# I2C


import halo
import event
import time
import mbuild

port   = 1883
server = '10.66.4.39'
ssl    = False
topic  = 'meteo'
ssid   = ''
pwd    = ''

halo.cloud_message.start(topic_head = topic, server = server, port = port, ssl = ssl)

intervals = [2, 5, 10, 15, 30, 60, 5*60, 15*60]
interval_index = 0

@event.start
def on_start():
    global ssid, pwd, intervals, interval_index

    show_led(1, hex_to_color('#fa0000'))
    halo.wifi.start(ssid, pwd)
    show_led(1, hex_to_color('#ff8400'))

    while not halo.wifi.is_connected():
        time.sleep(1)

    show_led(1, hex_to_color('#2db01c'))

    show_interval()

    timeout = 0
    while True:
        if timeout >= intervals[interval_index]:
            show_led(1, hex_to_color('#0091ff'))
            read_and_broadcast_sensors()
            time.sleep(1)
            show_led(1, hex_to_color('#2db01c'))
            timeout = 1

        timeout = timeout + 1        
        time.sleep(1)

def read_and_broadcast_sensors():
    values = [ 
        ['moisture',    mbuild.soil_moisture.get_humidity(index = 1)],
        ['humidity',    mbuild.humiture_sensor.get_relative_humidity(index = 1)],
        ['temparature', mbuild.humiture_sensor.get_temperature(opt = 'celsius', index = 1)],
        ['light',       mbuild.light_sensor.get_value(index = 1)]
    ]
    broadcast('sensors', to_json(values))
    

def broadcast(message, msg):
    halo.cloud_message.broadcast(message, msg)
        

def broadcastText(msg):
    broadcast('message', msg)


def show_led(id, color, percentage = 10):
    halo.led.show_single(limit1(id), color[0], color[1], color[2], percentage)

def show_interval():
    global interval_index, intervals
    offset = 3

    for i in range(0, len(intervals)):
        if (interval_index == i):
            show_led(i+offset, hex_to_color('#ff4d00'))
        else:
            show_led(i+offset, hex_to_color('#b81ca5'))
    broadcastText('Update interval: ' + str(intervals[interval_index]+1) + ' seconds')
    broadcast('interval', str(intervals[interval_index]+1))


@event.button_pressed
def on_pressed():
    global interval_index, intervals
    interval_index = inc(interval_index, len(intervals) - 1)
    show_interval()
    

@event.touchpad0_active
def on_touchpad():
    mbuild.servo_driver.set_angle(0, index = 1)

@event.touchpad1_active
def on_touchpad():
    mbuild.servo_driver.set_angle(90, index = 1)

@event.touchpad2_active
def on_touchpad():
    mbuild.servo_driver.set_angle(135, index = 1)

@event.touchpad3_active
def on_touchpad():
    mbuild.servo_driver.set_angle(180, index = 1)

@event.cloud_message('test')
def received_message():
    msg = halo.cloud_message.get_info('test')
    print('message received: ' + msg)


def is_number(value):
    try:
        value = int(value)
        return True
    except ValueError:
        return False

def test_is_number():
    if not is_number(1): print('failed: is_number 1')
    if is_number('msg'): print('failed: is_number 2')

test_is_number()

def to_json_val(value):
    if is_number(value):
        return str(value)
    return '"' + str(value) + '"'

def test_to_json_val():
    if to_json_val(0)     != '0': print('failed: to_json_val 1')
    if to_json_val("txt") != '"txt"': print('failed: to_json_val 2')
    if to_json_val("0")   != '0': print('failed: to_json_val 3')

test_to_json_val()

def to_json(values):
    json = '{ '
    separator = ''

    for i in range(0, len(values)):
        json = json + separator + '"' + values[i][0] + '"' + ': ' + to_json_val(values[i][1])
        separator = ', '

    return json + ' }'


def test_to_json():
    json = to_json([['key', 1]])
    if json != '{ "key": 1 }': print("failed: to_json 1")

    json = to_json([["string", "value"],["val", 1]])
    if json != '{ "string": "value", "val": 1 }': print("failed: to_json 2")

test_to_json()


def inc(id, last):
    return limit(id+1, 0, last)

def test_inc():
    if inc(1, 1) != 0: print('failed: inc 1')
    if inc(1, 2) != 2: print('failed: inc 2')

def limit(id, first, last):
    if id < first: id = last
    if id > last:  id = first
    return id

def limit1(id, last = 12):
    return limit(id, 1, last)

def test_limit():
    if limit1(12)      != 12: print('failed: limit 1')
    if limit1(0)       != 12: print('failed: limit 2')
    if limit1(200, 29) != 1:  print('failed: limit 3')
    if limit(200,0,29) != 0:  print('failed: limit 4')
    if limit1(-1)      != 12: print('failed: limit 5')
    if limit1(13)      != 1:  print('failed: limit 6')

test_limit()



def hex_to_color(color):
    start = 0
    if color[0] == '#':
        start = 1

    r = '' + color[start] + color[start + 1]
    g = '' + color[start + 2] + color[start + 3]
    b = '' + color[start + 4] + color[start + 5]

    return [int(r, 16), int(g, 16), int(b, 16)]

def test_hex_to_color():
    if hex_to_color('#238c44')[0] != 35:  print('failed: hex_to_color 1')
    if hex_to_color('#238c44')[1] != 140: print('failed: hex_to_color 2')
    if hex_to_color('#238c44')[2] != 68:  print('failed: hex_to_color 3')

    if hex_to_color('304152')[0] != 48:  print('failed: hex_to_color 4')
    if hex_to_color('304152')[1] != 65:  print('failed: hex_to_color 5')
    if hex_to_color('304152')[2] != 82:  print('failed: hex_to_color 6')

test_hex_to_color()

