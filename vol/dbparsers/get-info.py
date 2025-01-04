#!/usr/bin/env python3
import sqlite3
import sys
import json

database = "./cells.sqlite"
sib = None
mcc = None
mnc = None
filter_earfcn = None
if "-d" in sys.argv:
    database = sys.argv[sys.argv.index("-d") + 1]
if "-mcc" in sys.argv:
    mcc = sys.argv[sys.argv.index("-mcc") + 1]
if "-mnc" in sys.argv:
    mnc = sys.argv[sys.argv.index("-mnc") + 1]
if "-e" in sys.argv:
    filter_earfcn = int(sys.argv[sys.argv.index("-e") + 1])


def format_mcc_mnc(sib1):
    plmns = sib1["cellAccessRelatedInfo"]["plmn-IdentityList"]
    mcc_mnc_list = []
    for plmn in plmns:
        _mcc = "".join((str(x) for x in plmn["plmn-Identity"]["mcc"]))
        _mnc = "".join((str(x) for x in plmn["plmn-Identity"]["mnc"]))
        mcc_mnc_list.append(f"{_mcc}\t{_mnc}")

    mcc_mnc = "\n\t\t\t\t\t\t\t\t".join(mcc_mnc_list)
    return mcc_mnc


conn = sqlite3.connect(database)
cursor = conn.cursor()

cursor.execute(
    "SELECT band,earfcn,rsrp,sib1,sib3,sib5 FROM cells ORDER BY rsrp",
)

print("-" * 76)
for cell in cursor.fetchall():
    # print(cell)
    if filter_earfcn and cell[1] != filter_earfcn:
        continue

    # skip if sib1 not found
    if not cell[3]:
        continue

    sib1 = json.loads(cell[3])

    band = cell[0]
    earfcn = cell[1]
    rsrp = cell[2]
    tac = int(sib1["cellAccessRelatedInfo"]["trackingAreaCode"], 2)
    cellIdentity = int(sib1["cellAccessRelatedInfo"]["cellIdentity"], 2)
    priority = ""

    sib3 = None
    if cell[4]:
        sib3 = json.loads(cell[4])
        priority = int(
            sib3["cellReselectionServingFreqInfo"]["cellReselectionPriority"]
        )

    mcc_mnc = format_mcc_mnc(sib1)
    if mcc and mcc not in mcc_mnc:
        continue
    if mnc and mnc not in mcc_mnc:
        continue

    if isinstance(priority, int):
        outInfo = "{0}\t{1}\t{2}\t{3}\t{4:8d}\t{5:1d}\t\t{6}"
    else:
        outInfo = "{0}\t{1}\t{2}\t{3}\t{4:8d}\t{5:1s}\t\t{6}"
    print("Band\tEARFCN\tRSRP\tTAC\tcellIdentity\tPriority\tMCC\tMNC\t")
    print(outInfo.format(band, earfcn, rsrp, tac, cellIdentity, priority, mcc_mnc))

    if sib3:
        qRxLevMin = sib3["intraFreqCellReselectionInfo"]["q-RxLevMin"]
        sIntraSearch = sib3["intraFreqCellReselectionInfo"]["s-IntraSearch"]
        measIntraCond = sIntraSearch + qRxLevMin * 2

        sInterSearch = sib3["cellReselectionServingFreqInfo"]["s-NonIntraSearch"]
        measInterCond = sInterSearch * 2 + qRxLevMin * 2

        # q-RxLevMeas - q-RxLevMin*2 <= s-IntraSearch
        print(f"\nIntra-freq meas condition: cell RSRP <= {measIntraCond} dBm")
        print(f"Inter-freq meas condition: cell RSRP <= {measInterCond} dBm")
        print("")

    if cell[5]:
        sib5 = json.loads(cell[5])
        print("|-  neighbours")
        print("|-  earfcn\tallowedMeasBandwidth\tPriority")
        # print(sib5)
        # print(sib5["interFreqCarrierFreqList"])
        for neigh in sib5["interFreqCarrierFreqList"]:
            print("|")
            print(
                f"|-> {neigh['dl-CarrierFreq']:6d}\t{neigh['allowedMeasBandwidth']}\t\t\t{neigh['cellReselectionPriority']}"
            )
    else:
        print("sib5 for cell not found")
    print("-" * 76)
    print()
conn.close()
