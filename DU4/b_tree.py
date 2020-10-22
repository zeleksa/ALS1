

class B_tree():
    def __init__(self, t):
        self.t = t
        self.root = None

    def traverse(self):
        if self.root is not None:
            self.root.traverse()

    def search(self, num):
        if self.root is None:
            return None
        self.root.search(num)

    def insert(self, num):
        if self.root is None:
            self.root = B_node(self.t, is_leaf=True)
            self.root.keys[0] = num
            self.root.n = 1
        else:
            if self.root.n == 2*self.t - 1:
                new_root = B_node(self.t)
                new_root.children[0] = self.root
                new_root.split_child(0, self.root)

                i = 0
                if new_root.keys[0] < num:
                    i += 1
                new_root.children[i].insert_non_full(num)
                self.root = new_root
            else:
                self.root.insert_non_full(num)


class B_node():
    def __init__(self, t, is_leaf=False):
        self.keys = [None for _ in range(2*t - 1)]
        self.children = [None for _ in range(2*t)]
        self.t = t
        self.n = 0
        self.is_leaf = is_leaf

    def traverse(self):
        j = 0
        for i in range(self.n):
            if not self.is_leaf:
                self.children[i].traverse()
            print(self.keys[i], end=" ")
            j += 1

        if not self.is_leaf:
            self.children[j].traverse()

    def search(self, num):
        i = 0
        while i < self.n and num > self.keys[i]:
            i += 1
        if self.keys[i] == num:
            print("Found")
            return self.keys
        if self.is_leaf:
            print("Not Found")
            return None
        return self.children[i].search(num)

    def insert_non_full(self, num):
        i = self.n - 1
        if self.is_leaf:
            while i >= 0 and self.keys[i] > num:
                self.keys[i+1] = self.keys[i]
                i -= 1
            self.keys[i+1] = num
            self.n += 1
        else:
            while i >= 0 and self.keys[i] > num:
                i -= 1
            if self.children[i+1].n == 2*self.t - 1:
                self.split_child(i+1, self.children[i+1])

                if self.keys[i+1] < num:
                    i += 1
            self.children[i+1].insert_non_full(num)

    def split_child(self, i, old_node):
        new_node = B_node(old_node.t, is_leaf=old_node.is_leaf)
        new_node.n = self.t-1

        for j in range(self.t-1):
            new_node.keys[j] = old_node.keys[j+self.t]

        if not old_node.is_leaf:
            for j in range(self.t):
                new_node.children[j] = old_node.children[j+self.t]
        old_node.n = self.t - 1

        for j in range(self.n, i, -1):
            self.children[j+1] = self.children[j]
        self.children[i+1] = new_node

        for j in range(self.n - 1, i, -1):
            self.keys[j+1] = self.keys[j]
        self.keys[i] = old_node.keys[self.t-1]
        self.n += 1


if __name__ == "__main__":
    bt = B_tree(3)
    bt.insert(10)
    bt.insert(20)
    bt.insert(5)
    bt.insert(6)
    bt.insert(12)
    bt.insert(30)
    bt.insert(7)
    bt.insert(17)

    bt.traverse()
    print()

    bt.search(6)
    bt.search(15)
