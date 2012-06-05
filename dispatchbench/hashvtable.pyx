import numpy as np

cdef extern from *:
    void* malloc(long)
    void free(void*)
    double sin(double)

from random import randint
from time import clock

cdef extern from "time.h":
    cdef struct timespec:
        long tv_sec
        long tv_nsec
    void clock_gettime(int, timespec*)
    int CLOCK_REALTIME

cdef double walltime():
  cdef timespec tv
  clock_gettime(CLOCK_REALTIME, &tv)
  return tv.tv_sec + 1e-9 * tv.tv_nsec



cdef extern from *:
    int likely(int)

cdef extern from "stdint.h":
    ctypedef unsigned long uint64_t

ctypedef struct u64_v2:
    uint64_t x, y

ctypedef struct entry_t:
    uint64_t id, id2, id3
    void *funcptr

cdef struct table_t:
#    u64_v2 masks
#    u64_v2 shifts
    uint64_t m1, m2
    unsigned char r1
    unsigned char r2
    unsigned char r3
    entry_t fallback
    entry_t funcs[64]

cdef extern:
    uint64_t the_id, the_id2, the_id3, h, fallback_id

cdef double times3(double x): return 3*x
cdef double times4(double x): return 4*x
cdef double times5(double x): return 5*x
cdef double times6(double x): return 6*x
cdef double times7(double x): return 7*x

cdef void populate_table(table_t* table):
#    table.masks.x = table.masks.y = 0x3F
    table.m1 = 0x3F
    table.m2 = 0x3F
    table.r1 = randint(0, 58)
    table.r2 = randint(0, 58)
    table.r3 = randint(0, 58)
    table.fallback.id = 0xffffffffffffff43
    table.fallback.funcptr = &times3
#    table.shifts.x = table.r1
#    table.shifts.y = table.r2
    for i in range(64):
        k = sin(i*i) * 5 + 5
        table.funcs[i].funcptr = &times3
        table.funcs[i].id =  0xffffffffffffff42
        table.funcs[i].id2 = 0xffffffffffffff52
        table.funcs[i].id3 = 0xffffffffffffff62
        ## if k < 2:
        ##     table.funcs[i] = &times3
        ## elif k < 4:
        ##     table.funcs[i] = &times4
        ## elif k < 6:
        ##     table.funcs[i] = &times5
        ## elif k < 8:
        ##     table.funcs[i] = &times6
        ## else:
        ##     table.funcs[i] = &times7

cdef extern:
    double table_lookup_first_element(double value, table_t *table, long k)
    double zero_table_lookup(double value, table_t *table, long k)
    double one_table_lookup(double value, table_t *table, long k)
    double two_table_lookup(double value, table_t *table, long k)
    double two_table_onecollision_lookup(double value, table_t *table, long k)
    double three_table_lookup(double value, table_t *table, long k)
    double doublemask(double value, table_t *table, long k)
    double doublemask2(double value, table_t *table, long k)

    double three_table_lookup_96(double value, table_t *table, long k)
    double three_table_lookup_128(double value, table_t *table, long k)
    double three_table_lookup_160(double value, table_t *table, long k)


hashtypes = ['direct', # 0
             'index', # 1
             'noshift', # 2
             'oneshift', # 3
             'twoshift', # 4
             'twoshift+fback', # 5
             'threeshift', # 6
             'doublemask', # 7
             'doublemask2', # 8
             'threeshift96', # 9
             'threeshift128',
             'threeshift160'] # 10

def time_table_lookup(int n, int repeats, double x, hashtype):
    cdef int which = hashtypes.index(hashtype)
    cdef unsigned long* hs
    cdef table_t table
    cdef double value = 0
    #cdef unsigned long h
    times = np.zeros(repeats)
    try:
        populate_table(&table)
        #hs = <unsigned long*>malloc(sizeof(unsigned long) * n)
        #for k in range(n):
        #    hs[k] = randint(0, 0xFFFFFFFFFFFFFFFF)

        for rep in range(repeats):
            h = randint(0, 0xFFFFFFFFFFFFFFFF)
            t = walltime()
            if which == 0:
                for k in range(n):
                    value += times4(x)
            elif which == 1:
                for k in range(n):
                    value += table_lookup_first_element(x, &table, k)
            elif which == 2:
                for k in range(n):
                    value += zero_table_lookup(x, &table, k)
            elif which == 3:
                for k in range(n):
                    value += one_table_lookup(x, &table, k)
            elif which == 4:
                for k in range(n):
                    value += two_table_lookup(x, &table, k)
            elif which == 5:
                for k in range(n):
                    value += two_table_onecollision_lookup(x, &table, k)
            elif which == 6:
                for k in range(n):
                    value += three_table_lookup(x, &table, k)
            elif which == 7:
                for k in range(n):
                    value += doublemask(x, &table, k)
            elif which == 8:
                for k in range(n):
                    value += doublemask2(x, &table, k)
            elif which == 9:
                for k in range(n):
                    value += three_table_lookup_96(x, &table, k)
            elif which == 10:
                for k in range(n):
                    value += three_table_lookup_128(x, &table, k)
            elif which == 11:
                for k in range(n):
                    value += three_table_lookup_160(x, &table, k)
            times[rep] = (walltime() - t) / n
        return times.min(), times.mean(), times.std(), value
    finally:
        free(hs)

the_id =  0xffffffffffffff42
the_id2 = 0xffffffffffffff52
the_id3 = 0xffffffffffffff62
fallback_id = 0xffffffffffffff43
