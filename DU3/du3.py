import numpy as np
import time


class Node():
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


def build_tree(R, i, j):
    if i == j:
        return None
    new_node = Node(R[i][j])
    new_node.left = build_tree(R, i, R[i][j] - 1)
    new_node.right = build_tree(R, R[i][j], j)
    return new_node


def find_value(node, value):
    if node.value == value:
        return value
    if value < node.value:
        return find_value(node.left, value)
    if value > node.value:
        return find_value(node.right, value)


def inorder(node):
    if node.left:
        inorder(node.left)
    print(node.value)
    if node.right:
        inorder(node.right)


def min_fcn(R, C):
    ks = np.arange(R[i][j-1], R[i+1][j] + 1, dtype=np.int32)
    values = []
    for k in ks:
        values.append(C[i][k-1] + C[k][j])
    return np.min(values), ks[np.argmin(values)]


def tree_search(root, num):
    if root is None:
        return -1
    if num < root.value:
        return tree_search(root.left, num)
    if num > root.value:
        return tree_search(root.right, num)
    return num


def bisection(values, num):
    values_sorted = np.sort(values)
    start = 0
    end = len(values_sorted) - 1
    pivot = np.int32((start + end) / 2)
    while end - start > 0 and pivot != end and pivot != start:
        if num < values_sorted[pivot]:
            end = pivot  
        elif num > values_sorted[pivot]:
            start = pivot
        else:
            return values_sorted[pivot], pivot
        pivot = np.int32((start + end) / 2) 
    return -1, -1


def read_pq():
    p = []
    q = []
    with open("pq.txt", "r") as f:
        first = True
        content = f.readlines()        
        for line in content:
            values = line.replace("(", " ").replace(")", " ").split()
            for val in values:
                if val.isdigit():
                    p.append(int(val)) if first else q.append(int(val))
                else:
                    if val == "Q":
                        first = False
    return p, q


if __name__ == "__main__":

    #p, q = [4, 1, 2, 2, 6], [1, 1, 1, 3, 2, 1]
    p, q = read_pq()

    # Initialization
    N = len(q)
    W = np.zeros((N, N), dtype=np.int32)
    C = np.copy(W)
    R = np.copy(W)
    for i in range(N):
        C[i][i] = 0
        W[i][i] = q[i]
        for j in range(i+1, N):
            W[i][j] = W[i][j-1] + p[j-1] + q[j]
    
    for j in range(1, N):
        C[j-1][j] = W[j-1][j]
        R[j-1][j] = j
    print("Init done")
    
    # Algorithm
    for d in range(2, N):
        for j in range(d, N):
            i = j - d
            minimum, k = min_fcn(R, C)
            C[i][j] = W[i][j] + minimum
            R[i][j] = k
    print("Algo done")

    # Build optimal tree and array of values
    root = build_tree(R, 0, len(R) - 1)
    array = np.arange(1, 1001)    
    print("Tree and array done")

    # Experiment
    time_1 = []
    time_2 = []
    for i in range(1000):
        
        # Searched number
        num = np.random.choice(array) # S ohledem na zadané váhy - co to znamená?
        
        # Bisection
        t_start = time.time()
        _, _ = bisection(array, num)
        t_end = time.time()
        time_1.append(t_end - t_start)

        # Optimal BST
        t_start = time.time()
        _ = tree_search(root, num)
        t_end = time.time()
        time_2.append(t_end - t_start)
    print("Bisection time:", np.mean(time_1))
    print("Optimal BST time:", np.mean(time_2))