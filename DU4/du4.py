import numpy as np


class Rectangle():
    def __init__(self, x1, x2, y1, y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

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


class R_tree():
    def __init__(self, M):
        self.root = R_node(M, 'A', None, is_root=True, is_leaf=True)
        self.M = M
        self.ide_counter = 'A'
    
    def insert(self, E):
        L = self.choose_leaf(self.root, E)
        Ll = None
        if L.no_of_keys < self.M: # Mame misto
            L.keys[L.no_of_keys] = E
            L.no_of_keys += 1    
        else: # Nemame misto
            L, Ll = L.split_node(E)
        
        self.root, Ll = self.adjust_tree(L, Ll)
        if Ll is not None:
            new_root = R_node(self.M, 'A', None, is_root=True, is_leaf=False)
            new_root.keys[0] = Index_Record(get_bounded_rectangle(L.keys), chr(ord(self.ide_counter) + 1))
            new_root.keys[1] = Index_Record(get_bounded_rectangle(Ll.keys), chr(ord(self.ide_counter) + 2))
            new_root.children[0] = L
            new_root.children[1] = Ll
            new_root.no_of_keys = 2
            L.pred = new_root
            L.is_root = False
            Ll.pred = new_root
            Ll.is_root = False
            self.root = new_root
            self.ide_counter = chr(ord(self.ide_counter) + 2)

    def choose_leaf(self, N, E):
        # CL2
        if N.is_leaf:
            return N
        # CL3
        F = None
        minimum = np.inf
        pf = -1

        for i in range(N.no_of_keys):
            record = N.keys[i]
            print(record)
            diff = get_bounded_rectangle([record, E]).area() - record.I.area()
            if diff < minimum:
                F = record # Copy?
                minimum = diff
                pf = i
            elif diff == minimum and F is not None:
                if record.I.area() < F.I.area(): # Vzit mensi obdelnik
                    F = record
                    pf = i # pf je id?
        
        assert(pf != -1)
        # CL4
        return self.choose_leaf(N.children[pf], E)

    def adjust_tree(self, N, Nn=None):
        # AT2
        if N.is_root:
            return N, Nn

        # AT3
        P = N.pred
        En = P.find_record(N) # OPRAVIT metodu
        En.I = get_bounded_rectangle(N.keys)

        # AT4
        if Nn is not None:
            Enn = Index_Record(get_bounded_rectangle(Nn.keys), ide=Nn.ide)
            if P.no_of_keys < self.M:
                P.keys[P.no_of_keys] = Enn
                P.no_of_keys += 1
                return self.adjust_tree(P, None)
            else:
                P, Pp = P.split_node(Enn)
                return self.adjust_tree(P, Pp)
        return self.adjust_tree(P, None)

    def print_tree(self, N, depth):
        if N is None:
            return
        for child in N.children:
            self.print_tree(child, depth+1)
        if N.is_leaf:
            print("LEAF")
        else:
            print("NOT LEAF")
        for key in N.keys:
            if key is None:
                break
            print("Node {}, Key {}: Depth: {}".format(N.ide, key.ide, depth), end=" ")
            key.I.print_rec()

class R_node():
    def __init__(self, M, ide, pred, is_root=False, is_leaf=False):
        self.ide = ide
        self.M = M
        self.pred = pred
        self.keys = [None for _ in range(M)]
        self.children = [None for _ in range(M)]
        self.is_leaf = is_leaf
        self.is_root = is_root
        self.no_of_keys = 0

    def split_node(self, E):
        first = []
        second = []
        records = self.keys
        records.append(E)
        A, B = pick_seeds(records)
        first.append(A)
        second.append(B)

        while len(records) > 0:            
            if help_QS2(self.M, len(first), len(second), len(records)):
                first.extend(records)
                return self.ret_split(first, second)
            if help_QS2(self.M, len(second), len(first), len(records)):
                second.extend(records)
                return self.ret_split(first, second)

            first_area = get_bounded_rectangle(first).area()
            second_area = get_bounded_rectangle(second).area()

            C = pick_next(first, first_area, second, second_area, records)
            d1 = get_bounded_rectangle(np.append(first, C)).area() - first_area
            d2 = get_bounded_rectangle(np.append(second, C)).area() - second_area
            if d1 < d2:
                first.append(C)
            elif d2 < d1:
                second.append(C)
            else:
                if first_area < second_area:
                    first.append(C)
                elif second_area < first_area:
                    second.append(C)
                else:
                    if len(first) <= len(second):
                        first.append(C)
                    else:
                        second.append(C)
        return self.ret_split(first, second)

    def find_record(self, N):
        # TODO OPRAVIT
        for i in range(self.no_of_keys):
            if N.ide == self.children[i].ide:
                return self.keys[i]
        return None

    def ret_split(self, first, second):
        L = R_node(self.M, chr(ord(self.ide) + 1), self.pred, is_root=self.is_root, is_leaf=self.is_leaf)
        Ll = R_node(self.M, chr(ord(self.ide) + 2), self.pred, is_root=self.is_root, is_leaf=self.is_leaf)
        L.set_keys(first)
        Ll.set_keys(second)
        return L, Ll

    def set_keys(self, keys):
        self.no_of_keys = len(keys)
        for i in range(self.M):
            if i >= len(keys):
                self.keys[i] = None
            else:
                self.keys[i] = keys[i]


def pick_seeds(records):
    d = 0
    F1 = F2 = None
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
    assert(F1 != None and F2 != None and idx1 != -1 and idx2 != -1)
    del records[idx2]
    del records[idx1] # Zkontrolovat, ze se to smaze spravne
    return F1, F2


def pick_next(first, first_area, second, second_area, records):
    maximum = 0
    ret = None
    del_idx = -1
    
    for i in range(len(records)):
        record = records[i]
        d1 = get_bounded_rectangle(np.append(first, record)).area() - first_area #get_bounded_rectangle([first, record]).area() - first_area
        d2 = get_bounded_rectangle(np.append(second, record)).area() - second_area
        if np.abs(d1 - d2) > maximum:
            maximum = np.abs(d1 - d2)
            ret = record
            del_idx = i
    assert(ret != None and del_idx != -1)
    del records[del_idx]
    return ret


def get_bounded_rectangle(records):
    # Slo by optimalizovat pres numpy
    new_rectangle = Rectangle(np.inf, 0, np.inf, 0)
    for record in records:
        if record is None:
            break
        if record.I.x1 < new_rectangle.x1:
            new_rectangle.x1 = record.I.x1 #  +1 ? jak moc tesne to ma byt?
        if record.I.x2 > new_rectangle.x2:
            new_rectangle.x2 = record.I.x2
        if record.I.y1 < new_rectangle.y1:
            new_rectangle.y1 = record.I.y1
        if record.I.y2 > new_rectangle.y2:
            new_rectangle.y2 = record.I.y2
    return new_rectangle


def help_QS2(M, a, b, r):
    # Prosim at to funguje...
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
    rt.insert(Index_Record(Rectangle(1, 2, 1, 2), 1))
    rt.print_tree(rt.root, 0)
    print()
    rt.insert(Index_Record(Rectangle(3, 4, 3, 4), 2))
    rt.print_tree(rt.root, 0)
    print()
    rt.insert(Index_Record(Rectangle(2, 5, 1, 3), 3))
    rt.print_tree(rt.root, 0)
    print()

    rt.insert(Index_Record(Rectangle(6, 7, 5, 6), 4))
    rt.print_tree(rt.root, 0)
    print()
    

    rt.insert(Index_Record(Rectangle(1, 5, 2, 4), 5))
    print("ok1")
    rt.print_tree(rt.root, 0)
    print()
    rt.insert(Index_Record(Rectangle(10, 12, 6, 8), 6))
    print("ok2")
    rt.print_tree(rt.root, 0)
    print()

    # PO SEM DOBRE
    rt.insert(Index_Record(Rectangle(5, 7, 5, 6), 7))
    print("ok3")
    rt.print_tree(rt.root, 0)
    print()
    rt.insert(Index_Record(Rectangle(1, 3, 7, 9), 8))
    print("ok4")

    rt.print_tree(rt.root, 0)