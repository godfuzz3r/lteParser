#!/usr/bin/env python3
import time
import sys
import json
import sqlite3


def read_line(log, timeout):
    buffer_line = ""
    while 1:
        if time.time() > timeout:
            return ""
        line = log.readline()
        if not len(line):
            continue
        buffer_line += line
        if buffer_line[-1] == "\n":
            return buffer_line


def get_json(line):
    if "[I] Content: " in line:
        try:
            return json.loads(line.split("[I] Content:")[1])
        except json.decoder.JSONDecodeError:
            return None
    elif "[powermeasure]" in line:
        try:
            return json.loads(line.split("[powermeasure]")[1])
        except json.decoder.JSONDecodeError:
            return None
    return None


def earfcn_to_band(earfcn):
    conn = sqlite3.connect(band_database)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT band FROM lte where ? >= start_earfcn and ? <= end_earfcn;",
        (earfcn, earfcn),
    )

    band = cursor.fetchone()
    if not band:
        return ""
    if not band[0]:
        return ""
    return band[0]


def insert_cell(cursor, earfcn, sibType, info):
    cursor.execute(
        f"""INSERT INTO cells (earfcn, band, time, {sibType})
            VALUES
            (?, ?, DateTime('now'), ?)""",
        (earfcn, earfcn_to_band(earfcn), info),
    )


def update_cell(cursor, earfcn, sibType, info):
    cursor.execute(
        f"""UPDATE cells
            SET time = DateTime('now'), {sibType} = ?
            WHERE earfcn = ?
            """,
        (info, earfcn),
    )


def write_db(db_path, earfcn, sibType, info):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS cells (
                    earfcn integer NOT NULL UNIQUE,
                    band TEXT DEFAULT NULL,
                    time timestamp DEFAULT NULL,
                    rsrp TEXT DEFAULT NULL,
                    mib TEXT DEFAULT NULL,
                    sib1 TEXT DEFAULT NULL,
                    sib2 TEXT DEFAULT NULL,
                    sib3 TEXT DEFAULT NULL,
                    sib4 TEXT DEFAULT NULL,
                    sib5 TEXT DEFAULT NULL,
                    sib6 TEXT DEFAULT NULL,
                    sib7 TEXT DEFAULT NULL,
                    sib8 TEXT DEFAULT NULL,
                    sib9 TEXT DEFAULT NULL,
                    sib10 TEXT DEFAULT NULL,
                    sib11 TEXT DEFAULT NULL,
                    sib12 TEXT DEFAULT NULL,
                    sib13 TEXT DEFAULT NULL
                    );"""
    )
    conn.commit()
    cursor.execute(
        f"""SELECT earfcn FROM cells WHERE earfcn = ?""",
        (earfcn,),
    )
    col_exists = cursor.fetchone()
    if not col_exists:
        insert_cell(cursor, earfcn, sibType, info)
        conn.commit()
        conn.close()
        return

    cursor.execute(
        f"""SELECT {sibType} FROM cells WHERE earfcn = ?""",
        (earfcn,),
    )
    sib = cursor.fetchone()[0]
    if len(info) >= len(str(sib)):
        update_cell(cursor, earfcn, sibType, info)

    conn.commit()
    conn.close()


### parse params ###
file_name = "/tmp/ue.log"
timeout = 30
timeout_add = 30
earfcn = None
database = None
band_database = "/vol/helpers/lte_bands.sqlite3"
if "-f" in sys.argv:
    file_name = sys.argv[sys.argv.index("-f") + 1]
if "-t" in sys.argv:
    timeout = int(sys.argv[sys.argv.index("-t") + 1])
if "-T" in sys.argv:
    timeout_add = int(sys.argv[sys.argv.index("-T") + 1])
if "-e" in sys.argv:
    earfcn = int(sys.argv[sys.argv.index("-e") + 1])
if "-d" in sys.argv:
    database = sys.argv[sys.argv.index("-d") + 1]
if "-D" in sys.argv:
    band_database = sys.argv[sys.argv.index("-D") + 1]

timeout = time.time() + timeout


### check params ###
if database and not earfcn:
    sys.stderr.write("need earfcn to write to database")
    exit(1)

if database:
    try:
        conn = sqlite3.connect(database)
        conn.close()
    except Exception as e:
        sys.stderr.write(e)
        exit(1)

if band_database:
    try:
        conn_bands = sqlite3.connect(band_database)
        conn_bands.close()
    except Exception as e:
        sys.stderr.write(e)
        exit(1)


### wait for file ###
file_err = FileNotFoundError
while file_err:
    try:
        log = open(file_name)
        file_err = None
    except FileNotFoundError:
        if time.time() > timeout:
            sys.stderr.write("Can't open srsue log file, exiting")
            exit(1)
        time.sleep(1)


retrieved = {}
need_retrieve = ["rsrp", "mib", "sib1", "sib2"]
cell_sibs = []
while True:
    if time.time() > timeout:
        break

    line = read_line(log, timeout)
    if not line:
        break

    msgs = get_json(line)
    if not msgs:
        continue

    for msg in msgs:
        # power measure
        if "rsrp" in msg:
            if "rsrp" in retrieved:
                continue
            print(json.dumps(msg), flush=True)
            if database:
                write_db(database, earfcn, "rsrp", str(msg["rsrp"]))

        # mib
        if "BCCH-BCH-Message" in msg:
            if "mib" in retrieved:
                continue
            mib = msg["BCCH-BCH-Message"]["message"]
            retrieved["mib"] = mib
            out = {"type": "mib", "info": mib}
            print(json.dumps(out), flush=True)

            timeout += timeout_add
            if database:
                write_db(database, earfcn, "mib", json.dumps(mib))

        # sib
        if "BCCH-DL-SCH-Message" in msg:
            c1 = msg["BCCH-DL-SCH-Message"]["message"]["c1"]

            # sib1
            if "systemInformationBlockType1" in c1:
                if "sib1" in retrieved:
                    continue

                info = c1["systemInformationBlockType1"]
                retrieved["sib1"] = info
                cell_sibs = [
                    sib.replace("Type", "")  # sibType7 -> sib7
                    for mapping in info["schedulingInfoList"]
                    for sib in mapping["sib-MappingInfo"]
                ]
                need_retrieve += cell_sibs
                out = {"type": "sib1", "info": info}
                print(json.dumps(out), flush=True)

                timeout += timeout_add
                if database:
                    write_db(database, earfcn, "sib1", json.dumps(info))
            else:
                sib_list = c1["systemInformation"]["criticalExtensions"][
                    "systemInformation-r8"
                ]["sib-TypeAndInfo"]
                for type_info in sib_list:
                    for sibType, info in type_info.items():
                        if sibType not in retrieved:
                            retrieved[sibType] = info
                            out = {"type": sibType, "info": info}
                            print(json.dumps(out), flush=True)

                            timeout += timeout_add
                            if database:
                                write_db(database, earfcn, sibType, json.dumps(info))

    all_retrieved = all([need_sib in retrieved.keys() for need_sib in need_retrieve])
    if all_retrieved:
        break
