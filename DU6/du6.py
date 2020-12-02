
from typing import List
from collections import namedtuple
from operator import attrgetter
import numpy as np
import time
from r_tree import Rectangle, R_node, R_tree, Index_Record


class Point():
    def __init__(self, coords: List[int]):
        self.d = len(coords)
        self.coords = coords

    def __eq__(self, other):
        if self.d != other.d:
            return False
        for i in range(self.d):
            if self.coords[i] != other.coords[i]:
                return False
        return True
        
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
        dist += (point.get_coord(i) - S.get_coord(i))**2
    return np.sqrt(dist)


def gen_branch_list(point: Point, node: R_node) -> BranchList:
    branch_list = []
    for i in range(node.no_of_keys):
        branch_list.append(Branch(
            MBR=node.keys[i].I,
            Node=node.children[i],
            MinDist=min_dist(point, node.keys[i].I),
            MinMaxDist=min_max_dist(point, node.keys[i].I) # Mozna zbytecne
        ))
    return sorted(branch_list, key=attrgetter('MinDist'))


def prune_branch_list_down(node: R_node, point: Point, nearest: Object_, branch_list: BranchList):
    # H1
    del_indices = []
    for i in range(len(branch_list)):
        for j in range(len(branch_list)):
            if i != j and branch_list[i].MinDist > branch_list[j].MinMaxDist:
                del_indices.append(i)
                break
    remove_elements(branch_list, del_indices)
    
    # H2
    for branch in branch_list:
        if nearest.dist > branch.MinMaxDist:
            nearest.dist = branch.MinMaxDist# np.inf # object_dist(point, branch.MBR) ?
            nearest.rect = branch.MBR # None # branch.MBR ?


def prune_branch_list_up(node: R_node, point: Point, nearest: Object_, branch_list: BranchList):
    # H3
    del_indices = []
    for i in range(len(branch_list)):
        if branch_list[i].MinDist > nearest.dist:
            del_indices.append(i)
    remove_elements(branch_list, del_indices)


def remove_elements(the_list, indices):
    for idx in sorted(indices, reverse=True):
        del the_list[idx]


def NNSearch(node: R_node, point: Point, nearest: Object_):
    if node.is_leaf:
        for i in range(node.no_of_keys):
            dist = object_dist(point, node.keys[i].I)
            if dist < nearest.dist:
                nearest.dist = dist
                nearest.rect = node.keys[i].I
    else:
        branch_list = gen_branch_list(point, node)
        prune_branch_list_down(node, point, nearest, branch_list)
        for branch in branch_list:
            newNode = branch.Node
            NNSearch(newNode, point, nearest)
            prune_branch_list_up(node, point, nearest, branch_list)


def NNSearch_2(node: R_node, point: Point, nearest: Object_):
    if node.is_leaf:
        for i in range(node.no_of_keys):
            dist = object_dist(point, node.keys[i].I)
            if dist < nearest.dist:
                nearest.dist = dist
                nearest.rect = node.keys[i].I
    else:
        branch_list = gen_branch_list(point, node)
        for branch in branch_list:
            prune_branch_list_up(node, point, nearest, branch_list)
            newNode = branch.Node
            NNSearch_2(newNode, point, nearest)
            




if __name__ == "__main__":
    # Test min_dist and minmax_dist
    R = Rectangle(4, 8, 4, 6)
    Q1 = Point([2, 5])
    Q2 = Point([2, 12])
    print(np.sqrt(min_dist(Q1, R)))
    print(min_dist(Q2, R))

    print(min_max_dist(Q1, R))
    print(min_max_dist(Q2, R))
    print("-------------------")

    rt = R_tree(3)
    
    """
    rt.insert(Index_Record(Rectangle(1, 2, 1, 2), 0))
    rt.insert(Index_Record(Rectangle(3, 4, 3, 4), 1))
    rt.insert(Index_Record(Rectangle(2, 5, 1, 3), 2))
    rt.insert(Index_Record(Rectangle(6, 7, 5, 6), 3))
    rt.insert(Index_Record(Rectangle(1, 5, 2, 4), 4))
    rt.insert(Index_Record(Rectangle(10, 12, 6, 8), 5))
    rt.insert(Index_Record(Rectangle(5, 7, 5, 6), 6))
    rt.insert(Index_Record(Rectangle(1, 3, 7, 9), 7))
    rt.insert(Index_Record(Rectangle(20, 23, 15, 19), 8))
    rt.insert(Index_Record(Rectangle(1, 4, 2, 3), 9))
    rt.insert(Index_Record(Rectangle(1, 4, 1, 4), 10))
    rt.insert(Index_Record(Rectangle(1, 3, 5, 7), 11))
    rt.insert(Index_Record(Rectangle(1, 5, 2, 3), 12))
    rt.insert(Index_Record(Rectangle(1, 4, 2, 3), 13))
    """
    rt.insert(Index_Record(Rectangle(1, 1, 2, 2), 0))
    rt.insert(Index_Record(Rectangle(3, 3, 4, 4), 1))
    rt.insert(Index_Record(Rectangle(2, 2, 3, 3), 2))
    rt.insert(Index_Record(Rectangle(6, 6, 5, 5), 3))
    rt.insert(Index_Record(Rectangle(1, 1, 4, 4), 4))
    rt.insert(Index_Record(Rectangle(10, 10, 8, 8), 5))
    rt.insert(Index_Record(Rectangle(7, 7, 5, 5), 6))
    rt.insert(Index_Record(Rectangle(3, 3, 7, 7), 7))
    rt.insert(Index_Record(Rectangle(20, 20, 15, 15), 8))
    rt.insert(Index_Record(Rectangle(4, 4, 2, 2), 9))
    rt.insert(Index_Record(Rectangle(4, 4, 4, 4), 10))
    rt.insert(Index_Record(Rectangle(1, 1, 7, 7), 11))
    rt.insert(Index_Record(Rectangle(5, 5, 3, 3), 12))
    rt.insert(Index_Record(Rectangle(4, 4, 3, 3), 13))
    

    N = 50
    points = np.array([np.repeat(np.arange(N), N), np.tile(np.arange(N), N)]).T

    time_start = time.time()
    for i in range(N**2):
        Q = Point(points[i])
        nearest = Object_()
        NNSearch(rt.root, Q, nearest)
    time_end = time.time()
    print(f"Alg 1: {time_end - time_start}")

    time_start = time.time()
    for i in range(N**2):
        Q = Point(points[i])
        nearest = Object_()
        NNSearch_2(rt.root, Q, nearest)
    time_end = time.time()
    print(f"Alg 2: {time_end - time_start}")




