#!/usr/bin/env python3
import queue
import json
from flask import Flask, g, session, request
from flask import redirect, url_for
from flask import render_template, flash
import functools
from werkzeug.security import generate_password_hash, check_password_hash
from psycopg2.extras import DictCursor

from flask_bootstrap import Bootstrap
from forms import FilterCell, ScanBandOptions, AddJob, AutoScan
from werkzeug.datastructures import MultiDict
from markupsafe import Markup

from config import configure

app = Flask(__name__)
app = configure(app)
Bootstrap(app)

q = queue.Queue()
worker_status = {"status": None}
parsed_cells = []
autoscan = False

def get_db():
    if 'db' not in g:
        g.db = app.config['CONN_POOL'].getconn()
        g.db.autocommit = True
        g.cur = g.db.cursor(cursor_factory=DictCursor)
    return g.db, g.cur


def get_band_queue():
    db, cur = get_db()
    cur.execute(
        "SELECT band, start_earfcn, end_earfcn FROM scan_queue WHERE finished=False ORDER BY priority DESC;"
    )
    band, start_earfcn, end_earfcn = cur.fetchone()
    cur.close()
    return band, start_earfcn, end_earfcn


def update_band_status(start_earfcn, end_earfcn, band, finished=False):
    db, cur = get_db()
    cur.execute(
        "UPDATE scan_queue SET start_earfcn=%s, end_earfcn=%s, finished=%s WHERE band=%s;",
        (start_earfcn, end_earfcn, finished, band)
    )
    cur.close()


def update_cell_info(earfcn, sibs, scanned, reachable=False):
    db, cur = get_db()
    cur.execute(
        "UPDATE cells SET scanned=%s, sibs=%s, reachable=%s WHERE earfcn=%s;",
        (scanned, json.dumps(sibs), reachable, earfcn,)
    )
    cur.close()


@app.teardown_appcontext
def close_conn(e):
    cur = g.pop('cur', None)
    db = g.pop('db', None)
    if db is not None:
        cur.close()
        app.config['CONN_POOL'].putconn(db)


@app.route('/api/job', methods=['GET', 'POST'])
def job():
    global worker_status
    if request.method == "POST":
        q.put(request.get_json())
        return list(q.queue)
    
    if q.empty() and autoscan:
        band, start_earfcn, end_earfcn = get_band_queue()
        q.put({
                "job": "cell_search",
                "band": band,
                "start_earfcn": start_earfcn,
                "end_earfcn": end_earfcn
            })
    if q.empty():
        return "null"

    job = q.queue[0]
    worker_status["status"] = job["job"]
    return job

@app.route('/api/job/remove', methods=['GET', 'POST'])
def remove_job():
    if request.method == "POST":
        del q.queue[q.queue.index(request.get_json())]
    return "ok"

@app.route('/api/status', methods=['GET', 'POST'])
def status():
    global worker_status
    if request.method == "POST":
        worker_status = request.get_json()
        print(worker_status)
        if worker_status["status"] == "ok" and q.queue:
            q.get()
        if worker_status["name"] == "cell_search_cell_found":
            update_band_status( start_earfcn=worker_status["current_earfcn"]+1,
                                end_earfcn=worker_status["end_earfcn"],
                                band=worker_status["band"])
            q.put({
                    "job": "cell_parse",
                    "earfcn": worker_status["current_earfcn"]
                })
        
        if worker_status["name"] == "srsue_sibs_parsed":
            if "sib2" in worker_status["sibs"]:
                parsed_cells.append(worker_status["current_earfcn"])
                update_cell_info(   earfcn=worker_status["current_earfcn"],
                                    sibs=worker_status["sibs"],
                                    reachable=True,
                                    scanned=True)
            else:
                update_cell_info(   earfcn=worker_status["current_earfcn"],
                                    sibs=worker_status["sibs"],
                                    scanned=True)

            if "sib5" in worker_status["sibs"]:
                for neigh in worker_status["sibs"]["interFreqCarrierFreqList"]:
                    if autoscan and neigh["dl-CarrierFreq"] not in parsed_cells and neigh["dl-CarrierFreq"] not in [x["earfcn"] for x in q.queue]:
                        q.put({
                                "job": "cell_parse",
                                "earfcn": neigh["dl-CarrierFreq"]
                            })

        if worker_status["name"] == "cell_search_scan_done":
            update_band_status( start_earfcn=worker_status["current_earfcn"],
                                end_earfcn=worker_status["end_earfcn"],
                                band=worker_status["band"],
                                finished=True)

    return worker_status


