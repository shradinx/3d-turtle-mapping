import turtle_handler
from block_voxel import *
import block_voxel
import block_util
import asyncio
import websockets
import threading

from ursina import *

active_websocket = None

window.borderless = False
app = Ursina(title="Interactive 3D Environment: Integration with ComputerCraft Turtles")

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

host = "0.0.0.0"
port = 8000

movementActions = {
    "turn_left": [turtle_handler.rotate, True],
    "turn_right": [turtle_handler.rotate, False],
    "forward": [turtle_handler.moveForwardBack, True, ""],
    "back": [turtle_handler.moveForwardBack, False, ""],
    "up": [turtle_handler.moveUpDown, True, ""],
    "down": [turtle_handler.moveUpDown, False, ""],
}

buttonActions = {
    "inspect": "Inspect Block",
    "inspect_up": "Inspect Block Up",
    "inspect_down": "Inspect Block Down",
    "dig": "Dig Block",
    "dig_up": "Dig Block Above",
    "dig_down": "Dig Block Below"
}

WIP_actions = {
    "place": "Place Block",
    "place_up": "Place Block Above",
    "place_down": "Place Block Below"
}

blockBreakActions = {
    "dig": [turtle_handler.dig, turtle_handler.Direction.FORWARD],
    "dig_up": [turtle_handler.dig, turtle_handler.Direction.UP],
    "dig_down": [turtle_handler.dig, turtle_handler.Direction.DOWN],
}

blockPlaceActions = {
    "place": [turtle_handler.place, turtle_handler.Direction.FORWARD],
    "place_up": [turtle_handler.place, turtle_handler.Direction.UP],
    "place_down": [turtle_handler.place, turtle_handler.Direction.DOWN]
}

inspectActions = {
    "inspect": [block_util.placeFrontBack, True, ""],
    "inspect_up": [block_util.placeAboveBelow, True, ""],
    "inspect_down": [block_util.placeAboveBelow, False, ""],
}

ec = EditorCamera()

actionMenu = Entity(parent=camera.ui)

def sendActionAsync(coroutine, loop):
    return asyncio.run_coroutine_threadsafe(coroutine, loop)

async def sendAction(action: str):
    if not active_websocket:
        if len(notifications) == 0:
            Notification("No active connection!", bg_color=color.red)
        return
    
    if (action in movementActions) and turtle_handler.get_animation_active():
        return
    
    if re.search("dig", action):
        split = action.split("_")

        msg = action
        block = None

        if len(split) == 1:
            block = turtle_handler.get_selected_turtle().getBlockInFront()
        else:
            dir = split[1].upper()
            dirEnum = turtle_handler.Direction(dir)
            if dirEnum is None:
                return
            
            block = turtle_handler.getBlock(dirEnum)

        msg = msg + " | " + str((block is not None))
        await active_websocket.send(msg)
    else:
        await active_websocket.send(action)



def createAxes(text: str, color=color.white, position=(0, 0, 0), text_pos=(0, 0, 0), scale=(0, 0, 0)):
    axis_obj = Entity(
        parent=axis,
        model='cube',
        color=color,
        scale=scale,
        position=position
    )
    axis_text_obj = Text(
        world_parent=axis_obj,
        text=text,
        position=text_pos
    )


axis = Entity(parent=turtle_handler.get_selected_turtle())
axis.world_rotation = Vec3(0, 0, 0)

createAxes(text="X", color=color.red, position=(1, 0, 0),
           text_pos=(0.1, 0.02), scale=(2, 0.05, 0.05))

createAxes(text="Y", color=color.green, position=(0, 1, 0),
           text_pos=(0.02, 0.1), scale=(0.05, 2, 0.05))

createAxes(text="Z", color=color.blue, position=(0, 0, 1),
           text_pos=(0.02, 0.02, 0.25), scale=(0.05, 0.05, 2))


def center_text(text: dict[tuple[float, int], Text]):
    def _():
        for k, v in text.items():
            v.origin = k
    invoke(_, delay=0)


