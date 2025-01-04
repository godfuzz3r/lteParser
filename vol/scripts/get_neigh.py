#!/usr/bin/env python3
import sqlite3
import sys
import json

database = "./cells.sqlite"
earfcn = None
if "-d" in sys.argv:
    database = sys.argv[sys.argv.index("-d") + 1]
if "-e" in sys.argv:
    earfcn = int(sys.argv[sys.argv.index("-e") + 1])
if not earfcn:
    sys.stderr.write("earfcn need to find neigh")
    exit(1)

conn = sqlite3.connect(database)
cursor = conn.cursor()
try:
    cursor.execute("SELECT sib5 FROM cells WHERE earfcn = ?", (earfcn,))
except sqlite3.OperationalError:
    print("")
    exit(0)

cell = cursor.fetchone()
conn.close()

if not cell:
    sys.stderr.write(f"earfcn {earfcn} was not scanned")
    exit(1)

sib5 = cell[0]
if not sib5:
    sys.stderr.write(f"sib5 not found for {earfcn}")
    exit(1)

sib5 = json.loads(sib5)
neighs = [str(neigh["dl-CarrierFreq"]) for neigh in sib5["interFreqCarrierFreqList"]]
print(" ".join(neighs))