@app.route('/', methods=['GET', 'POST'])
def index():
    form = FilterCell()
    db, cur = get_db()

    cur.execute(
        "SELECT band FROM cells GROUP BY band ORDER BY band DESC;"
    )
    bands = map(lambda x: x[0], cur.fetchall())
    form.band.choices += list(bands)

    band = "any"
    reachable_only = False
    if form.validate_on_submit():
        band = form.band.data
        reachable_only = form.reachable_only.data

    sql = "SELECT band, earfcn, TO_CHAR(last_scan, 'DD-MM-YYYY:HH:MI:SS') as last_scan, reachable, jsonb_object_keys(sibs) as sib from cells where scanned=True;"
    if band != "any":
        sql += f" and band={band}"
    if reachable_only:
        sql += " and reachable=True"
    sql += ";"
    cur.execute(
        sql
    )
    cells = cur.fetchall()
    cur.close()
    c = {}
    for cell in cells:
        if c.get(cell['earfcn']):
            c[cell['earfcn']]['sibs'] += f", {cell['sib']}"
        else:
            c[cell['earfcn']] = {}
            c[cell['earfcn']]['earfcn'] = cell['earfcn']
            c[cell['earfcn']]['band'] = cell['band']
            c[cell['earfcn']]['last_scan'] = cell['last_scan']
            c[cell['earfcn']]['reachable'] = cell['reachable']
            c[cell['earfcn']]['sibs'] = cell['sib']
            print(c)
    cells = c.values()
    return render_template('index.html', form=form, cells=cells)


@app.route('/jobs', methods=['GET', 'POST'])
def jobs():
    db, cur = get_db()
    if request.method == 'POST':
        form = ScanBandOptions()
        cur.execute(
            "UPDATE scan_queue SET start_earfcn=%s, end_earfcn=%s, priority=%s, finished=%s WHERE band=%s;",
            (form.start_earfcn.data,
             form.end_earfcn.data,
             form.priority.data,
             form.finished.data,
             form.band.data)
        )

    cur.execute(
        "SELECT * FROM scan_queue ORDER BY priority DESC;"
    )
    bands = cur.fetchall()
    jobs = [json.dumps(j, indent=4) for j in list(q.queue)]

    forms = {  band['band'] : ScanBandOptions(  formdata=MultiDict({
                                                        'start_earfcn': band['start_earfcn'],
                                                        'end_earfcn': band['end_earfcn'],
                                                        'priority': band['priority'],
                                                        'finished': band['finished']
                                                        }),
                                                band=band['band'])
                            for band in bands
                            }

    cur.close()
    return render_template('jobs.html',
                            scanned_arfcns=parsed_cells,
                            jobs=jobs,
                            bands=bands,
                            forms=forms)


@app.route('/jobs/add', methods=['GET', 'POST'])
def newjob():
    global autoscan
    form = AddJob()
    db, cur = get_db()
    cur.execute(
        "SELECT band FROM scan_queue band;"
    )
    bands = map(lambda x: x[0], cur.fetchall())
    form.band.choices += list(bands)
    autoscanForm = AutoScan(autoscan=autoscan)
    if request.method == 'POST':
        autoscan = autoscanForm.autoscan
    return render_template('newjob.html', form=form, autoscanForm=autoscanForm)


@app.route('/status')
def showstatus():
    return render_template('status.html', status=worker_status)


@app.route('/cell/<earfcn>')
def cells(earfcn):
    db, cur = get_db()
    cur.execute(
        "SELECT * FROM cells WHERE earfcn=%s;",
        (earfcn,)
    )
    cell = cur.fetchone()
    cur.close()
    sibs = json.dumps(cell['sibs'], indent=4)
    print(sibs)
    return render_template('cell.html', sibs=sibs)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=1337)
