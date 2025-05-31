from block_voxel import *
import block_voxel as bv
import async_util as au
from string_util import *
import asyncio
import websockets
import threading

from turtle_handler import *

from ursina import *

window.borderless = False

app = Ursina(title="Interactive 3D Environment: Integration with ComputerCraft Turtles")

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
    if (mouse.hovered_entity and isinstance(mouse.hovered_entity, Block)):
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

def get_buttons():
    for k, v in au.buttonActions.items():
        yield Button(
            text=v,
            scale=(0.25, 0.075),
            on_click=lambda k=k: au.sendActionAsync(au.sendAction(k), loop)
        )

def get_wip_buttons():
    for k, v in au.WIP_actions.items():
        yield Button(
            text=v,
            scale=(0.25, 0.075)
            # on_click=lambda k=k: sendActionAsync(sendAction(k), loop)
        )

def get_action_text():
    return [
        Text(text="Use W,S for forward/back movement..." , scale=1),
        Text(text="Use A,S for left/right rotation...", scale=1)
    ]

def make_inventory():
    global active_slot

    rows, cols = 4, 4
    button_size = 0.15
    spacing = 0.025

    grid_width = cols * button_size + (cols - 1) * spacing
    grid_height = rows * button_size + (rows - 1) * spacing

    button_grid = Inventory(grid_width=grid_width, grid_height=grid_height)
    button_grid.collision = True

    for y in range(rows):
        for x in range(cols):
            i = y * cols + x
            text = str(i + 1)
            hover_text = "Empty"
            b = Slot(
                index=text,
                hover_text=hover_text,
                button_size=button_size,
                parent=button_grid,
                x=x,
                y=y,
                spacing=spacing
            )
            if i == 0:
                b.color = color.gray
            invButtons.append(b)
    active_slot = invButtons[0]
    draw_slot_notification(active_slot.get_hover_text())

""" 
WIP Buttons -> WindowPanel.content

Text(text="WIP Buttons", origin=(0, 0), scale=1),
*get_wip_buttons() 
"""

def start_websocket():
    async def run():
        async with websockets.serve(au.handshake, host, port) as ws:
            print(f"[WebSocket] Server started on ws://{host}:{port}")

            def make_buttons():
                pos = (window.top_left.x+0.25, window.top_left.y)

                wp = WindowPanel(
                    parent=actionMenu,
                    title="Actions Menu",
                    position=pos,
                    content=[
                        *get_action_text(),
                        *get_buttons()
                    ]
                )
            
            invoke(make_buttons, delay=0.1)
            invoke(make_inventory, delay=0.1)
            au.init_editor_cam()
            await asyncio.Future()

    loop.run_until_complete(run())

def main():
    ws_thread = threading.Thread(target=start_websocket, daemon=True)
    ws_thread.start()

    app.run()

if (__name__ == '__main__'):
    main()