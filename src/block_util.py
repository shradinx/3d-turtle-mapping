from ursina import *
import json

import block_voxel
from block_voxel import Block

import turtle_handler as th

def create(blockData: str, coords: tuple[int]):
    jsonData = json.loads(blockData)
    name = jsonData["name"]

    c = color.random_color()
    for blockColor, blockList in block_voxel.get_voxels().items():
        for block in blockList:
            if block.get_hover_text() == name:
                c = blockColor
                break
    
    block = Block(hover_text=name, position=coords,
                color=c, transparent=True)
    return block

def placeFrontBack(frontOrBack: bool, blockData: str):
    place(blockData, th.get_selected_turtle().getXZCoords(frontOrBack))

def placeAboveBelow(upOrDown: bool, blockData: str):
    place(blockData, th.get_selected_turtle().getYCoords(upOrDown))

def place(blockData: str, coords: tuple[int]):
    if (blockData == '"No block to inspect"'):
        return
    try:
        for _, bList in block_voxel.get_voxels().items():
            for b in bList:
                if b.position == coords:
                    return
        create(blockData, coords)
    except ValueError as e:
        print(f"[WebSocket] ValueError: {e}")
    except Exception as e:
        print(f"[Exception] {e}")