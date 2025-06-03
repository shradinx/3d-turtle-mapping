from imports import *

import turtle_handler as th
import block_util as bu
import json_util as ju
import gui_util as gu

active_websocket = None

movementActions = {
    "turn_left": [th.rotate, True],
    "turn_right": [th.rotate, False],
    "forward": [th.moveForwardBack, True, ""],
    "back": [th.moveForwardBack, False, ""],
    "up": [th.moveUpDown, True, ""],
    "down": [th.moveUpDown, False, ""]
}

buttonActions = {
    "inspect": "Inspect Block",
    "inspect_up": "Inspect Block Up",
    "inspect_down": "Inspect Block Down",
    "auto_inspect": "Inspect All",
    "dig": "Dig Block",
    "dig_up": "Dig Block Above",
    "dig_down": "Dig Block Below",
    "place": "Place Block",
    "place_up": "Place Block Above",
    "place_down": "Place Block Below"
}

WIP_actions = {}

blockBreakActions = {
    "dig": [th.dig, th.Direction.FORWARD],
    "dig_up": [th.dig, th.Direction.UP],
    "dig_down": [th.dig, th.Direction.DOWN]
}

blockPlaceActions = {
    "place": [th.place, th.Direction.FORWARD],
    "place_up": [th.place, th.Direction.UP],
    "place_down": [th.place, th.Direction.DOWN]
}

inspectActions = {
    "inspect": [bu.placeFrontBack, True, ""],
    "inspect_up": [bu.placeAboveBelow, True, ""],
    "inspect_down": [bu.placeAboveBelow, False, ""]
}

invActions = {
    "select_slot": th.updateSlotInfo
}

ec = None

def init_editor_cam():
    global ec
    ec = EditorCamera()

def get_active_websocket():
    return active_websocket

def set_active_websocket(ws: websockets.ServerConnection):
    global active_websocket
    active_websocket = ws

host = "0.0.0.0"
port = 8000

def start_websocket(loop: asyncio.AbstractEventLoop, actionMenu: Entity):
    async def run():
        async with websockets.serve(handshake, host, port) as ws:
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
            init_editor_cam()
            await asyncio.Future()

    loop.run_until_complete(run())


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
            except ValueError:
                print(f"[WebSocket] Invalid message format: {message}")

            print(f"[WebSocket] Action: {action}")
            print(f"[WebSocket] Response Data: {data}")

            if rest:
                continue

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
    t = th.get_selected_turtle()
    coords = t.getXZCoords(True) if t is not None else (0, 0, 0)
    th.create_turtle(ec, coords)

def sendActionAsync(coroutine, loop: asyncio.AbstractEventLoop):
    return asyncio.run_coroutine_threadsafe(coroutine, loop)

async def sendAction(action: str, delay=None):
    if not active_websocket:
        return
    
    if (action in movementActions) and th.get_animation_active():
        return
    
    if delay is not None:
        await asyncio.sleep(delay)
    
    if re.search("dig", action):
        split = action.split("_")

        msg = action
        block = None

        if len(split) == 1:
            block = th.get_selected_turtle().getBlockInFront()
        else:
            dir = split[1].upper()
            dirEnum = th.Direction(dir)
            if dirEnum is None:
                return
            
            block = th.getBlock(dirEnum)

        msg = msg + " | " + str((block is not None))
        await active_websocket.send(msg)
    elif re.search("auto_inspect", action):
        await th.autoInspect()
    else:
        await active_websocket.send(action)

def handle_action(action: str, data: str):
    if action in invActions.keys():
        func = invActions[action]
        func(data)
        
        return True
    elif action in movementActions.keys():
        func, boolArg, *rest = movementActions[action]

        if (rest):
            func(boolArg, data)
        else:
            func(boolArg)
        return True
    elif action in blockBreakActions.keys():
        func, dir = blockBreakActions[action]
        block = th.getBlock(dir)
        func(block)

        return True
    elif action in blockPlaceActions.keys():
        func, dir = blockPlaceActions[action]
        option = th.getDirectionOption(dir)

        value = ju.getValueFromJSON(data, "count")
        if value is None:
            return False
        
        newData = "Empty" if value-1 <= 0 else ju.modifyJSON(data, "count", int(value)-1, dumpToString=True)

        coords = th.getCoords(dir, option)
        func(data, newData, coords)

        return True
    elif action in inspectActions.keys():
        func, boolArg, *rest = inspectActions[action]
        func(boolArg, data)

        return True
    
    return False