import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle as pltRec


# Class for a set of unique identifiers
class ID_set():
    def __init__(self):
        self.ide_counter = 'A'
        self.ide = 'A'

    # Get unique identifier
    def get_ide(self):
        ret = self.ide
        offset = 'A' if ret == len(ret)*'Z' else ''
        if self.ide[-1] == 'Z':
            self.ide = self.ide_counter + ret[:-1] + offset
            self.ide_counter = chr(ord(self.ide_counter) + 1)
        else:
            self.ide = self.ide[:-1] + chr(ord(self.ide[-1]) + 1)
        return ret
        

class Rectangle():
    def __init__(self, x1, x2, y1, y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

    def __eq__(self, other):
        if not isinstance(other, Index_Record):
            return False
        return self.x1 == other.x1 and self.x2 == other.x2 and self.y1 == other.y1 and self.y2 == other.y2

    def area(self):
        a = self.x2 - self.x1
        b = self.y2 - self.y1
        return a*b

    def print_rec(self):
        print("Rectangle ({}, {}, {}, {}).".format(self.x1, self.x2, self.y1, self.y2))


class Index_Record():
    def __init__(self, I, ide):
        self.I = I
        self.ide = ide

    def __eq__(self, other):
        if not isinstance(other, Index_Record):
            return False
        return self.ide == other.ide and self.I == other.I


class R_tree():
    def __init__(self, M):
        self.M = M # Maximum number of stored records in one node
        self.id_set = ID_set() # Set of unique identifiers for nodes
        self.root = R_node(M, self.id_set, None, is_root=True, is_leaf=True)
    
    def insert(self, E):
        L = self.choose_leaf(self.root, E)
        Ll = None
        if L.no_of_keys < self.M:
            # There is a space
            L.keys[L.no_of_keys] = E
            L.no_of_keys += 1    
        else:
            # There is no space
            L, Ll = L.split_node(E)
        
        L, Ll = self.adjust_tree(L, Ll)
        if Ll is not None:
            # We have to make a new root
            new_root = R_node(self.M, self.id_set, None, is_root=True, is_leaf=False)
            new_root.keys[0] = Index_Record(get_bounded_rectangle(L.keys), L.ide)
            new_root.keys[1] = Index_Record(get_bounded_rectangle(Ll.keys), Ll.ide)
            new_root.children[0] = L
            new_root.children[1] = Ll
            new_root.children[0].ide = L.ide
            new_root.children[1].ide = Ll.ide
            new_root.no_of_keys = 2
            L.pred = new_root
            L.is_root = False
            Ll.pred = new_root
            Ll.is_root = False
            self.root = new_root
        else:
            self.root = L

        # Traverse the tree and renew the information about predecesor for each node
        self.adjust_preds(self.root)

    def choose_leaf(self, N, E):
        if N.is_leaf:
            return N
        F = None
        minimum = np.inf
        pf = -1
        for i in range(N.no_of_keys):
            record = N.keys[i]
            diff = get_bounded_rectangle([record, E]).area() - record.I.area()
            if diff < minimum:
                F = record
                minimum = diff
                pf = i
            elif diff == minimum and F is not None:
                if record.I.area() < F.I.area():
                    F = record
                    pf = i
        assert(pf != -1)
        return self.choose_leaf(N.children[pf], E)

    def adjust_tree(self, N, Nn=None):
        if N.is_root:
            return N, Nn
        P = N.pred
        En, idx = P.find_record(N)
        En.I = get_bounded_rectangle(N.keys)
        P.children[idx] = N

        if Nn is not None:
            Enn = Index_Record(get_bounded_rectangle(Nn.keys), ide=Nn.ide)
            if P.no_of_keys < self.M:
                P.keys[P.no_of_keys] = Enn
                P.children[P.no_of_keys] = Nn
                P.no_of_keys += 1
                return self.adjust_tree(P, None)
            else:
                P, Pp = P.split_node(Enn, True, Nn)
                return self.adjust_tree(P, Pp)
        return self.adjust_tree(P, None)

    def adjust_preds(self, N):
        if N is None or N.is_leaf:
            return
        for child in N.children:
            if child:
                child.pred = N
                self.adjust_preds(child)

    def print_tree(self, N, depth):
        if N is None:
            return
        for child in N.children:
            self.print_tree(child, depth+1)
        if N.is_leaf:
            print("LEAF")
        elif N.is_root:
            print("ROOT")
        else:
            print("INNER NODE")
        for key in N.keys:
            if key is None:
                break
            print("Node {}, Key {}: Depth: {}, Pred: {}".format(N.ide, key.ide, depth, N.pred.ide if N.pred else "None"), end=" ")
            key.I.print_rec()

    def missing_test(self, N, ides):
        if N is None:
            return ides
        for child in N.children:
            ides = self.missing_test(child, ides)
        if N.is_leaf:
            for key in N.keys:
                if key:
                    ides[key.ide] = True
        return ides

    def plot_tree(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        rec = get_bounded_rectangle(self.root.keys)
        self.root.plot_node(ax)
        ax.add_patch(pltRec(
            xy=(rec.x1, rec.y1),
            width=rec.x2-rec.x1,
            height=rec.y2-rec.y1,
            linestyle = '-',
            linewidth=1.3,
            color='b',
            fill=False))
        ax.text(rec.x2, rec.y1, self.root.ide, fontsize=14, color='b')
        plt.show()
        

class R_node():
    def __init__(self, M, id_set, pred, is_root=False, is_leaf=False, origin_id=None):
        self.ide = origin_id if origin_id else id_set.get_ide()
        self.id_set = id_set
        self.M = M
        self.pred = pred
        self.keys = [None for _ in range(M)]
        self.children = [None for _ in range(M)]
        self.is_leaf = is_leaf
        self.is_root = is_root
        self.no_of_keys = 0

    def __eq__(self, other): 
        if not isinstance(other, R_node):
            return False
        for i in range(self.M):
            if self.keys[i] and not other.keys[i]:
                return False
            if other.keys[i] and not self.keys[i]:
                return False
            if self.keys[i] != other.keys[i]:
                return False
        return True

    def split_node(self, E, has_children=False, Nn=None):
        first = []
        second = []
        first_children = []
        second_children = []
        records = self.keys
        records.append(E)
        children = self.children
        if has_children:
            children.append(Nn)

        A, B, C1, C2 = pick_seeds(records, children, has_children)
        first.append(A)
        second.append(B)
        first_children.append(C1)
        second_children.append(C2)

        while len(records) > 0:
            if help_QS2(self.M, len(first), len(second), len(records)):
                first.extend(records)
                first_children.extend(children)
                return self.ret_split(first, second, first_children, second_children, has_children)
            if help_QS2(self.M, len(second), len(first), len(records)):
                second.extend(records)
                second_children.extend(children)
                return self.ret_split(first, second, first_children, second_children, has_children)

            first_area = get_bounded_rectangle(first).area()
            second_area = get_bounded_rectangle(second).area()

            C, Ch = pick_next(first, first_area, second, second_area, records, children)
            d1 = get_bounded_rectangle(np.append(first, C)).area() - first_area
            d2 = get_bounded_rectangle(np.append(second, C)).area() - second_area
            if d1 < d2:
                first.append(C)
                first_children.append(Ch)
            elif d2 < d1:
                second.append(C)
                second_children.append(Ch)
            else:
                if first_area < second_area:
                    first.append(C)
                    first_children.append(Ch)
                elif second_area < first_area:
                    second.append(C)
                    second_children.append(Ch)
                else:
                    if len(first) <= len(second):
                        first.append(C)
                        first_children.append(Ch)
                    else:
                        second.append(C)
                        second_children.append(Ch)
        return self.ret_split(first, second, first_children, second_children, has_children)

    def find_record(self, N):
        for i in range(self.no_of_keys):
            if N.ide == self.keys[i].ide:
                return self.keys[i], i
        return None, None

    def ret_split(self, first, second, first_children, second_children, has_children):
        L = R_node(self.M, self.id_set, self.pred, is_root=self.is_root, is_leaf=self.is_leaf, origin_id=self.ide)
        Ll = R_node(self.M, self.id_set, self.pred, is_root=self.is_root, is_leaf=self.is_leaf)
        L.set_keys(first, first_children, has_children)
        Ll.set_keys(second, second_children, has_children)
        return L, Ll

    def set_keys(self, keys, children, has_children=False):
        self.no_of_keys = len(keys)
        for i in range(self.M):
            if i >= len(keys):
                self.keys[i] = None
                self.children[i] = None
            else:
                self.keys[i] = keys[i]
                if has_children:
                    self.children[i] = children[i]

    def print_node(self):
        print("Node id: {}, keys:".format(self.ide), end=" ")
        for key in self.keys:
            if key is None:
                print("[Nonekey]")
                continue
            print("Key id: {}".format(key.ide))
            key.I.print_rec()
        print()

    def plot_node(self, ax):
        for record in self.keys:
            if record:
                rec = record.I
                ax.add_patch(pltRec(
                    xy=(rec.x1, rec.y1),
                    width=rec.x2-rec.x1,
                    height=rec.y2-rec.y1,
                    linestyle = 'dotted' if self.is_leaf else '--',
                    linewidth=1 if self.is_leaf else 1.2,
                    color='r' if self.is_leaf else 'b',
                    fill=False))
                ax.text(
                    (rec.x1+rec.x2)/2,
                    (rec.y1+rec.y2)/2,
                    record.ide,
                    fontsize=10,
                    color='r' if self.is_leaf else 'b')
        for child in self.children:
            if child:
                child.plot_node(ax)
        ax.axis('equal')



def pick_seeds(records, children=None, has_children=False):
    d = -np.inf
    F1 = F2 = C1 = C2 = None
    idx1 = idx2 = -1
    for i in range(len(records)):
        E1 = records[i]
        if E1 is None:
            break
        for j in range(i+1, len(records)): 
            E2 = records[j]
            if E2 is None:
                break
            J = get_bounded_rectangle([E1, E2])
            area = J.area() - E1.I.area() - E2.I.area()
            if area > d:
                d = area
                F1 = E1
                F2 = E2
                idx1 = i
                idx2 = j
                if has_children:
                    C1 = children[i]
                    C2 = children[j]
    assert(F1 != None and F2 != None and idx1 != -1 and idx2 != -1)
    del records[idx2]
    del records[idx1]
    if has_children:
        del children[idx2]
        del children[idx1]
    return F1, F2, C1, C2


def pick_next(first, first_area, second, second_area, records, children):
    maximum = 0
    ret_record = None
    ret_child = None
    del_idx = -1
    
    for i in range(len(records)):
        record = records[i]
        d1 = get_bounded_rectangle(np.append(first, record)).area() - first_area
        d2 = get_bounded_rectangle(np.append(second, record)).area() - second_area
        if np.abs(d1 - d2) > maximum:
            maximum = np.abs(d1 - d2)
            ret_record = record
            ret_child = children[i]
            del_idx = i
    assert(ret_record != None and del_idx != -1)
    del records[del_idx]
    del children[del_idx]
    return ret_record, ret_child


def get_bounded_rectangle(records):
    # Slo by optimalizovat pres numpy
    new_rectangle = Rectangle(np.inf, 0, np.inf, 0)
    for record in records:
        if record is None:
            break
        if record.I.x1 < new_rectangle.x1:
            new_rectangle.x1 = record.I.x1
        if record.I.x2 > new_rectangle.x2:
            new_rectangle.x2 = record.I.x2
        if record.I.y1 < new_rectangle.y1:
            new_rectangle.y1 = record.I.y1
        if record.I.y2 > new_rectangle.y2:
            new_rectangle.y2 = record.I.y2
    return new_rectangle


def help_QS2(M, a, b, r):
    if a >= M/2:
        return False
    if b < M/2:
        return False
    if a + r < M/2:
        return False
    if a + r > b + 1:
        return False
    if a + r > M:
        return False
    return True


if __name__ == "__main__":

    rt = R_tree(3)
    rt.insert(Index_Record(Rectangle(1, 2, 1, 2), 0))
    rt.print_tree(rt.root, 0)
    print()
    rt.insert(Index_Record(Rectangle(3, 4, 3, 4), 1))
    rt.print_tree(rt.root, 0)
    print()
    rt.insert(Index_Record(Rectangle(2, 5, 1, 3), 2))
    rt.print_tree(rt.root, 0)
    print()

    rt.insert(Index_Record(Rectangle(6, 7, 5, 6), 3))
    rt.print_tree(rt.root, 0)
    print()
    

    rt.insert(Index_Record(Rectangle(1, 5, 2, 4), 4))
    print("ok1")
    rt.print_tree(rt.root, 0)
    print()
    rt.insert(Index_Record(Rectangle(10, 12, 6, 8), 5))
    print("ok2")
    rt.print_tree(rt.root, 0)
    print()

    rt.insert(Index_Record(Rectangle(5, 7, 5, 6), 6))
    print("ok3")
    rt.print_tree(rt.root, 0)
    print()

    rt.insert(Index_Record(Rectangle(1, 3, 7, 9), 7))
    print("ok4")
    rt.print_tree(rt.root, 0)

    rt.insert(Index_Record(Rectangle(20, 23, 15, 19), 8))
    print("ok4")
    rt.print_tree(rt.root, 0)

    rt.insert(Index_Record(Rectangle(1, 4, 2, 3), 9))
    print("ok4")
    rt.print_tree(rt.root, 0)

    rt.insert(Index_Record(Rectangle(1, 4, 1, 4), 10))
    print("ok4")
    rt.print_tree(rt.root, 0)

    rt.insert(Index_Record(Rectangle(1, 3, 5, 7), 11))
    print("ok4")
    rt.print_tree(rt.root, 0)

    rt.insert(Index_Record(Rectangle(1, 5, 2, 3), 12))
    print("ok4")
    rt.print_tree(rt.root, 0)

    rt.insert(Index_Record(Rectangle(1, 4, 2, 3), 13))
    print("ok4")
    rt.print_tree(rt.root, 0)

    miss_test = rt.missing_test(rt.root, [False for _ in range(14)])
    if all(miss_test):
        print("OK")
    else:
        print("Something is missing")
        print(miss_test)