import numpy as np
import itertools
import math
from typing import List
from collections import namedtuple
from operator import attrgetter
from r_tree import Rectangle, R_node, R_tree, Index_Record, get_bounded_rectangle
# from du6 import Po
from du5 import hilbert_value


MAX_HILBERT_ORDER = 10
Rect_info = namedtuple('Rect_info', ['Rect', 'Center', 'H'])

class Static_R_node():
    def __init__(self, M, pred):
        self.M = M
        self.pred = pred
        self.rectangles = [None for _ in range(M)]
        self.children = [None for _ in range(M)]        

    def set_rects(self, rectangles: List[Rectangle]):
        for i in range(self.M):
            if i >= len(rectangles):
                self.rectangles[i] = None
            else:
                self.rectangles[i] = rectangles[i]

    def set_children(self, children):
        for i in range(self.M):
            if i >= len(children):
                self.children[i] = None
            else:
                self.children[i] = children[i]

    def is_root(self):
        return True if self.pred is None else False

    def is_leaf(self):
        return True if all([x is None for x in self.children]) else False




def round_(x, y, i):
    if i % 4 == 0:
        return math.floor(x), math.floor(y)
    elif i % 4 == 1:
        return math.ceil(x), math.floor(y)
    elif i % 4 == 2:
        return math.ceil(x), math.ceil(y)
    elif i % 4 == 3:
        return math.floor(x), math.ceil(y)
    print("Round ERROR")
    return None, None

def get_centers(rectangles: List[Rectangle]) -> List[Rectangle]:
    centers = []
    for i in range(len(rectangles)):
        rect = rectangles[i]
        #x = math.floor((rect.x1 + rect.x2) / 2)
        #y = math.floor((rect.y1 + rect.y2) / 2)
        x, y = round_((rect.x1 + rect.x2) / 2, (rect.y1 + rect.y2) / 2, i)
        centers.append(Rectangle(x, x, y, y))
    return centers


def get_mbr(rectangles: List[Rectangle]) -> Rectangle:
    mbr = Rectangle(np.inf, 0, np.inf, 0)
    for rect in rectangles:
        if rect.x1 < mbr.x1:
            mbr.x1 = rect.x1
        if rect.x2 > mbr.x2:
            mbr.x2 = rect.x2
        if rect.y1 < mbr.y1:
            mbr.y1 = rect.y1
        if rect.y2 > mbr.y2:
            mbr.y2 = rect.y2
    return mbr


def max_coord(rect: Rectangle):
    return max(rect.x2, rect.y2)


def get_hilbert_curve_order(mbr: Rectangle) -> int:
    for i in range(MAX_HILBERT_ORDER):
        if max_coord(mbr) <= 2**i:
            return i
        #if mbr.area() <= (2**i) * (2**i):
        #    return i
    print("WARNING: Needs larger Hilbert curve order!")
    return MAX_HILBERT_ORDER


def sort_rectangles(rectangles: List[Rectangle]) -> List[Rect_info]:
    centers = get_centers(rectangles)
    n = get_hilbert_curve_order(get_mbr(centers))
    rect_list = []

    print(f"H order: {n}")

    for (rect, center) in zip(rectangles, centers):
        assert(center.x1 == center.x2 and center.y1 == center.y2)
        rect.print_rec()
        center.print_rec()
        print("=====")
        rect_list.append(Rect_info(
            Rect=rect,
            Center=center,
            H=hilbert_value(center.x1, center.y1, n)
        ))
    return sorted(rect_list, key=attrgetter('H'))


def group_rectangles(rectangels: List[Rect_info], c: int) -> List[List[Rectangle]]:
    groups = []
    group = []
    for i in range(len(rectangels)):
        if i != 0 and i % c == 0:
            groups.append(group)
            group = []
        group.append(rectangels[i].Rect)
    if len(group) > 0:
        groups.append(group)
    return groups


def get_mbrs_and_nodes_for_groups(pred: Static_R_node, groups: List[List[Rectangle]], c: int) -> List[Rectangle]:
    mbrs = []
    nodes = []
    for group in groups:
        mbrs.append(get_mbr(group))
        node = Static_R_node(c, pred)
        node.set_rects(group)
        nodes.append(node)
    return mbrs, nodes
        
    
def build_static_hilbert_tree(root: Static_R_node, rectangles: List[Rectangle], N: int, c: int):
    print_rectangeles(rectangles)
    sorted_rectangels = sort_rectangles(rectangles)
    groups = group_rectangles(sorted_rectangels, c)
    mbrs, children = get_mbrs_and_nodes_for_groups(root, groups, c)
    if len(mbrs) <= c:
        root.set_rects(mbrs)
        root.set_children(children)
        return root
    else:
        print("Recursion")
        new_root = Static_R_node(c, None)
        new_root = build_static_hilbert_tree(new_root, mbrs, len(mbrs), c)
        # TODO vymyslet napojovani
        return new_root


    
    """
    print(f"N = {N}, c = {c}")
    for i in range(len(groups)):
        print(f"Group {i}:")
        for r in groups[i]:
            r.Rect.print_rec()
            r.Center.print_rec()
            print(r.H)
            print("----------")"""


def print_tree(node: Static_R_node, depth: int):
    if node is None:
        return
    for child in node.children:
        print_tree(child, depth+1)
    info = "Inner"
    if node.is_root():
        info = "Root"
    elif node.is_leaf():
        info = "Leaf"
    print(f"{info} node in depth {depth}:")
    for rect in node.rectangles:
        if rect is None:
            print("None")
            continue
        rect.print_rec()
    print("------")
    

def print_rectangeles(rectangles):
    for rect in rectangles:
        rect.print_rec()


if __name__ == "__main__":
    rectangles = [
        Rectangle(1, 3, 1, 5),
        Rectangle(3, 7, 3, 9),
        Rectangle(2, 6, 1, 3),
        Rectangle(6, 10, 5, 11),
        Rectangle(3, 5, 2, 8),
        Rectangle(10, 12, 6, 8),
        Rectangle(5, 7, 5, 9),
        Rectangle(1, 3, 7, 9),
        Rectangle(20, 23, 15, 19),
        Rectangle(5, 10, 2, 12),
        Rectangle(7, 14, 9, 13),
        Rectangle(3, 9, 5, 7),
        Rectangle(8, 12, 4, 8),
        Rectangle(14, 16, 2, 4)
    ]
    N = len(rectangles)
    c = 3

    root = Static_R_node(c, None)
    root = build_static_hilbert_tree(root, rectangles, N, c)
    print_tree(root, 0)


    