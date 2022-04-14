import Rhino.Geometry as rg
from Rhino.Geometry import Point3d as Point
from Rhino.Geometry import Vector3d as Vector
from Rhino.Geometry import Line


class Attractor(object):
    """
    Represents a attractor(leaf) in the tree that
    the branches would grow towards
    -----------------------
    self.position           : Point3d
    self.reached            : bool
    self.influencing nodes  : Nodes the attractor is influencing
    """

    def __init__(self, position):
        self.position = position
        self.reached = False
        self.influencing_nodes = []
        self.fresh = True

    def draw(self):
        return Point(self.position)
