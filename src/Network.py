from random import random, randrange, uniform
import Rhino.Geometry as rg
from Rhino.Geometry import Point3d as Point
from Rhino.Geometry import Vector3d as Vector
from Rhino.Geometry import Line


class Network(object):
    def __init__(self, v_type):
        self.attractors = []
        self.nodes = []
        self.venation = v_type
        self.tolerance = None

        self.attraction_distance = None
        self.kill_distance = None
        self.node_list = []

    def update(self):
        for attractor in self.attractors:
            if self.venation == 'open':
                closest_node = self.get_closest_node(
                    attractor, self.get_nodes_in_range(attractor))
                if closest_node is not None:
                    closest_node.influenced_by.append(attractor)
                    attractor.influencing_nodes = [closest_node]

            else:
                neighboring_nodes = self.get_relative_neighborhood(attractor)
                nodes_too_close = self.get_too_close_nodes(attractor)

                nodes_to_grow = [
                    n for n in neighboring_nodes if n not in nodes_too_close]
                attractor.influencing_nodes = neighboring_nodes

                if len(nodes_to_grow) > 0:
                    attractor.fresh = False
                    for node in nodes_to_grow:
                        node.influenced_by.append(attractor)

        # grow
     
        for node in self.nodes:
            if len(node.influenced_by) > 0:
                average_direction = self.get_average_direction(
                    node, node.influenced_by)
                next_node = node.next(average_direction)
                self.nodes.append(next_node)

            node.influenced_by = []
            node_set = []
            if node.is_tip:
                current_node = node
                while current_node.parent is not None:
                    if current_node.parent.thickness < current_node.thickness + 0.1:
                        current_node.parent.thickness = current_node.thickness + 0.05
                        node_set.append(current_node)
                    current_node = current_node.parent

        for attractor in self.attractors:
            if self.venation == 'open':
                if attractor.reached:
                    self.attractors.remove(attractor)
            else:
                if len(attractor.influencing_nodes) > 0 and not attractor.fresh:
                    all_nodes_reached = True
                    for node in attractor.influencing_nodes:
                        if node.position.DistanceTo(attractor.position) > self.kill_distance:
                            all_nodes_reached = False

                    if all_nodes_reached:
                        self.attractors.remove(attractor)

    def draw(self):
        network_lines = []
        thicknessses = []
        for node in self.nodes:
            network_lines.append(node.draw())
            thicknessses.append(node.thickness)
        return network_lines, thicknessses

    def branch_tree(self):
        root_count = 1
        roots = []
        for node in self.nodes:
            if node.is_tip:
                current_node = node
                while current_node.parent is not None:
                    root = current_node.parent
                    current_node = current_node.parent
                current_node = node      
                while current_node.parent is not None:
                    current_node.root = root
                    current_node = current_node.parent    
        
        roots = [n for n in self.nodes if n.root is None]
        #roots.append(root0)

        root_tree = []
        
        for root in roots:
            root_grp = []
            for node in self.nodes:
                if node.root is root:
                    root_grp.append(node.draw())
            root_tree.append(root_grp)
        
        return root_tree

    def distance_to_nodes(self, node, attractor):
        return Point.DistanceTo(Point(node.position), Point(attractor.position))

    def get_relative_neighborhood(self, attractor):
        close_branches = self.get_nodes_in_range(attractor)
        relative_neighbors = []
        for p0 in close_branches:
            fail = False
            dist_p0 = Vector(attractor.position - p0.position).Length
            for p1 in close_branches:
                if p1 != p0:
                    dist_p1 = Vector(attractor.position - p1.position).Length
                    if dist_p1 > dist_p0:
                        continue
                    p0_to_p1 = Vector(p1.position - p0.position).Length
                    if dist_p0 > p0_to_p1:
                        fail = True
                        break
            if not fail:
                relative_neighbors.append(p0)

        return relative_neighbors

    def get_nodes_in_range(self, attractor):
        node_list = []
        for node in self.nodes:
            if self.distance_to_nodes(node, attractor) < self.attraction_distance:
                node_list.append(node)
        return node_list

    def get_too_close_nodes(self, attractor):
        closer_branches = []
        for node in self.nodes:
            if self.distance_to_nodes(node, attractor) < self. kill_distance:
                closer_branches.append(node)
        return closer_branches

    def get_closest_node(self, attractor, neighboring_nodes):
        closest_node = None
        record = self.attraction_distance

        for node in neighboring_nodes:
            distance = self.distance_to_nodes(node, attractor)
            if distance < self.kill_distance:
                attractor.reached = True
                closest_node = None
            elif distance < record:
                closest_node = node
                record = distance
        return closest_node

    def get_average_direction(self, node, close_attractors):
        average_direction = Vector(0, 0, 0)

        for attractor in close_attractors:
            average_direction = Vector.Add(
                average_direction, (Vector(attractor.position)-Vector(node.position)))
            average_direction.Unitize()

        # Jitter
        average_direction = Vector.Add(average_direction, Vector(
            uniform(-0.1, 0.1), uniform(-0.1, 0.1), 0.0))
        average_direction.Unitize()

        average_direction /= len(node.influenced_by)
        average_direction.Unitize()

        return average_direction

    def close_ends(self):
        tip_nodes = [node for node in self.nodes if node.is_tip]
        for n0 in tip_nodes:
            for n1 in tip_nodes:
                if n0 is not n1:
                    dist = self.distance_to_nodes(n0,n1)
                    if dist<self.tolerance and dist>0.25:
                        direction = Vector(n1.position-n0.position)
                        new_node = n0.next(direction)
                        self.nodes.append(new_node)
                

    def add_node(self, node):
        self.nodes.append(node)
