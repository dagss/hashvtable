from hashvtable import time_table_lookup, hashtypes

for hashtype in hashtypes:
    res = time_table_lookup(10**7, 10, 1.0, hashtype)
    print "%15s: min=%.2e  mean=%.2e  std=%.2e val=%f" % ((hashtype,) + res)
