cimport numpy as cnp
from numpy cimport uint64_t
from numpy cimport uint8_t
import numpy as np

def count_collisions(cnp.ndarray[uint64_t] hashes,
                     cnp.ndarray[uint8_t] scratch,
                     uint64_t r1,
                     uint64_t r2,
                     uint64_t m1,
                     uint64_t m2):
    cdef int i, collisions
    cdef uint64_t h
    for i in range(scratch.shape[0]):
        scratch[i] = 0
    for i in range(hashes.shape[0]):
        h = ((hashes[i] >> r1) & m1) ^ ((hashes[i] >> r2) & m2)
        scratch[h] += 1

    collisions = 0
    for i in range(scratch.shape[0]):
        if scratch[i] >= 2:
            collisions += scratch[i] - 1

    return collisions


def find_hash_params(cnp.ndarray[uint64_t] hashes, int k):
    cdef cnp.ndarray[uint8_t] scratch = np.zeros(2**k, dtype=np.uint8)
    cdef int r1, r2, m1, m2
    cdef int n = 2**k
    cdef int collisions
    cdef int trials = 0
    for r1 in range(64 - k + 1):
        for r2 in range(r1, 64 - k + 1):
            for m1 in range(n-1, -1, -1):
                for m2 in range(n-1, -1, -1):
                    collisions = count_collisions(hashes, scratch, r1, r2, m1, m2)
                    trials += 1
                    if collisions == 0:
                        return 0, trials
    
    return 1, trials
