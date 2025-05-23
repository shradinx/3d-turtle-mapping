from enum import Enum

class MoveDirection(Enum):
    UP_DOWN = 0
    FORWARD_BACK = 1

def getRotationValue(dir: bool):
    """
    True for left / False for right
    """
    return -90 if dir else 90