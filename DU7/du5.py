import numpy as np


def get_quadrant(x, y, n):
    r = (2**n) / 2
    if x < r and y < r:
        return 0
    if x < r and y >= r:
        return 1
    if x >= r and y >= r:
        return 2
    if x >= r and y < r:
        return 3
    print("QUADRANT ERROR")
    return None


def hilbert_value(x, y, n):
    if n == 0:
        return 0
    if n == 1:
        if x == 0 and y == 0:
            return 0
        if x == 0 and y == 1:
            return 1
        if x == 1 and y == 1:
            return 2
        if x == 1 and y == 0:
            return 3
    else:
        quad = get_quadrant(x, y, n)
        prev_len = quad*(2**(n-1) * 2**(n-1))

        if quad == 0:
            return prev_len + hilbert_value(y, x, n-1)
        if quad == 1:
            return prev_len + hilbert_value(x, y - 2**(n-1), n-1)
        if quad == 2:
            return prev_len + hilbert_value(x - 2**(n-1), y - 2**(n-1), n-1)
        if quad == 3:
            return prev_len + hilbert_value(2**(n-1) - 1 - y, 2**n - 1 - x, n-1)
    print("CURVE ERROR")
    return None

if __name__ == "__main__":
    for n in range(5):
        print(f"N = {n}:")
        indices = np.array([np.repeat(np.arange(2**n), 2**n), np.tile(np.arange(2**n), 2**n)]).T
        for idx in indices:
            x, y = idx[0], idx[1]
            print(f"    H value for [{x},{y}] = {hilbert_value(x, y, n)}")