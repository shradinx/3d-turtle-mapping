import block_voxel as bv
import async_util as au
import threading

import turtle_handler as th
import gui_util as gu

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

host = "0.0.0.0"
port = 8000

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


def start_websocket():
    async def run():
        async with websockets.serve(au.handshake, host, port) as ws:
            print(f"[WebSocket] Server started on ws://{host}:{port}")

            def make_buttons():
                pos = (window.top_left.x+0.25, window.top_left.y)
                gu.populate_action_text()

                WindowPanel(
                    parent=actionMenu,
                    title="Actions Menu",
                    position=pos,
                    content=[
                        *gu.get_action_text().values(),
                        *gu.get_buttons(loop=loop)
                    ]
                )
                gu.center_action_text()
            
            invoke(make_buttons, delay=0.1)
            invoke(th.make_inventory, delay=0.1)
            au.init_editor_cam()
            await asyncio.Future()

    loop.run_until_complete(run())


def main():
    ws_thread = threading.Thread(target=start_websocket, daemon=True)
    ws_thread.start()

    app.run()


if (__name__ == '__main__'):
    main()
