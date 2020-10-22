import numpy as np

class Node:
    def __init__(self, data):
        self.left = None
        self.right = None
        self.data = data

def insert(node, data):
    if node is None or node.data is None:
        return Node(data)
    if data < node.data:
        node.left = insert(node.left, data)
    if data > node.data:
        node.right = insert(node.right, data)
    return node

def findMin(node):
    if node.left is None:
        return node.data
    return findMin(node.left)

def delete(node, data):
    if node is None:
        return node
    if data < node.data:
        node.left = delete(node.left, data)
    elif data > node.data:
        node.right = delete(node.right, data)
    else:
        if node.left is None and node.right is None:
            return None
        if node.left is None:
            tmp = node.right
            node = None
            return tmp
        if node.right is None:
            tmp = node.left
            node = None
            return tmp
        
        minimum = findMin(node.right)
        node.data = minimum
        node.right = delete(node.right, minimum)

    return node

def inorder(node):
    if node.left:
        inorder(node.left)
    print(node.data)
    if node.right:
        inorder(node.right)

def treeHeight(node):
    if node is None:
        return 0
    if node.left is None and node.right is None:
        return 1
    if node.left is None:
        return 1 + treeHeight(node.right)
    if node.right is None:
        return 1 + treeHeight(node.left)
    else:
        return 1 + max(treeHeight(node.left), treeHeight(node.right))


if __name__ == "__main__":
    
    heights_1 = []
    heights_2 = []
    heights_3 = []

    for _ in range(1000):
        # 1)
        keys = np.linspace(1, 100, 100, dtype=np.int32)
        np.random.shuffle(keys)

        root = None
        for key in keys:
            root = insert(root, key)
        #print("1) ", treeHeight(root))
        heights_1.append(treeHeight(root))

        # 2)
        keys = np.linspace(1, 200, 200, dtype=np.int32)
        keysToDelete = np.random.choice(200, 100, replace=False)
        np.random.shuffle(keys)
        np.random.shuffle(keysToDelete)
        root = None
        for key in keys:
            root = insert(root, key)
        for key in keysToDelete:
            root = delete(root, key)
        #print("2) ", treeHeight(root))
        heights_2.append(treeHeight(root))

        # 3)
        keys = np.linspace(1, 200, 100, dtype=np.int32)
        keysToDelete = np.random.choice(200, 100, replace=False)
        np.random.shuffle(keys)
        np.random.shuffle(keysToDelete)
        root = None
        for i in range(len(keys)):
            if i % 2 == 0 and i > 0:
                root = delete(root, keysToDelete[i])
            root = insert(root, keys[i])
        #print("3) ", treeHeight(root))
        heights_3.append(treeHeight(root))

    print("1)", np.mean(heights_1))
    print("2)", np.mean(heights_2))
    print("3)", np.mean(heights_3))
    