import pyglet
import logging
from collections import namedtuple

logging.basicConfig(level=logging.DEBUG)

class Pos(namedtuple('Pos', ['row', 'column'])):
    """ A position object encodes a row and a column """
    @property
    def left(self):
        return Pos(self.row, self.column-1)
    @property
    def right(self):
        return Pos(self.row, self.column+1)
    @property
    def up(self):
        return Pos(self.row+1, self.column)
    @property
    def down(self):
        return Pos(self.row-1, self.column)

class Direction:
    """ A direction object is a function which modifies a position """
    def __init__(self, name):
        self.name = name
    def __call__(self, pos : Pos):
        """ :rtype : Pos"""
        return getattr(pos, self.name)

class Directions:
    """ The Directions class stores each cardinal direction as a global object"""
    Left = Direction('left')
    Right = Direction('right')
    Up = Direction('up')
    Down = Direction('down')

class BaseObject():
    """ The BaseObject is the parent of all game objects and behaviours.
    It keeps a reference to the game that it is in. """
    def __init__(self):
        self.position = None
        self.game = None
        self.prev_pos = None

    def tick(self):
        pass

    def send_message(self, event:str, *args, **kwargs):
        """ Send a message to this object. If the object is able to handle it,
         i.e. it has a method called on_'event', the method is run."""
        if hasattr(self, 'on_'+event):
            return getattr(self, 'on_'+event)(*args, **kwargs)

    def try_move(self, direction):
        """ Attempt to move to a new position.
        If an object is already there, it is sent a moved_to event.
        The obstacle may move itself out of the way, then return True
        to signify that this object is free to move there."""
        can_move = True
        position = direction(self.position)
        obstacle = self.game.grid.get(position, None)
        if obstacle:
            can_move = obstacle.send_message('moved_to', self, direction)
        if can_move:
            self.game.move(self, position)
        return can_move

    def delete(self):
        """ Delete this object from the grid """
        self.game.delete(self.position)

class Game(object):
    """ The Game handles a grid of BaseObjects, and also tells a graphics engine what to do. """
    def __init__(self):
        self.graphics_engine = None
        self.grid = {}

    def move(self, object : BaseObject, position :Pos):
        """ Move an object to a new position"""
        # Check there is nothing already at the new position
        assert position not in self.grid
        # Delete the object from the grid, then re-add it.
        del self.grid[object.position]
        self.grid[position.row, position.column] = object
        object.position = position

    def delete(self, position : Pos):
        """ Delete the object at a position. """
        obj = self.grid[position]
        del self.grid[position]
        # Let the graphics engine know to no longer draw this object
        if self.graphics_engine: self.graphics_engine.delete(obj)

    def add_object(self, pos:Pos, obj:BaseObject):
        """ Add an object to the grid """
        already_present = self.grid.get(pos, None)
        if not already_present:
            self.grid[pos] = obj
            obj.game = self
            obj.position = Pos(*pos)
            obj.prev_pos = obj.position
            if self.graphics_engine: self.graphics_engine.add_object(obj)

    def tick(self):
        """ Run one step of the game logic """
        positions = sorted(self.grid.keys())
        ticked = {}
        for pos in positions:
            obj = self.grid[pos]
            obj.position = Pos(*pos)
            obj.prev_pos = obj.position
            ticked[obj] = False

        cur_objs = [self.grid[p] for p in positions]

        for obj in cur_objs:
            if ticked[obj] == False:
                ticked[obj] = True
                obj.tick()


