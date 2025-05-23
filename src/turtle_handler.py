from ursina import *
from block_voxel import *
import block_util
from enum import Enum

import directions
from directions import MoveDirection


class Turtle(Block):
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
        for _, blockList in voxels.items():
            for block in blockList:
                if block.position == (x, y, z):
                    target = block
        return target

    def getBlockAboveBelow(self, upOrDown: bool):
        x, y, z = self.getYCoords(upOrDown)
        target = None
        for _, block in voxels.items():
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


class Direction(Enum):
    UP = "UP"
    DOWN = "DOWN"
    FORWARD = "FORWARD"

selected_turtle = None
turtles = []
animation_active = False


def get_animation_active():
    return animation_active


def set_animation_active(active: bool):
    global animation_active

    animation_active = active


def create_turtle(cam, coords=(0, 0, 0)):
    global selected_turtle

    selected_turtle = Turtle(coords=coords)
    turtles.append(selected_turtle)

    cam.parent = selected_turtle
    """ camera.position = (0, 15, 10)
    camera.look_at(selected_turtle) """


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
    return selected_turtle.getXZCoords(option) if dir == Direction.FORWARD else selected_turtle.getYCoords(option)

def getDirectionOption(dir: Direction):
    option = None
    match dir:
        case Direction.UP, Direction.FORWARD:
            option = True
        case Direction.DOWN:
            option = False
    return option


def dig(block: Block):
    if block is None:
        return

    if isinstance(block, Turtle):
        return

    block.remove()


def place(blockData: str, coords: tuple[int]):
    if blockData == "":
        return

    block_util.place(blockData, coords)
