from hashvtable import time_table_lookup, hashtypes

hashtypes = ['threeshift', 'threeshift96', 'threeshift128', 'threeshift160']

for hashtype in hashtypes:
    res = time_table_lookup(10**7, 40, 1.0, hashtype)
    print "%15s: min=%.2e  mean=%.2e  std=%.2e val=%f" % ((hashtype,) + res)
