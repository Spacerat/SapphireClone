import logging
import pyglet
import os
from pyglet.gl import *

class ResourceManager(object):
    image_grid = {}
    base_dir = "resources"
    @classmethod
    def get_grid(cls, name):
        try:
            return cls.image_grid[name]
        except KeyError:
            path = os.path.join(cls.base_dir, name)
            logging.info("Loading: %s" % path)

            img = pyglet.image.load(path)
            grid = pyglet.image.ImageGrid(img, 1, int(img.width / img.height))
            cls.image_grid[name] = grid
            return grid


sprite_classes = {}
class SpriteGraphicsType(type):
    def __init__(cls, name, bases, dct):
        if not name.startswith("Base"):
            if not name.endswith("Sprite"):
                raise Exception("Sprite class must end with name 'Sprite'")
            sprite_for = name[0:-6]
            sprite_classes[sprite_for] = cls
        super(SpriteGraphicsType, cls).__init__(name, bases, dct)


class BaseSprite(object, metaclass=SpriteGraphicsType):
    default_image = ''
    def __init__(self, engine):
        self._frame = 0
        self._image = ""
        self.sprite = None
        self.grid = None
        self.engine = engine
        self.image = self.default_image

    @property
    def frame(self):
        return self._frame

    @frame.setter
    def frame(self, frame):
        self._frame = frame
        if self.sprite:
            self.sprite.image = self.grid[frame]

    @property
    def image(self):
        return self._image

    @property
    def numFrames(self):
        return self.grid.columns

    @image.setter
    def image(self, value):
        if self._image != value:
            self._image = value
            self.grid = ResourceManager.get_grid(value)
            img = self.grid[self.frame]
            try:
                self.sprite.image = img
            except AttributeError:
                self.sprite = pyglet.sprite.Sprite(img, batch = self.engine.batch)

    def update_sprite_position(self, obj, frame):
        p_x = self.engine.grid_size * obj.prev_pos.column
        p_y = self.engine.grid_size * obj.prev_pos.row
        n_x = self.engine.grid_size * obj.position.column
        n_y = self.engine.grid_size * obj.position.row
        if self.sprite:
            self.sprite.x = p_x + (n_x - p_x)*frame
            self.sprite.y = p_y + (n_y - p_y)*frame


    def delete(self):
        if self.sprite:
            self.sprite.delete()

    def update(self, obj, frame):
        pass


class BaseGraphicsEngine(object):
    def delete(self, obj): pass
    def update(self, frame): pass
    def draw(self): pass
    def add_object(self, obj): pass

class SpriteGraphicsEngine(BaseGraphicsEngine):
    grid_size = 60
    def __init__(self):
        self.window = pyglet.window.Window(1024, 768)

        self.batch = pyglet.graphics.Batch()
        self.sprites = {}

        @self.window.event
        def on_draw():
            self.draw()

    def delete(self, obj):
        sprite = self.sprites[obj]
        del self.sprites[obj]
        sprite.delete()

    def update(self, frame):
        for obj, sprite in self.sprites.items():
            sprite.update(obj, frame)
            sprite.update_sprite_position(obj, frame)

    def draw(self):
        self.window.clear()
        self.batch.draw()

    def add_object(self, obj):
        obj_class = type(obj).__name__
        try:
            cls = sprite_classes[obj_class]
            self.sprites[obj] = cls(self)
        except KeyError:
            raise Exception("Missing sprite class for object {}".format(obj_class))
