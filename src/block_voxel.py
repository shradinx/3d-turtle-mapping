from ursina import *

class Block(Button):
    def __init__(self, hover_text: str = None, texture=None, model='cube', position=(0, 0, 0), rotation=(0, 0, 0), color=color.white, transparent=False):
        super().__init__(
            parent=scene,
            position=position,
            model=model,
            color=color
        )

        if texture is not None:
            self.texture = texture
        if model != 'cube':
            self.origin_y_setter(self.origin_y_getter()+0.5)

        self.__wireframe__ = None
        self.rotation = rotation
        self.__hover_text__ = hover_text
        self.__id__ = random.randint(0, 1000)
        self.__color__ = color
        self.info_box = None

        if transparent:
            self.alpha_setter(0.5)

        self.create_wireframe()

        blocks: list[Block] = voxels.get(color, [])
        blocks.append(self)
        voxels.update({color: blocks})

    def create_wireframe(self):
        e = Entity(model='cube', color=color.black, scale=1.05, parent=self)
        e.wireframe = True
        self.__wireframe__ = e

    def get_wireframe(self):
        return self.__wireframe__

    def set_wireframe(self, wireframe: Entity):
        self.__wireframe__ = wireframe

    def on_mouse_enter(self):
        if not self.get_hover_text():
            return super().on_mouse_enter()

        if not self.info_box:
            self.info_box = InfoBox(self.get_hover_text(), id=self.get_id())
        
        return super().on_mouse_enter()

    def on_mouse_exit(self):
        if self.info_box:
            destroy_entity(self.info_box)
            self.info_box = None

    def get_id(self):
        return self.__id__

    def get_hover_text(self):
        return self.__hover_text__

    def get_color(self):
        return self.__color__
    
    def remove(self):
        blocks: list[Block] = voxels.get(self.get_color())
        blocks.remove(self)
        if len(blocks) == 0:
            voxels.pop(self.get_color())
                
        destroy_entity(self)


class InfoBox(Text):
    def __init__(self, text: str, id: int = random.randint(0, 1000), bg_color=color.dark_gray, t_color=color.white):
        super().__init__(
            text=text,
            color=t_color,
            parent=camera.ui,
            position=mouse.position
        )
        self.__id__ = id

        self.create_background(color=bg_color)

    def get_id(self):
        return self.__id__


class Notification(Button):
    def __init__(self, text: str, bg_color=color.dark_gray, t_color=color.white, destroy_on_click=True):
        super().__init__(
            text=text,
            color=bg_color,
            scale=(0.3, 0.075)
        )
        self.destroy_on_click = destroy_on_click
        self.text_entity.color = t_color
        self.id = random.randint(1, 1000)

    def on_click(self):
        global notification
        if not self.destroy_on_click:
            return
        
        notification = None
        destroy(self)

    
voxels: dict[color.Color, list[Block]] = {}
text_boxes: list[InfoBox] = []
notification = None
slot_notification = None

def destroy_entity(entity):
    destroy(entity=entity)

def get_voxels() -> dict[color.Color, list[Block]]:
    return voxels


def get_text_boxes() -> list[InfoBox]:
    return text_boxes


def get_notification() -> Notification:
    return notification
