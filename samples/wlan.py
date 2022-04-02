import event
import halo
import time


@event.start
def on_start():
    ssid = "localtest"
    password = "localtest"

    halo.led.show_single(1, 255, 0, 0, 10)
    halo.wifi.start(ssid, password)

    halo.led.show_single(1, 252, 162, 0, 10)

    while not halo.wifi.is_connected():
        time.sleep(1)

    halo.led.show_single(1, 0, 255, 0, 10)
# cloud_message.start(topi_head, client_id=None, server="mq.makeblock.com", port=1883, user=None, password=None, keepalive=60, ssl=False)
    time.sleep(10)
    halo.cloud_message.start(topic_head = 'test', server = '192.168.1.1', ssl=False)
    halo.led.show_single(1, 0, 0, 255, 10)

    while True:
        time.sleep(1)



@event.button_pressed
def on_pressed():
    halo.cloud_message.broadcast('test', 'test')
    print('halo.cloud_message.broadcast')

# @event.received('test')
# def onreceive(m, msg):
#    print('test')



@event.cloud_message('test')
def received_message(message):
    print(message)
