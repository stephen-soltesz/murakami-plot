#!/usr/bin/env python

#%%
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from datetime import datetime
import sys
import json
import threading
import glob
import random

import io
import flask
import csv

PORT_NUMBER = 8080
history_filename = 'history.csv'

app = flask.Flask(__name__)
lock = threading.Lock()


@app.route('/', methods=['GET'])
def home():
    response = """
    <html><body>
        <img src="/scatter_seconds"/>
        <img src="/scatter_hours?offset=-5"/>
        <img src="/time"/>
    </body></html>
    """
    return flask.Response(
        response, content_type='text/html; charset=utf-8')


@app.route('/scatter_hours', methods=['GET'])
def scatter_hours():
    with lock:
        try:
            offset = int(flask.request.args.get('offset', 0))
        except ValueError:
            offset = 0
        hourly, _, upload, download = load_image(offset)
        output = plot_scatter(
            ((hourly, download, 'download'),
             (hourly, upload, 'upload')),
            title='Test-rate vs Hour-of-day', xlabel='Hour (offset {0})', offset=offset)
        return flask.send_file(output, mimetype='image/svg+xml')


@app.route('/scatter_seconds', methods=['GET'])
def scatter_seconds():
    with lock:
        timeu, upload = load_data('test_keys', 'test_c2s', 'sender_data')
        timed, download = load_data('test_keys', 'test_s2c', 'receiver_data')
        output = plot_scatter(
            ((timed, download, 'download'),
             (timeu, upload, 'upload')),
            title='Test-rate vs Seconds', xlabel='Seconds', xlim=(0, 11))
        return flask.send_file(output, mimetype='image/svg+xml')


@app.route('/time', methods=['GET'])
def time():
    with lock:
        _, dates, upload, download = load_image()
        output = plot_time(dates, upload, download)
        return flask.send_file(output, mimetype='image/svg+xml')


def load_data(keys, test, samples):
    time = []
    rate = []
    for data_filename in glob.glob('data/*.njson'):
        data = json.loads(open(data_filename).read())
        if keys in data and test  in data[keys]:
            if len(data[keys][test]) > 0:
                if data[keys][test][0]:
                    d = data[keys][test][0][samples]
                    for sample in d:
                        time.append(sample[0] + random.random() * 0.5)
                        rate.append(sample[1])
                else:
                    print data_filename, 'missing', samples
            else:
                print data_filename, 'missing array for', test
        else:
            print data_filename, 'missing', keys
    return time, rate


def load_image(offset=0):
    hourly = []
    dates = []
    y_upload = []
    y_download = []
    with open(history_filename) as csvfile:
      reader = csv.DictReader(csvfile)
      rows = []
      for row in reader:
          rows.append(row)
      
      for row in sorted(rows, key=lambda r: r['Datetime']):
        _, hms = row['Datetime'].split()
        h, m, s = hms.split(':')

        ts = int(h) * 3600 + int(m) * 60 + int(s)
        dt = datetime.strptime(row['Datetime'], '%Y-%m-%d %H:%M:%S')
        dl = float(row['Download'])
        ul = float(row['Upload'])

        hourly.append(((float(ts) / 3600.0) + offset) % 24)
        dates.append(dt)
        y_download.append(dl / 1000.0)
        y_upload.append(ul / 1000.0)
    return hourly, dates, y_upload, y_download


def plot_scatter(time_rate_labels, title='', offset=0, xlim=(0, 24), xlabel=''):
    plt.figure(figsize=(8, 6))
    m = None
    for i in range(len(time_rate_labels)):
        t, r, l = time_rate_labels[i]
        m = max(max(r), m)
        plt.scatter(t, r, s=9, label=l)
        plt.plot(xlim, (np.average(r), np.average(r)))
    plt.title(title)
    plt.ylabel('Mbps')
    if xlabel:
        plt.xlabel(xlabel.format(offset))

    plt.xlim(xlim)
    plt.ylim(0, 1.2 * m)
    plt.legend()
    print 'scatter-plot.svg'

    output = io.BytesIO()
    plt.savefig(output, format="svg")
    output.seek(0, 0)
    return output


def plot_time(dates, upload, download):
    plt.figure(figsize=(8, 6))
    plt.plot_date(dates, download, ls='-', ms=4, label="download")
    plt.plot_date(dates, upload, ls='-', ms=4, label="upload")
    plt.title('Test Rates Over Time')
    plt.ylabel('Mbps')
    plt.xlabel('Date')

    plt.ylim(0, 1.2 * max(download))
    plt.tick_params(axis='x', labelrotation=-45)
    plt.legend()
    print 'time-plot.svg'

    output = io.BytesIO()
    plt.savefig(output, format="svg")
    output.seek(0, 0)
    return output


def main():
    global history_filename

    print 'Starting server on port ' , 8000
    print sys.argv
    if len(sys.argv) > 1:
        history_filename = sys.argv[1]
    app.run(host='0.0.0.0', port=8000, debug=False)


if __name__ == '__main__':
    main()
