# UTILITY FUNCTIONS FOR USE WITH PANDA3D

def move_cam(direction):
    pos = base.cam.get_pos()
    angle = base.cam.getHpr()
    match direction:
        case "left":
            base.cam.setPos(pos.x - base.cam_speed, pos.y, pos.z)
        case "right":
            base.cam.setPos(pos.x + base.cam_speed, pos.y, pos.z)
        case "fwd":
            base.cam.setPos(pos.x, pos.y + base.cam_speed, pos.z)
        case "back":
            base.cam.setPos(pos.x, pos.y - base.cam_speed, pos.z)
        case "up":
            base.cam.setPos(pos.x, pos.y, pos.z + base.cam_speed)
        case "down":
            base.cam.setPos(pos.x, pos.y, pos.z - base.cam_speed)
        case "look_down":
            base.cam.setHpr(angle.x, angle.y - base.cam_speed, angle.z)
        case "look_up":
            base.cam.setHpr(angle.x, angle.y + base.cam_speed, angle.z)
        case "speed_up":
            base.cam_speed *= 2.
        case "speed_down":
            base.cam_speed /= 2.
        case _: 
            print("Move direction not recognised!")
    
def enable_camera_controls(esc=True, buffer=False):
    base.cam_speed = .2
    base.accept("arrow_left", move_cam, ["left"])
    base.accept("arrow_left-repeat", move_cam, ["left"])
    base.accept("a", move_cam, ["left"])
    base.accept("a-repeat", move_cam, ["left"])
    base.accept("arrow_right", move_cam, ["right"])
    base.accept("arrow_right-repeat", move_cam, ["right"])
    base.accept("d", move_cam, ["right"])
    base.accept("d-repeat", move_cam, ["right"])
    base.accept("arrow_up", move_cam, ["fwd"])
    base.accept("arrow_up-repeat", move_cam, ["fwd"])
    base.accept("w", move_cam, ["fwd"])
    base.accept("w-repeat", move_cam, ["fwd"])
    base.accept("arrow_down", move_cam, ["back"])
    base.accept("arrow_down-repeat", move_cam, ["back"])
    base.accept("s", move_cam, ["back"])
    base.accept("s-repeat", move_cam, ["back"])
    base.accept("page_up", move_cam, ['up'])
    base.accept("page_up-repeat", move_cam, ['up'])
    base.accept("q", move_cam, ['up'])
    base.accept("q-repeat", move_cam, ['up'])
    base.accept("page_down", move_cam, ['down'])
    base.accept("page_down-repeat", move_cam, ['down'])
    base.accept("e", move_cam, ['down'])
    base.accept("e-repeat", move_cam, ['down'])
    base.accept("g", move_cam, ['look_down'])
    base.accept("g-repeat", move_cam, ['look_down'])
    base.accept("h", move_cam, ['look_up'])
    base.accept("h-repeat", move_cam, ['look_up'])
    base.accept("p", move_cam, ['speed_up'])
    base.accept("o", move_cam, ['speed_down'])

    if buffer: base.accept("v", base.bufferViewer.toggleEnable)
    if esc:    base.accept("escape", base.userExit)