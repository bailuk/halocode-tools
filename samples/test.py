import event
import halo
import time

@event.start
def on_start():
    id = 1
    id_old = 1
    while True:
        halo.led.show_single(id, 0, 255, 00, 10)
        if id_old != id:
            halo.led.show_single(id_old, 0, 0, 255, 10)
            id_old = id

        id = id + 1
        if id > 12:
            id = 1

        time.sleep(0.5)
        print('hallo from mars')
