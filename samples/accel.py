import event
import halo
import time

# For message broadcasting 
# install mosquitto or use 
# https://www.hivemq.com/


port     = 1883
server   = '192.168.178.65'
ssl      = False

axis = ['x', 'y', 'z']

halo.cloud_message.start(topic_head = 'test', server = server, port=port, ssl=ssl)


@event.start
def on_start():
    ssid     = 'testnet'
    password = 'testnet'

    halo.led.show_single(1, 255, 0, 0, 10)
    halo.wifi.start(ssid, password)

    halo.led.show_single(1, 252, 162, 0, 10)

    while not halo.wifi.is_connected():
        time.sleep(1)

    halo.led.show_single(1, 0, 255, 0, 10)
    
    while True:
        time.sleep(1)
        broadcast_accel()


@event.button_pressed
def on_pressed():
    broadcast_text('button pressed')

@event.free_fall
def on_free_fall():
    broadcast_text('free fall')


@event.arrow_down
def on_arrow_down():
    broadcast_text('arrow down')

@event.arrow_up
def on_arrow_up():
    broadcast_text('arrow up')

@event.rotate_anticlockwise
def on_anticlock():
    broadcast_text('rotate anti clockwise')

@event.rotate_clockwise
def on_clock():
    broadcast_text('rotate clockwise')

@event.shaked
def on_shacked():
    broadcast_text('shaked')

@event.tilted_left
def on_tilted_left():
    broadcast_text('tilted left')

@event.tilted_right
def on_tilted_right():
    broadcast_text('tilted right')


def broadcast_accel():
    global axis

    json = '{ '

    separator = ''
    for i in range(0, len(axis)):
        json = json + separator + '"' + axis[i] + '"' + ': ' + str(halo.motion_sensor.get_acceleration(axis[i]))
        separator = ', '

    json = json + ' }'
    halo.cloud_message.broadcast('accel', json)


def broadcast(message, msg):
    halo.cloud_message.broadcast(message, msg)
        

def broadcast_text(msg):
    broadcast('message', msg)
 

