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

conn = sqlite3.connect(database)
cursor = conn.cursor()

cursor.execute(
    "SELECT earfcn FROM cells",
)

cells = cursor.fetchall()
conn.close()

print(" ".join([str(x[0]) for x in cells]))
