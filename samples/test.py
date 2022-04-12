import event
import halo
import time

# hallocode is ESP32-based
#   See https://docs.micropython.org/en/latest/esp32/quickref.html

# WARNING 
#   Python library functions that are not officialy supported by 
#   makeblock can crash this device. They can provoke a boot loop. 
#   Do not test such function in the start event.
import os
import network

import machine
import esp32
import esp

@event.start
def on_start():
    id = 1
    id_old = 1

    print('hallo from mars')

    while True:
        halo.led.show_single(id, 0, 255, 00, 10)
        if id_old != id:
            halo.led.show_single(id_old, 0, 0, 255, 10)
            id_old = id

        id = id + 1
        if id > 12:
            id = 1

        time.sleep(0.5)



@event.button_pressed
def on_pressed():
    # This crashes and reboots the OS 
    # print(os.getcwd())

    # This works
    print('CPU: ' + str(machine.freq()/1000000) + ' MHz')

    farenheit = esp32.raw_temperature()
    celsius = (farenheit-32)/1.8
    print('CPU temp: ' + str(celsius) + '° Celsius')

    # This works
    mega = 1024 * 1024
    print('Flash storage: ' + str(esp.flash_size() / mega) + ' MB')
    print('Halsensor value: ' + str(esp32.hall_sensor()))
    
    esp.osdebug(esp.LOG_DEBUG)

    