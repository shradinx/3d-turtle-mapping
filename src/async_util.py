import asyncio
import websockets
import turtle_handler
import json_util as ju
from turtle_handler import *

active_websocket = None

movementActions = {
    "turn_left": [turtle_handler.rotate, True],
    "turn_right": [turtle_handler.rotate, False],
    "forward": [turtle_handler.moveForwardBack, True, ""],
    "back": [turtle_handler.moveForwardBack, False, ""],
    "up": [turtle_handler.moveUpDown, True, ""],
    "down": [turtle_handler.moveUpDown, False, ""]
}

buttonActions = {
    "inspect": "Inspect Block",
    "inspect_up": "Inspect Block Up",
    "inspect_down": "Inspect Block Down",
    "dig": "Dig Block",
    "dig_up": "Dig Block Above",
    "dig_down": "Dig Block Below",
    "place": "Place Block",
    "place_up": "Place Block Above",
    "place_down": "Place Block Below"
}

WIP_actions = {}

blockBreakActions = {
    "dig": [turtle_handler.dig, turtle_handler.Direction.FORWARD],
    "dig_up": [turtle_handler.dig, turtle_handler.Direction.UP],
    "dig_down": [turtle_handler.dig, turtle_handler.Direction.DOWN]
}

blockPlaceActions = {
    "place": [turtle_handler.place, turtle_handler.Direction.FORWARD],
    "place_up": [turtle_handler.place, turtle_handler.Direction.UP],
    "place_down": [turtle_handler.place, turtle_handler.Direction.DOWN]
}

inspectActions = {
    "inspect": [block_util.placeFrontBack, True, ""],
    "inspect_up": [block_util.placeAboveBelow, True, ""],
    "inspect_down": [block_util.placeAboveBelow, False, ""]
}

invActions = {
    "select_slot": turtle_handler.updateSlotInfo
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
                fail_reason = rest[0]
                if bv.notification is None:
                    bv.notification = bv.Notification(fail_reason, bg_color=color.red)
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
    t = turtle_handler.get_selected_turtle()
    coords = t.getXZCoords(True) if t is not None else (0, 0, 0)
    turtle_handler.create_turtle(ec, coords)

def sendActionAsync(coroutine, loop):
    return asyncio.run_coroutine_threadsafe(coroutine, loop)

async def sendAction(action: str):
    if not active_websocket:
        if bv.notification is None:
            bv.notification = bv.Notification("No active connection!", bg_color=color.red)
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
        block = turtle_handler.getBlock(dir)
        func(block)

        return True
    elif action in blockPlaceActions.keys():
        func, dir = blockPlaceActions[action]
        option = turtle_handler.getDirectionOption(dir)

        value = ju.getValueFromJSON(data, "count")
        if not value:
            return False
        
        newData = "Empty" if value-1 <= 0 else ju.modifyJSON(data, "count", int(value)-1, dumpToString=True)

        coords = turtle_handler.getCoords(dir, option)
        func(data, newData, coords)

        return True
    elif action in inspectActions.keys():
        func, boolArg, *rest = inspectActions[action]
        func(boolArg, data)

        return True
    
    return False