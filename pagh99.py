from __future__ import division
import numpy as np

def make_table(hashes, k, b, epsilon):
    kg = int(np.log2(b))
    assert 2**kg == b
    n = len(hashes)
    mf = 2**k - 1
    mg = 2**kg - 1
    if b < (2 + epsilon) * (1 + epsilon) * n:
        raise ValueError("b too small or epsilon too large")
    for r in range(64):
        def f(h): return (h >> r) & mf
        def g(h): return h & mg

        # Use g to seperate into b bins.
        f_hashes = f(hashes).astype(np.uint16)
        g_hashes = g(hashes).astype(np.uint16)
        bc = np.bincount(g_hashes)

        # Criteria 1: f is 1:1 within each bin
        ok = False
        for ib in range(len(bc)):
            if bc[ib] > 1:
                f_hashes_bin = f_hashes[g_hashes == ib]
                if len(np.unique(f_hashes_bin)) != len(f_hashes_bin):
                    break
        else:
            ok = True
        if not ok:
            continue
        # Criteria 2: bins are even enough
        condnr = np.sum(bc[bc > 1]**2)
        #print bc
        #print condnr, n / (1 + epsilon)
        if condnr > n / (1 + epsilon):
            print bc
            print ValueError("criteria 2 failed")
        
        break # found hash

    D = np.zeros(b, np.uint16)
    T = np.zeros(n, bool)
    P = np.argsort(bc)[::-1]
    m = sum(bc > 1)

    # Deal with all bins with more than one element
    for ibin in P[:m]:
        # Scan for a displacement which makes this bin fill in
        # open slots only
        for d in range(n):
            f_hashes_bin = f_hashes[g_hashes == ibin]
            hval = f_hashes_bin ^ d
            if np.all(T[hval] == False):
                T[hval] = True
                D[ibin] = d
                break
        else:
            raise AssertError()
    # Deal with all bins with zero elements
    E = np.nonzero(T == False)[0]
    for ibin, slot in zip(P[m:], E):
        f_hashes_bin = f_hashes[g_hashes == ibin]
        if len(f_hashes_bin) == 0:
            continue
        assert len(f_hashes_bin) == 1
        D[ibin] = f_hashes_bin[0] ^ slot

    

    return r, D
        
        
            
            

def draw_hashes(rng, nitems):
    hashes = rng.randint(2**32, size=nitems).astype(np.uint64)
    hashes <<= 32
    hashes |= rng.randint(2**32, size=nitems).astype(np.uint64)
    return hashes

rng = np.random#.RandomState(43)
n = 32
hashes = draw_hashes(rng, n)
r, D = make_table(hashes, 5, 128, 0.1)
print r
print D
idx = ((hashes >> r) & 31) ^ D[hashes & 127]
print idx, len(np.unique(idx)) == len(idx)
