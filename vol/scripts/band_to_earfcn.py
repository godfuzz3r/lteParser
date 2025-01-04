#!/usr/bin/env python3
import sqlite3
import sys

try:
    band = int(sys.argv[-1])
except:
    print("usage: ./earfcn_to_band.py -d <./lte_bands.sqlite3> <band>")
    exit()

database = "/vol/helpers/lte_bands.sqlite3"
if "-d" in sys.argv:
    database = sys.argv[sys.argv.index("-d") + 1]

conn = sqlite3.connect(database)
cursor = conn.cursor()
cursor.execute("SELECT start_earfcn,end_earfcn FROM lte WHERE band = ?;", (band,))

e = cursor.fetchone()
print(f"{e[0]} {e[1]}")
