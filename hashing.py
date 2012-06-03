from __future__ import division
import numpy as np
import sys
from findhash import count_collisions, find_hash_params

def simulate(nitems, nslots, nsims=100):
    k = int(np.log2(nslots))
    assert 2**k == nslots
    success_count = 0
    trials = 0
    for isim in range(nsims):
        hashes = np.random.randint(2**32, size=nitems).astype(np.uint64)
        hashes <<= 32
        hashes |= np.random.randint(2**32, size=nitems).astype(np.uint64)
        ncoll, simtrials = find_hash_params(hashes, k)
        if ncoll == 0:
            success_count += 1
        trials += simtrials
    return success_count / nsims, trials

for nitems, nslots in [(6, 8),
                       (8, 8),
                       (20, 32),
                       (20, 64),
                       (30, 64),
                       (30, 128),
                       (64, 256),
                       (64, 512)]:
    print 'nitems=%d, nslots=%d, P(success)=%.2f trials=%d' % ((nitems,
                                                                nslots,) +
                                                               simulate(nitems, nslots))
    sys.stdout.flush()
