from __future__ import division
import numpy as np

class NoPerfectTableError(Exception):
    pass

def make_table(keys, n, b, max_d):
    kn = int(np.log2(n))
    if 2**kn != n:
        raise ValueError('Please make n a power of 2')
    kb = int(np.log2(b))
    if 2**kb != b:
        raise ValueError('Please make b a power of 2')

    mask_f = 2**kn - 1
    mask_g = (2**kb - 1) & (max_d - 1)

    # B: number of keys in each bin
    # P: B[P] is sorted from largest to smallest bin
    # D: displacement array
    # T: slot taken array

    # Use g-hash to seperate into b bins.
    g_hashes = (keys & mask_g).astype(np.uint16)
    B = np.bincount(g_hashes)
    P = np.argsort(B)[::-1]
    m = sum(B > 1)

    def find_displacements(r):
        D = np.zeros(b, np.uint16)
        T = np.zeros(n, bool)

        # Each r gives rise to a seperate f-hash
        f_hashes = (keys >> r) & mask_f

        # Deal with bins with more than one element first
        for binidx in P[:m]:
            binsize = B[binidx]
            f_hashes_bin = f_hashes[g_hashes == binidx]

            # Step 1: Validate that f is 1:1 on bin
            if len(np.unique(f_hashes_bin)) != binsize:
                return None
            
            # Step 2: Find displacement that makes this bin fill in open
            # slots only
            for d in range(min(b, max_d, n)):
                hashval = f_hashes_bin ^ d
                if np.all(T[hashval] == False):
                    T[hashval] = True
                    D[binidx] = d
                    break
            else:
                # Couldn't find displacement
                return None

        # Deal with remaining trivial bins
        E = np.nonzero(T == False)[0].astype(np.uint64)
        for binidx, slot in zip(P[m:], E):
            f_hashes_bin = f_hashes[g_hashes == binidx]
            if len(f_hashes_bin) == 0:
                break # done
            assert len(f_hashes_bin) == 1
            D[binidx] = f_hashes_bin[0] ^ slot

        # Done
        return D

    for r in range(64, -1, -1):
        D = find_displacements(r)
        if D is not None:
            break
    else:
        raise NoPerfectTableError("Unable to find perfect hash, please increase b")

    return r, D, mask_f, mask_g
    
            

def draw_hashes(rng, nitems):
    hashes = rng.randint(2**32, size=nitems).astype(np.uint64)
    hashes <<= 32
    hashes |= rng.randint(2**32, size=nitems).astype(np.uint64)
    return hashes

def simulate(rng, nsim, c, n, b, max_d):
    failures = 0
    trycounts = np.ones(nsim) * 65
    for i in range(nsim):
        keys = draw_hashes(rng, c)
        try:
            r, D, mask_f, mask_g = make_table(keys, n, b, max_d)
        except NoPerfectTableError:
            failures += 1
        else:
            trycounts[i] = 64 - r
            idx = ((keys >> r) & mask_f) ^ D[keys & mask_g]
            assert len(np.unique(idx)) == len(idx)
    return failures, np.mean(trycounts), np.max(trycounts)
    

rng = np.random  #.RandomState(43)
nsim = 1000
for n in [8, 16, 32, 64, 128, 256, 512, 1024, 2048]:
    c = n
    b = n
    failures, try_mean, try_max = simulate(rng, nsim, c, n, b, 2**16)
    print 'n=%4d   b=%5d   failure-rate=%.4f   try-mean=%.2f  try-max=%d ' % (
        n, b, failures / nsim, try_mean, try_max)
