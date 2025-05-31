from ursina import *
import block_voxel as bv
from string_util import *
import block_util
import async_util as au
from enum import Enum

import json_util as ju

import asyncio

import directions
from directions import MoveDirection


class Turtle(bv.Block):
    def __init__(self, coords=(0, 0, 0)):
        super().__init__(
            position=coords,
            hover_text="Turtle",
            texture="resources/turtle_full.png",
            model="resources/turtle_base"
        )
        self.create_wireframe()

    def get_pos_turtle_xz(self, forwardOrBack: bool, distance=1):
        """
        True for forward / False for back
        """

        forward = self.forward.normalized() * distance
        current_pos = self.world_position
        front_pos = None
        if (forwardOrBack):
            front_pos = current_pos - forward
        else:
            front_pos = current_pos + forward
        return Vec3(round(front_pos.x), round(front_pos.y), round(front_pos.z))

    def get_pos_turtle_y(self, upOrDown: bool, distance=1):
        """
        True for up / False for down
        """

        direction = None
        if (upOrDown):
            direction = self.up.normalized() * distance
        else:
            direction = self.down.normalized() * distance

        current_pos = self.world_position
        new_pos = current_pos + direction
        return Vec3(round(new_pos.x), round(new_pos.y), round(new_pos.z))

    def getXZCoords(self, forwardOrBack: bool):
        x, y, z = self.get_pos_turtle_xz(forwardOrBack)
        return (x, y, z)

    def getYCoords(self, upOrDown: bool):
        """
        True for up / False for down
        """

        x, y, z = self.get_pos_turtle_y(upOrDown)
        return (x, y, z)

    def getBlockInFront(self):
        x, y, z = self.getXZCoords(True)
        target = None
        for _, blockList in bv.voxels.items():
            for block in blockList:
                if block.position == (x, y, z):
                    target = block
        return target

    def getBlockAboveBelow(self, upOrDown: bool):
        x, y, z = self.getYCoords(upOrDown)
        target = None
        for _, blocks in bv.voxels.items():
            for block in blocks:
                if block.position == (x, y, z):
                    target = block
        return target

    def updateTurtleRotation(self, dir: bool):
        """
        True for left / False for right
        """

        deg = directions.getRotationValue(dir)
        self.animate('rotation_y', self.rotation_y + deg,
                     duration=0.5, curve=curve.linear)
        set_animation_active(True)
        invoke(lambda: set_animation_active(False), delay=0.5)


class Inventory(Draggable):
    def __init__(self, grid_width, grid_height):
        super().__init__(
            model='quad',
            color=color.clear,
            scale=(grid_width, grid_height),
            origin=(-0.25, 0.25),
            position=(0.5 - .05, 0.5 - .075, 0)
        )
        self.__slots__: list[Slot] = []

    def get_slots(self):
        return self.__slots__


active_slot = None


class Slot(Button):
    def __init__(self, index: str, hover_text: str, button_size: float, parent: Entity, x: int, y: int, spacing: float):
        super().__init__(
            text=index,
            text_size=adapt_text_size(index),
            scale=(button_size, button_size),
            parent=parent,
            position=(
                x * (button_size + spacing),
                -y * (button_size + spacing),
                0
            )
        )
        self.index = int(index)
        self.__hover_text__ = hover_text
        self.__id__ = random.randint(0, 1000)
        self.notif_box = None

    def get_hover_text(self):
        return self.__hover_text__

    def set_hover_text(self, text):
        self.__hover_text__ = text

    def get_id(self):
        return self.__id__

    def on_click(self):
        global active_slot

        if not active_slot:
            active_slot = invButtons[0]
        active_slot.color = color.black
        active_slot = self
        active_slot.color = color.gray

        draw_slot_notification(self.get_hover_text())

        au.sendActionAsync(au.sendAction(
            f"select_slot | {self.index}"), asyncio.get_event_loop())


class Direction(Enum):
    UP = "UP"
    DOWN = "DOWN"
    FORWARD = "FORWARD"


selected_turtle = None
invButtons: list[Slot] = []
animation_active = False


def clear_slot_notification():
    destroy(bv.slot_notification)
    bv.slot_notification = None


def draw_slot_notification(text: str):
    if bv.slot_notification is not None:
        clear_slot_notification()
    bv.slot_notification = bv.Notification(
        text, bg_color=color.black66, destroy_on_click=False)
    bv.slot_notification.position = (0, 0.4, 0)

def redraw_slot_info(text: str):
    clear_slot_notification()
    draw_slot_notification(text)


def get_active_slot():
    return active_slot


def set_active_slot(slot: Slot):
    global active_slot
    active_slot = slot


def get_animation_active():
    return animation_active


def set_animation_active(active: bool):
    global animation_active

    animation_active = active


def create_turtle(cam, coords=(0, 0, 0)):
    global selected_turtle

    selected_turtle = Turtle(coords=coords)

    cam.parent = selected_turtle


def get_selected_turtle():
    return selected_turtle


def moveForwardBack(forwardOrBack: bool, canMove: str):
    move(MoveDirection.FORWARD_BACK, forwardOrBack, canMove)


def moveUpDown(upOrDown: bool, canMove: str):
    move(MoveDirection.UP_DOWN, upOrDown, canMove)


def move(moveDir: MoveDirection, option: bool, canMove: str):
    if 'false' in canMove:
        return
    newCoords = ()
    match moveDir:
        case MoveDirection.UP_DOWN:
            newCoords = selected_turtle.getYCoords(option)
        case MoveDirection.FORWARD_BACK:
            newCoords = selected_turtle.getXZCoords(option)

    selected_turtle.animate_position(
        newCoords, duration=0.5, curve=curve.linear)
    set_animation_active(True)
    invoke(lambda: set_animation_active(False), delay=0.5)


def rotate(leftOrRight: bool):
    selected_turtle.updateTurtleRotation(leftOrRight)


def getBlock(dir: Direction):
    global selected_turtle

    block = None
    match dir:
        case Direction.UP:
            block = selected_turtle.getBlockAboveBelow(True)
        case Direction.DOWN:
            block = selected_turtle.getBlockAboveBelow(False)
        case Direction.FORWARD:
            block = selected_turtle.getBlockInFront()
    return block


def getCoords(dir: Direction, option: bool):
    return selected_turtle.getXZCoords(True) if dir == Direction.FORWARD else selected_turtle.getYCoords(option)


def getDirectionOption(dir: Direction):
    option = None
    match dir:
        case Direction.UP | Direction.FORWARD:
            option = True
        case Direction.DOWN:
            option = False
    return option


def dig(block: bv.Block):
    if block is None:
        return

    if isinstance(block, Turtle):
        return

    block.remove()
    if block.info_box:
        destroy(block.info_box)


def place(oldData: str, newData: str, coords: tuple[int]):
    if oldData == "" or newData == "":
        return

    updateSlotInfo(newData)
    block_util.place(oldData, coords)


def updateSlotInfo(data: str):
    slot = get_active_slot()
    jsonData = ju.loadToJSON(data)
    text = "Empty"
    if jsonData != "Empty":
        name = jsonData["name"]
        count = jsonData["count"]
        text = f"{name} ({count})"
    slot.set_hover_text(text)
    redraw_slot_info(text)
