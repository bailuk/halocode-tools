import event, halo, time

#halo.mesh.set_mode("mesh")

@event.start
def on_start():
    halo.mesh.join_group('api1')


@event.mesh_message('go5')
def on_received():
    print('go5 received')

@event.mesh_message('go4')
def on_received():
    print('go4 received')

go4 = False

@event.button_pressed
def on_pressed():
    global go4
    if (go4):
        print('boradcast go4')
        halo.mesh.broadcast('go4')
        go4 = False

    else:
        print('boradcast go5')
        halo.mesh.broadcast('go5')
        go4 = True


@event.mesh_message('message')
def on_mesh_message():
    halo.mesh.start_group('mesh1')
    halo.mesh.join_group('mesh1')
    halo.mesh.broadcast('message')
    halo.mesh.broadcast('hallo', 'mesh2')
    halo.mesh.get_info('message')
    
    
