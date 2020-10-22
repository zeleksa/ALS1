import numpy as np
import time


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


"""
def hash_insert(hash_table, value, a, b, p, m):
    
    # Primary hash key
    hash_key = hash_fcn(value, a, b, p, m)
    
    if len(hash_table[hash_key]) >= 3:
        n_j = hash_table[hash_key][0] # Size of secondary table
        hash_key_secondary = hash_fcn(value, hash_table[hash_key][1], hash_table[hash_key][2], p, n_j**2)
        if len(hash_table[hash_key]) == 3:
            # Create new secondary table
            hash_table_secondary = [None for _ in range(n_j**2)]
            hash_table_secondary[hash_key_secondary] = value
            hash_table[hash_key].extend(hash_table_secondary)
        else:
            if hash_table[hash_key][3 + hash_key_secondary]:
                print('Kolize:', hash_table[hash_key][3 + hash_key_secondary], value)
            hash_table[hash_key][3 + hash_key_secondary] = value
    else:
        # Standard chaining
        hash_table[hash_key].append(value)
"""

"""
def count_secondary_slots(values, hash_table, a, b, p, Zp, Zp_star):
    for value in values:
        hash_key = hash_fcn(value, a, b, p, len(hash_table))
        if hash_table[hash_key]:
            if hash_table[hash_key][0] == 1:
                hash_table[hash_key][1] = np.random.choice(Zp_star)
                hash_table[hash_key][2] = np.random.choice(Zp)
            hash_table[hash_key][0] += 1
        else:
            hash_table[hash_key].extend([1, 0, 0])
"""


def hash_fcn(k, a, b, p, m):
    return ((a*k + b) % p) % m


def hash_table_size(hash_table):
    size = 0
    for i in range(len(hash_table)):
        size += len(hash_table[i])
    return size


def hash_insert_primary(values, hash_table, p, Zp, Zp_star):
    first = True
    # Zkontrolovat predpoklad, ze hashovaci funkce byla dobre zvolena
    while first or hash_table_size(hash_table) > 4*len(values):
        a = np.random.choice(Zp_star)
        b = np.random.choice(Zp)
        for value in values:
            hash_key = hash_fcn(value, a, b, p, len(hash_table))
            hash_table[hash_key].append(value)
        first = False
    return a, b


def hash_insert_secondary(values, hash_table, p, Zp, Zp_star):
    # Go through all slots and reorganize the table into secondary tables
    for i in range(len(hash_table)):
        slot = hash_table[i]
        collision = True
        if slot: # Slot can be empty
            if len(slot) == 1:
                # Slot with only one element can remain there (append a = b = 0 to it)
                hash_table[i] = [slot[0], [0, 0]]
                continue
            while collision:
                # We have to select a hash function (without collisions)
                collision = False
                a = np.random.choice(Zp_star)
                b = np.random.choice(Zp)
                n_j = len(slot)
                # Create secondary hash table with size (n_j)^2
                hash_table_secondary = [None for _ in range(n_j**2)]
                for value in slot:
                    # Insert all values from the slot into the secondary table
                    hash_key = hash_fcn(value, a, b, p, n_j**2)
                    if hash_table_secondary[hash_key]:
                        # If there was a collision, pick another hash function
                        collision = True
                        break
                    hash_table_secondary[hash_key] = value
                if not collision:
                    hash_table_secondary.append([a, b])
            hash_table[i] = hash_table_secondary
        

if __name__ == "__main__":
    
    # 4888 random values from 0 to 100000
    values = np.random.choice(100000, 4888, replace=False)
    avg_speedup = []

    for i in range(50):
        # Searched numbers (randomly selected from values list)
        nums = np.random.choice(values, 400)

        # 1) Bisection time measurement
        time_start = time.time()
        for t in nums:
            found, _ = bisection(values, t)
            #if t != found:
            #    print("[BISECTION] Number {} not found!".format(t, found))
        time_end = time.time()
        time_1 = time_end - time_start

        # 2) Hash time measurement
        time_start = time.time()
        
        # Prime number larger than all values
        p = 100003
        Zp_star = np.arange(p)
        Zp = np.arange(1, p)

        # Create hash table
        hash_table = [[] for _ in range(4888)]

        # Insert all values in primary table with chaining (find suitable a and b)
        a, b = hash_insert_primary(values, hash_table, p, Zp, Zp_star)

        # Reorganize values in primary table into secondary table
        hash_insert_secondary(values, hash_table, p, Zp, Zp_star)

        # Find numbers
        for t in nums:
            slot = hash_table[hash_fcn(t, a, b, p, len(hash_table))]
            found = slot[hash_fcn(t, slot[-1][0], slot[-1][1], p, len(slot) - 1)]
            #if t != found:
            #    print("[HASH] Number {} not found! Found {}.".format(t, found))
        time_end = time.time()
        time_2 = time_end - time_start

        print("Speedup:", time_1/time_2)
        avg_speedup.append(time_1/time_2)

    print("\nAverage speedup: {}".format(np.mean(avg_speedup)))


    # Zkontrolovat dusledek:
    """ Pokud vybereme n klíčů v hašovací tabulce velikosti m = n použitím hašovací
        funkce h náhodně vybrané z univerzální třídy hašovacích funkcí, a nastavíme
        velikost každé sekundární tabulky na mj = nj^2 pro j = 0, 1, . . . , m − 1, pak
        pravděpodobnost že celková paměť použitá pro sekundární hašovací tabulku
        překročí 4n je méně než 0.5. """
    # Pokud to překročí, tak musím zvolit jinou hash funkci