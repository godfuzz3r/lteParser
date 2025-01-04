#!/usr/bin/env python3
import sqlite3
import sys

try:
    earfcn = int(sys.argv[-1])
except:
    print("usage: ./earfcn_to_band.py -d <./lte_bands.sqlite3> <earfcn>")
    exit()

database = "/vol/helpers/lte_bands.sqlite3"
if "-d" in sys.argv:
    database = sys.argv[sys.argv.index("-d") + 1]

conn = sqlite3.connect(database)
cursor = conn.cursor()
cursor.execute(
    "SELECT band FROM lte where ? >= start_earfcn and ? <= end_earfcn;",
    (earfcn, earfcn),
)

band = cursor.fetchone()[0]
print(band)
