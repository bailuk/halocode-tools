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

    showLed(1, hexToColor('#fa0000'))
    halo.wifi.start(ssid, pwd)
    showLed(1, hexToColor('#ff8400'))

    while not halo.wifi.is_connected():
        time.sleep(1)

    showLed(1, hexToColor('#2db01c'))

    showInterval()

    timeout = 0
    while True:
        if timeout >= intervals[interval_index]:
            showLed(1, hexToColor('#0091ff'))
            readAndBroadcastSensors()
            time.sleep(1)
            showLed(1, hexToColor('#2db01c'))
            timeout = 1

        timeout = timeout + 1        
        time.sleep(1)

def readAndBroadcastSensors():
    values = [ 
        ['moisture',    mbuild.soil_moisture.get_humidity(index = 1) ],
        ['humidity',    mbuild.humiture_sensor.get_relative_humidity(index = 1)],
        ['temparature', mbuild.humiture_sensor.get_temperature(opt = 'celsius', index = 1)],
        ['light',       mbuild.light_sensor.get_value(index = 1)]
    ]
    broadcast('sensors', toJson(values))
        
    
def toJson(values):
    json = '{ '
    separator = ''

    for i in range(0, len(values)):
        json = json + separator + '"' + values[i][0] + '"' + ': ' + str(values[i][1])
        separator = ', '

    return json + ' }'
    

def broadcast(message, msg):
    halo.cloud_message.broadcast(message, msg)
        

def broadcastText(msg):
    broadcast('message', msg)


def toLedId(id):
    if id < 1:
        id = 12
    if id > 12:
        id = 1
    return id

def inc(led, limit):
    led = led + 1
    if led >= limit:
        led = 0
    return led

def showLed(id, color, percentage = 10):
    halo.led.show_single(toLedId(id), color[0], color[1], color[2], percentage)

def hexToColor(color):
    start = 0
    if color[0] == '#':
        start = 1

    r = '' + color[start] + color[start + 1]
    g = '' + color[start + 2] + color[start + 3]
    b = '' + color[start + 4] + color[start + 5]

    return [int(r, 16), int(g, 16), int(b, 16)]


def showInterval():
    global interval_index, intervals
    offset = 3

    for i in range(0, len(intervals)):
        if (interval_index == i):
            showLed(i+offset, hexToColor('#ff4d00'))
        else:
            showLed(i+offset, hexToColor('#b81ca5'))
    broadcastText('Update interval: ' + str(intervals[interval_index]+1) + ' seconds')
    broadcast('interval', str(intervals[interval_index]+1))


@event.button_pressed
def on_pressed():
    global interval_index, intervals
    interval_index = inc(interval_index, len(intervals))
    showInterval()
    

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
def received_message(message):
    print('message received: ')
