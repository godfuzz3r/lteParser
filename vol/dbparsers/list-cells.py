#!/usr/bin/env python3
import sqlite3
import sys
import json

database = "./vol/cells.sqlite"
if "-d" in sys.argv:
    database = sys.argv[sys.argv.index("-d") + 1]

conn = sqlite3.connect(database)
cursor = conn.cursor()

cursor.execute(
    "SELECT band,earfcn,rsrp,mib,sib1,sib2,sib3,sib4,sib5,sib6,sib7,sib8,sib9,sib10,sib11,sib12,sib13 FROM cells ORDER BY rsrp",
)

print("Band\tEARFCN\t\tRSRP\tMIB parsed\tparsed SIBs\tpriority")
for cell in cursor.fetchall():
    band = cell[0]
    earfcn = cell[1]
    rsrp = cell[2]
    mib = cell[3]
    sibs = ""
    priority = None
    for i in range(13):
        sib = cell[i + 4]
        if sib:
            sibs += str(i + 1) + " "

    # sib3
    if cell[6]:
        priority = json.loads(cell[6])["cellReselectionServingFreqInfo"][
            "cellReselectionPriority"
        ]

    out = f"{band}\t{earfcn}\t\t{rsrp}\t{bool(mib)}\t\t{sibs}"
    if priority:
        out += f"\t{priority}"
    print(out)
