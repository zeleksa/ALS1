import numpy as np


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
        self.root = R_node(M, 'A', None, is_root=True, is_leaf=True)
        self.M = M
        self.ide_counter = 'B'
    
    def insert(self, E):
        L = self.choose_leaf(self.root, E)
        Ll = None
        if L.no_of_keys < self.M: # Mame misto
            L.keys[L.no_of_keys] = E
            L.no_of_keys += 1    
        else: # Nemame misto
            L, Ll = L.split_node(E)
        
        self.root, Ll = self.adjust_tree(L, Ll) # TODO Poslat tam navic kopii L nodu v pripade ze se rozlomil? (kvuli porovnavani)
        if Ll is not None:
            print("NEW ROOOT")
            new_root = R_node(self.M, self.ide_counter, None, is_root=True, is_leaf=False)
            new_root.keys[0] = Index_Record(get_bounded_rectangle(L.keys), L.ide)#chr(ord(self.ide_counter) + 1))
            new_root.keys[1] = Index_Record(get_bounded_rectangle(Ll.keys), Ll.ide)#chr(ord(self.ide_counter) + 2))
            new_root.children[0] = L
            new_root.children[1] = Ll
            new_root.children[0].ide = L.ide#chr(ord(self.ide_counter) + 1)
            new_root.children[1].ide = Ll.ide#chr(ord(self.ide_counter) + 2)
            new_root.no_of_keys = 2
            L.pred = new_root
            L.is_root = False
            Ll.pred = new_root
            Ll.is_root = False
            self.root = new_root
            self.ide_counter = chr(ord(self.ide_counter) + 1)

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
        En = P.find_record(N) # OPRAVIT metodu - ok - vypada to ze je to v poradku
        En.I = get_bounded_rectangle(N.keys)

        print("AT3")

        # AT4
        if Nn is not None:
            print("AT4")
            print(N.ide, Nn.ide)
            print(P.no_of_keys)
            Enn = Index_Record(get_bounded_rectangle(Nn.keys), ide=Nn.ide)
            if P.no_of_keys < self.M:
                P.keys[P.no_of_keys] = Enn
                P.children[P.no_of_keys] = Nn # TODO promyslet
                P.no_of_keys += 1
                print("AT4.1")
                return self.adjust_tree(P, None)
            else:
                print("AT4.2")
                P, Pp = P.split_node(Enn, True, Nn)
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

    def __eq__(self, other): 
        if not isinstance(other, R_node):
            # don't attempt to compare against unrelated types
            return False
        print("eq", len(self.keys), len(other.keys))
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
            print("HAS CHILDREN!", end=" ")
            children.append(Nn)


        A, B, C1, C2 = pick_seeds(records, children, has_children)
        first.append(A)
        second.append(B)
        first_children.append(C1)
        second_children.append(C2)

        while len(records) > 0:
            print("SPLIT:", len(first), len(second), "remaining:", len(records), len(children)) 
            if help_QS2(self.M, len(first), len(second), len(records)):
                first.extend(records)
                first_children.extend(children)
                print("HELP QS2.1:", len(first), len(second))
                return self.ret_split(first, second, first_children, second_children, has_children)
            if help_QS2(self.M, len(second), len(first), len(records)):
                second.extend(records)
                second_children.extend(children)
                print("HELP QS2.2:", len(first), len(second))
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
            print("for", i, N.ide, self.children[i].ide)
            if N.ide == self.keys[i].ide:    
                assert(N != self.children[i])
                return self.keys[i]
        return None

    def ret_split(self, first, second, first_children, second_children, has_children):
        print("ret_split, ", self.ide, self.ide + self.ide[-1])
        L = R_node(self.M, self.ide, self.pred, is_root=self.is_root, is_leaf=self.is_leaf)
        Ll = R_node(self.M, self.ide + self.ide[-1], self.pred, is_root=self.is_root, is_leaf=self.is_leaf)
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


def pick_seeds(records, children=None, has_children=False):
    d = 0
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

    # PO SEM DOBRE, pak se ztrati zaznam <(3, 4, 3, 4), 2> # TODO zjistit proc a opravit chybu - chybi AAA
    rt.insert(Index_Record(Rectangle(5, 7, 5, 6), 7))
    print("ok3")
    rt.print_tree(rt.root, 0)
    print()

    # Tady se to rozsype jako domecek z karet
    rt.insert(Index_Record(Rectangle(1, 3, 7, 9), 8))
    print("ok4")

    rt.print_tree(rt.root, 0)