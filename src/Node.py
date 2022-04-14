import Rhino.Geometry as rg
from Rhino.Geometry import Point3d as Point
from Rhino.Geometry import Vector3d as Vector
from Rhino.Geometry import Line
from parameters import length

class Node(object):
    """
    Represents a node(branch) in the tree
    ------------------
    position    : Point3d
    parent      : self
    direction   : Vector3d
    """

    def __init__(self, parent, position, is_tip):
        self.position = position
        self.parent = parent
        self.is_tip = is_tip
        self.root = None
        self.influenced_by = []
        self.thickness = 0.0
    
    def next(self, average_direction):
        self.is_tip = False
        next_position = self.position + average_direction*length
        next_branch = Node(self, next_position, True)
        return next_branch

    def draw(self):
        line = Line(Point(self.parent.position), Point(self.position)) if self.parent is not None else None
        return line
