import block_voxel as bv
import async_util as au
import threading

from imports import *

app = Ursina(
    title="Interactive 3D Environment: Integration with ComputerCraft Turtles",
    icon="resources/pyturtle.ico",
    size=(1280, 720),
    borderless=False)
app.backfaceCullingOn()

window.exit_button.disable()
window.fps_counter.disable()
window.entity_counter.disable()
window.collider_counter.disable()
window.cog_button.disable()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


actionMenu = Entity(parent=camera.ui)
inventoryMenu = Entity(parent=camera.ui)


def update():
    if (mouse.hovered_entity and isinstance(mouse.hovered_entity, bv.Block)):
        for tb in bv.get_text_boxes():
            screen_pos = world_position_to_screen_position(
                mouse.hovered_entity.world_position
            )
            tb.position = screen_pos


inputs = {
    'w': "forward",
    's': "back",
    'a': "turn_left",
    'd': "turn_right",
    'space': "up",
    'left shift': "down"
}


def input(key):
    if key in inputs.keys():
        au.sendActionAsync(au.sendAction(inputs[key]), loop)


def main():
    ws_thread = threading.Thread(target=Func(au.start_websocket, loop, actionMenu), daemon=True)
    ws_thread.start()

    app.run()


if (__name__ == '__main__'):
    main()