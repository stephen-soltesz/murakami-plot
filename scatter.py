#!/usr/bin/env python

#%%
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from datetime import datetime
import sys
import threading

import io
import flask
import csv

PORT_NUMBER = 8080
history_filename = 'history.csv'

app = flask.Flask(__name__)
lock = threading.Lock()


@app.route('/', methods=['GET'])
def home():
    #print 'request', flask.request.form
    response = """
    <html><body>
        <img src="/scatter"/>
        <img src="/time"/>
    </body></html>
    """
    return flask.Response(
        response, content_type='text/html; charset=utf-8')


@app.route('/scatter', methods=['GET'])
def scatter():
    #print 'request', flask.request.form
    with lock:
        hourly, _, upload, download = load_image()
        output = plot_scatter(hourly, upload, download)
        return flask.send_file(output, mimetype='image/svg+xml')


@app.route('/time', methods=['GET'])
def time():
    #print 'request', flask.request.form
    with lock:
        _, dates, upload, download = load_image()
        output = plot_time(dates, upload, download)
        return flask.send_file(output, mimetype='image/svg+xml')


def load_image():
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

        hourly.append(((float(ts) / 3600.0) - 5) % 24)
        dates.append(dt)
        y_download.append(dl / 1000.0)
        y_upload.append(ul / 1000.0)
    return hourly, dates, y_upload, y_download


def plot_scatter(hourly, upload, download):
    plt.figure(figsize=(8, 6))
    plt.scatter(hourly, download, s=9, label="download")
    plt.plot((0, 24), (np.average(download), np.average(download)))
    plt.scatter(hourly, upload, s=9, label="upload")
    plt.plot((0, 24), (np.average(upload), np.average(upload)))
    plt.title('Scatter Plot - Test-rate vs Hour-of-day')
    plt.ylabel('Mbps')
    plt.xlabel('Hour (EST)')

    plt.xlim(0, 24)
    plt.ylim(0, 1.2 * max(download))
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
