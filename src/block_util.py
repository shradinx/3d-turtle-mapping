from imports import *

import json_util as ju
import block_voxel as bv
import turtle_handler as th
import async_util as au


def create(blockData: str, coords: tuple[int]):
    jsonData = ju.loadToJSON(blockData)
    if jsonData is None:
        return

    name = jsonData["name"]
    c = color.random_color()

    for blockColor, blockList in bv.get_voxels().items():
        for block in blockList:
            if block.get_hover_text() == name:
                c = blockColor
                break

    block = bv.Block(hover_text=name, position=coords,
                     color=c, transparent=True)
    block.on_click_setter(Func(on_block_click, block))

    return block


def placeFrontBack(frontOrBack: bool, blockData: str):
    place(blockData, th.get_selected_turtle().getXZCoords(frontOrBack))


def placeAboveBelow(upOrDown: bool, blockData: str):
    place(blockData, th.get_selected_turtle().getYCoords(upOrDown))


def place(blockData: str, coords: tuple[int]):
    if (blockData == '"No block to inspect"'):
        return
    try:
        for _, bList in bv.get_voxels().items():
            for b in bList:
                if b.position == coords:
                    return
        create(blockData, coords)
    except ValueError as e:
        print(f"[WebSocket] ValueError: {e}")


def on_block_click(block: bv.Block):
    if isinstance(block, th.Turtle):
        return

    turtle = th.get_selected_turtle()

    tBlock = turtle.getBlockInFront()
    action = "dig"

    if tBlock is None:
        tBlock = turtle.getBlockAboveBelow(True)
        action = "dig_up"

    if tBlock is None:
        tBlock = turtle.getBlockAboveBelow(False)
        action = "dig_down"

    if tBlock.position == block.position:
        au.sendActionAsync(au.sendAction(action), asyncio.get_event_loop())
