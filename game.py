import pyglet
import logging
from game_engine import BaseObject, Game, Directions
from sprite_engine import BaseSprite, SpriteGraphicsEngine
import random
logging.basicConfig(level=logging.DEBUG)

class GameObject(BaseObject):
    """ The base SapphireYours object, contains all default properties"""
    isFlat = False
    isCrusher = False
    isEarthJoiner = False

class Falling(GameObject):
    def __init__(self):
        self.falling = False
        super(Falling, self).__init__()

    def tick(self):
        if self.try_move(Directions.Down):
            self.falling = True
        else:
            if self.falling:
                self.falling = False
            else:
                obj_below = self.game.grid[self.position.down]
                if obj_below.isFlat == False:
                    for direction in (Directions.Left, Directions.Right):
                        if not direction(self.position) in self.game.grid and not direction(self.position).down in self.game.grid:
                            if self.try_move(direction):
                                break
        super(Falling, self).tick()

class Crushable(GameObject):
    def on_moved_to(self, sender, direction):
        if isinstance(sender, Falling) and sender.isCrusher and sender.falling:
            self.delete()
            return True
        return False


class Player(GameObject):
    def on_keyboard_input(self, sender, key):
        pass

#### Define Sapphire Yours game objects ####

class Wall(GameObject):
    isFlat = True
    isEarthJoiner = True
class Stone(Falling):
    isCrusher = True
class Sapphire(Falling, Crushable):
    pass
class Emerald(Falling):
    def __init__(self):
        self.beingUnbagged = False
        super(Emerald, self).__init__()
    def tick(self):
        if self.beingUnbagged:
            self.beingUnbagged = False
        super(Emerald, self).tick()
class Earth(GameObject):
    isEarthJoiner = True
    isFlat = True
    def __init__(self):
        self.adjacenct_earth = 0
        super(Earth, self).__init__()
    def tick(self):
        self.adjacenct_earth = 0
        for pos, num in zip([self.position.down, self.position.up, self.position.left, self.position.right], [1, 2, 4, 8]):
            obj = self.game.grid.get(pos, None)
            if obj and obj.isEarthJoiner:
                self.adjacenct_earth += num
        super(Earth, self).tick()

class Bag(Falling):
    def on_moved_to(self, sender, direction):
        if isinstance(sender, Falling) and sender.isCrusher and sender.falling:
            pos = self.position
            self.delete()
            emerald = Emerald()
            emerald.beingUnbagged = True
            self.game.add_object(pos, emerald)
        return False


class RollSprite(BaseSprite):
    def __init__(self, engine):
        self._f = 0
        super(RollSprite, self).__init__(engine)
    def update(self, obj : BaseObject, frame:float):
        grid_frame = 0
        if obj.prev_pos == obj.position.right:
            grid_frame = int(self.numFrames*frame)
        elif obj.prev_pos == obj.position.left:
            grid_frame = int(self.numFrames - self.numFrames*frame-1)
        self.frame = grid_frame
        super(RollSprite, self).update(obj, frame)

class WallSprite(BaseSprite):
    default_image = "wall.png"
class StoneSprite(RollSprite):
    default_image = "stone.png"
class SapphireSprite(RollSprite):
    default_image = "sapphire.png"
class EmeraldSprite(RollSprite):
    default_image = "emerald.png"
    from_bag_image = "bagexpl.png"
    def update(self, obj : Emerald, frame:float):
        super(EmeraldSprite, self).update(obj, frame)
        if obj.beingUnbagged == True:
            self.image = self.from_bag_image
            self.frame = int((self.numFrames-1)*(1-frame))
        else:
            self.image = "emerald.png"
class BagSprite(RollSprite):
    default_image = "bag.png"
class EarthSprite(BaseSprite):
    default_image = "earth.png"
    #adjacency_conversion = [15, 14, 13, 10, 12, 9, 7, 3, 11, 6, 8, 4, 5, 1, 2 , 0]
    adjacency_conversion = [15, 13, 14, 10, 12, 7, 9, 4, 11, 6, 8, 3, 5, 1, 2, 0]
    def update(self, obj : Earth, frame:float):
        self.frame = self.adjacency_conversion[obj.adjacenct_earth]
        super(EarthSprite, self).update(obj, frame)



class Runner(object):
    def __init__(self, game, graphics_engine):
        self.graphics_engine = graphics_engine
        self.game = game
        self.game.graphics_engine = graphics_engine

        for c in range(40):
            game.add_object((0, c-20), Wall())
        for r in range(30):
            game.add_object((random.randint(0, 20), random.randint(0, 20)), Earth())
        for r in range(30):
            choice = random.randint(0, 2)
            if choice == 0:
                game.add_object((6+r, 8), Stone())
            elif choice == 1:
                game.add_object((6+r, 8), Bag())
            elif choice == 2:
                game.add_object((6+r, 8), Sapphire())


    def run(self):
        tick_counter = 0
        def tick(dt):
            nonlocal tick_counter, self
            tick_counter += 1
            n_ticks = 10

            if tick_counter == n_ticks:
                tick_counter = 0
                self.game.tick()
            self.graphics_engine.update(tick_counter/n_ticks)

        pyglet.clock.schedule_interval(tick, 1/60)
        pyglet.app.run()

def main():
    Runner(Game(), SpriteGraphicsEngine()).run()

if __name__ == '__main__':
    main()