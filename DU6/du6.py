
from typing import List
from collections import namedtuple
from operator import attrgetter
import numpy as np
from r_tree import Rectangle, R_node, R_tree


class Point():
    def __init__(self, coords: List[int]):
        self.d = len(coords)
        self.coords = coords
        
    def get_coord(self, i: int):
        if i >= self.d or i < 0:
            return None
        return self.coords[i]

    def get_dim(self):
        return self.d


class Object_():
    def __init__(self):
        self.rect = None
        self.dist = np.inf


Branch = namedtuple('Branch', ['MBR', 'Node', 'MinDist', 'MinMaxDist'])
BranchList = List[Branch]


def get_rec_points(rec: Rectangle):
    S  = Point([rec.x1, rec.y1])
    T  = Point([rec.x2, rec.y2])
    R1 = Point([rec.x1, rec.y2])
    R2 = Point([rec.x2, rec.y1])
    return S, T, R1, R2


def min_dist(Q: Point, R: Rectangle):
    dist = 0
    S, T, _, _ = get_rec_points(R)
    for i in range(Q.get_dim()):
        q_i = Q.get_coord(i)
        s_i = S.get_coord(i)
        t_i = T.get_coord(i)
        r_i = q_i
        if q_i < s_i:
            r_i = s_i
        elif q_i > t_i:
            r_i = t_i
        dist += abs(q_i - r_i)**2
    return dist # Nema tam byt odmocnina?


def min_max_dist(Q: Point, R: Rectangle):
    minmax = np.inf
    S, T, _, _ = get_rec_points(R)
    for k in range(Q.get_dim()):
        q_k = Q.get_coord(k)
        s_k = S.get_coord(k)
        t_k = T.get_coord(k)
        rm_k = s_k if q_k <= (s_k + t_k)/2 else t_k
        flux = abs(q_k - rm_k)**2
        for i in range(Q.get_dim()):
            if i != k:
                q_i = Q.get_coord(i)
                s_i = S.get_coord(i)
                t_i = T.get_coord(i)
                rM_i = s_i if q_i >= (s_i + t_i)/2 else t_i
                flux += abs(q_i - rM_i)**2
        minmax = flux if flux < minmax else minmax
    return minmax


def object_dist(point: Point, rec: Rectangle):
    S, T, _, _ = get_rec_points(rec)
    assert(S == T)
    dist = 0
    for i in range(point.get_dim()):
        dist += (point.get_coord[i] - S.get_coord[i])**2
    return np.sqrt(dist)


def gen_branch_list(point: Point, node: R_node) -> BranchList:
    branch_list = []
    for i in range(node.no_of_keys):
        branch_list.append(Branch(
            MBR=node.keys[i],
            Node=node.children[i],
            MinDist=min_dist(point, node.keys[i].I),
            MinMaxDist=min_max_dist(point, node.keys[i].I)
        ))
    return sorted(branch_list, key=attrgetter('MinDist'))


def prune_branch_list(node: R_node, point: Point, nearest: Object_, branch_list: BranchList):
    # TODO
    pass


def NNSearch(node: R_node, point: Point, nearest: Object_):
    if node.is_leaf:
        for i in range(node.no_of_keys):
            dist = object_dist(point, node.keys[i].I)
            if dist < nearest.dist:
                nearest.dist = dist
                nearest.rect = node.keys[i].I
    else:
        branch_list = gen_branch_list(point, node)
        last = prune_branch_list(node, point, nearest, branch_list)
        # TODO



if __name__ == "__main__":
    # Test min_dist
    R = Rectangle(4, 8, 4, 6)
    Q1 = Point([2, 5])
    Q2 = Point([2, 12])
    print(np.sqrt(min_dist(Q1, R)))
    print(min_dist(Q2, R))

    print(min_max_dist(Q1, R))
    print(min_max_dist(Q2, R))