def update():
    if (mouse.hovered_entity):
        for tb in block_voxel.get_text_boxes():
            screen_pos = world_position_to_screen_position(
                mouse.hovered_entity.world_position
            )
            tb.position = screen_pos


def input(key):
    action = None
    match key:
        case 'w':
            action = "forward"
        case 's':
            action = "back"
        case 'a':
            action = "turn_left"
        case 'd':
            action = "turn_right"
        case 'space':
            action = "up"
        case 'left shift':
            action = "down"
    if action is not None:
        sendActionAsync(sendAction(action), loop)


async def handshake(websocket: websockets.ServerConnection):
    global active_websocket

    print("[WebSocket] Client Connected!")
    active_websocket = websocket

    await websocket.send("handshake")

    try:
        async for message in websocket:
            if (message == "CLIENT_ERROR"):
                await websocket.close()
                return
            
            try:
                action, data, *rest = message.split('|')
                if rest:
                    fail_reason = rest[0]
                    if len(notifications) == 0:
                        Notification(fail_reason, bg_color=color.red)
            except ValueError:
                print(f"[WebSocket] Invalid message format: {message}")

            print(f"[WebSocket] Action: {action}")
            print(f"[WebSocket] Response Data: {data}")

            if (action == "handshake" and data == "Yes"):
                handle_handshake()
                continue
            
            result = handle_action(action, data)
            if not result:
                print(f"[WebSocket] Unknown or improper action config: {action}")
    except websockets.exceptions.ConnectionClosed:
        print("[WebSocket] Client Disconnected!")
        await websocket.close()
        return
    finally:
        active_websocket = None

def handle_handshake():
    t = turtle_handler.get_selected_turtle()
    coords = t.getXZCoords(True) if t is not None else (0, 0, 0)
    turtle_handler.create_turtle(ec, coords)

def handle_action(action, data):
    if action in movementActions.keys():
        func, boolArg, *rest = movementActions[action]

        if (rest):
            func(boolArg, data)
        else:
            func(boolArg)

        return True
    elif action in blockBreakActions.keys():
        func, dir = blockBreakActions[action]
        block = turtle_handler.getBlock(dir)
        func(block)

        return True
    elif action in blockPlaceActions.keys():
        func, dir = blockPlaceActions[action]

        block = turtle_handler.getBlock(dir)
        option = turtle_handler.getDirectionOption(dir)

        if option is None:
            return False
        
        coords = turtle_handler.getCoords(dir, option)
        func(data, coords)

        return True
    elif action in inspectActions.keys():
        func, boolArg, *rest = inspectActions[action]
        func(boolArg, data)

        return True
    
    return False

button_scale = (0.25, 0.075)
text = {
    (-0.54, 0): Text(text="Use W,S for forward/back movement...", origin=(0, 0), scale=1),
    (-0.7, 0): Text(text="Use A,S for left/right rotation...", origin=(0, 0), scale=1)
}


def get_buttons():
    for k, v in buttonActions.items():
        yield Button(
            text=v,
            scale=button_scale,
            on_click=lambda k=k: sendActionAsync(sendAction(k), loop)
        )

def get_wip_buttons():
    for k, v in WIP_actions.items():
        yield Button(
            text=v,
            scale=button_scale
            # on_click=lambda k=k: sendActionAsync(sendAction(k), loop)
        )

t = Text(text="WIP Buttons", origin=(0, 0), scale=1)
def center_wip():
    t.origin = (-0.55, 0)

def start_websocket():
    async def run():
        async with websockets.serve(handshake, host, port) as ws:
            print(f"[WebSocket] Server started on ws://{host}:{port}")

            def make_buttons():
                WindowPanel(
                    parent=actionMenu,
                    title="Actions Menu",
                    x=-0.6,
                    y=0.4,
                    content=[
                        *text.values(),
                        *get_buttons(),
                        t,
                        *get_wip_buttons()
                    ]
                )
                center_text(text)
                center_wip()

            invoke(make_buttons, delay=0.1)
            await asyncio.Future()

    loop.run_until_complete(run())


def main():
    ws_thread = threading.Thread(target=start_websocket, daemon=True)
    ws_thread.start()

    app.run()

if (__name__ == '__main__'):
    main()