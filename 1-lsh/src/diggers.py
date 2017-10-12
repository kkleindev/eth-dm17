import sys
import numpy as np

# The number of bands in signature matrix.
N_BANDS = 20
# The number of rows per band.
N_ROWS_PER_BAND = 50
# Number of buckets for band hashing.
N_BUCKETS = 8193
# A large prime larger than the number of rows in the signature matrix, used for hashing.
PRIME = 3373
# Seed used for randomization in every instance of mapper.
SEED = 1337
#
SIMILARITY = .85


def create_signature(hash_functions, shingles):
    signature = np.ones(len(hash_functions)) * sys.maxint
    for j in range(len(hash_functions)):
        for i in range(len(shingles)):
            signature[j] = np.minimum(hash_functions[j](shingles[i]), signature[j])
    return signature

def similarity(shingles_1, shingles_2):
    set_a = set(shingles_1)
    set_b = set(shingles_2)
    return len(set_a.intersection(set_b)) / len(set_a.union(set_b))

def mapper(key, value):
    # key: None
    # value: one line of input file
    # initialize int-document array and id
    shingles = value.split(' ')
    document_id = int(shingles[0].split('_')[1])
    shingles = map(int, shingles[1:])
    n_rows = N_BANDS * N_ROWS_PER_BAND
    np.random.seed(seed=SEED)

    #hash_functions = map(lambda x: gen_hashfunc(n_rows), range(n_rows))
    hash_functions = [gen_hash_function(n_rows) for i in range(n_rows)]

    signature = create_signature(hash_functions, shingles)

    band_hash_functions = [gen_hash_function(N_BUCKETS)
            for i in range(N_ROWS_PER_BAND)]

    result = np.empty(N_BANDS)
    for i in range(N_BANDS):
        band = signature[i * N_ROWS_PER_BAND:(i+1) * N_ROWS_PER_BAND]
        sum_hashes = 0
        for j in range(N_ROWS_PER_BAND):
            sum_hashes += band_hash_functions[j](band[j])
        result[i] = sum_hashes % N_BUCKETS
    #yield [(bucket, (document_id, shingles)) for bucket in result]  # this is how you yield a key, value pair
    yield [(bucket, value) for bucket in result]

def reducer(key, values):
    # key: key from mapper used to aggregate
    # values: list of all value for that key
    duplicates = []
    for i in range(len(values)):
        #(document_id_1, shingles_1) = values[i]
        shingles_1 = values[i].split(' ')
        document_id_1 = int(shingles_1[0].split('_')[1])
        shingles_1 = map(int, shingles_1[1:])
        for j in range(i + 1, len(values)):
            #(document_id_2, shingles_2) = values[j]
            shingles_2 = values[j].split(' ')
            document_id_2 = int(shingles_2[0].split('_')[1])
            shingles_2 = map(int, shingles_2[1:])
            if similarity(shingles_1, shingles_2) >= SIMILARITY:
                duplicates.append(
                        (max(document_id_1, document_id_2), min(document_id_1, document_id_2)))
    print duplicates
    if len(duplicates) != 0:
        yield duplicates # this is how you yield a key, value pair

def gen_hash_function(n_rows):
    a = np.random.randint(1, n_rows)
    b = np.random.randint(0, n_rows)
    return lambda s: ((np.multiply(a, s) + b) % PRIME) % n_rows

# Simple test case for min hashing. Inspired by lecture slide 18 from week 3.
def test_min_hash():
    shingles_1 = [0, 1, 5, 6]
    shingles_2 = [2, 3, 4]
    shingles_3 = [0, 5, 6]
    permutation_1 = [2, 3, 6, 5, 0, 1, 4]
    permutation_2 = [3, 1, 0, 2, 5, 6, 4]
    permutation_3 = [0, 2, 6, 5, 1, 4, 3]
    # Create mock hash functions permuting the shingles.
    hash_functions = []
    hash_functions.append(lambda s: permutation_1[s % 7])
    hash_functions.append(lambda s: permutation_2[s % 7])
    hash_functions.append(lambda s: permutation_3[s % 7])
    signature_1 = create_signature(hash_functions, shingles_1)
    signature_2 = create_signature(hash_functions, shingles_2)
    signature_3 = create_signature(hash_functions, shingles_3)
    print signature_1
    print signature_2
    print signature_3

def min_hash():
    return 0

def band_hash():
    return 0
