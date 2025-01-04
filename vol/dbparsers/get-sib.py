#!/usr/bin/env python3
import sqlite3
import sys

database = "./cells.sqlite"
earfcn = None
sib = None
if "-d" in sys.argv:
    database = sys.argv[sys.argv.index("-d") + 1]

if "-e" in sys.argv:
    earfcn = sys.argv[sys.argv.index("-e") + 1]

if "-s" in sys.argv:
    sib = sys.argv[sys.argv.index("-s") + 1]

if not earfcn or not sib:
    print("usage: ./getsib.py -d <./cells.sqlite> -e <earfcn> -s <sib>")
    exit()

conn = sqlite3.connect(database)
cursor = conn.cursor()

cursor.execute(
    f"SELECT {sib} FROM cells WHERE earfcn = ?",
    (earfcn,),
)

cell = cursor.fetchone()
conn.close()

if not cell:
    sys.stderr.write(f"earfcn {earfcn} was not scanned")
    exit(1)

if not cell[0]:
    sys.stderr.write(f"{sib} not found for {earfcn}")
    exit(1)

print(cell[0])
