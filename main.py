#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify
from multiprocessing import Process
import time
import configparser

from package.rigctlproxy import RigctlProxy
from package.cwserial import CwSerial

app = Flask(__name__)

rig_file = None

config = configparser.ConfigParser()
config.read('config.ini')

host = config['server']['host']
port = config['server']['port']
rig_file = config['device']['rigfile']
model_id = config['device']['rigmodelid']

print("host: " + host + ", port: " + port + ", rig_file: " + rig_file + ", model_id: " + model_id)
rp = RigctlProxy('2028', '/dev/ttyACM0')

def main():
    app.run(host=host, port=port)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_freq', methods=['GET'])
def get_freq():
    f = rp.get_freq()
    if f % 1000 == 0:
        fs = "{:.3f}".format(round(f / 1000000, 3))
    else:
        fs = "{:.5f}".format(round(f / 1000000, 5))
    return jsonify(
        freq=f,
        freqs=fs
    )

@app.route('/set_freq', methods=['GET'])
def set_freq():
    freq = request.args.get('freq')

    if not freq:
        return "freq can't be empty, and must be greater then 0", 400

    try:
        int(freq)
    except Exception as ex:
        return "freq must be integer, and must be greater then 0", 400

    if int(freq) <= 0:
        return "freq must be greater then 0", 400

    f = rp.set_freq(int(freq))

    return jsonify(
        freq=f
    )


@app.route('/get_mode', methods=['GET'])
def get_mode():
    m = rp.get_mode()
    return jsonify(mode=m)

@app.route('/set_mode', methods=['GET'])
def set_mode():
    mode = request.args.get('mode')

    if not mode:
        return "mode can't be empty", 400
    if mode not in ['USB', 'LSB', 'CW', 'CWR', 'RTTY', 'AM', 'FM']:
        return "mode incorrect", 400

    m = rp.set_mode(mode)

    return jsonify(
        mode=m
    )


@app.route('/set_ptt', methods=['GET'])
def set_ptt():
    ptt = request.args.get('ptt')
    if ptt not in [0, 1, '0', '1', 'RX', 'TX', 'rx', 'tx']:
        return jsonify(error='ptt parameter incorrect')
    p = 0
    if ptt in [1, '1', 'TX', 'tx']:
        p = 1
    if ptt in [0, '0', 'RX', 'rx']:
        p = 0
    rp.set_ptt(p)
    return jsonify(ptt=p)
    
@app.route('/get_ptt', methods=['GET'])
def get_ptt():
    p = rp.get_ptt()
    return jsonify(ptt=p)

@app.route('/send_cw', methods=['GET'])
def send_cw():
    wpm = request.args.get('wpm')
    phrase = request.args.get('phrase')

    if not wpm:
        return "wpm can't be empty, and must be between 10 and 35", 400

    try:
        int(wpm)
    except Exception as ex:
        return "wpm must be integer, and must be between 10 and 35", 400

    if 10 <= int(wpm) <= 35:
        pass
    else:
        return "wpm must be between 10 and 35", 400
    if not phrase:
        return "phrase can't be empty", 400

    process = Process(
        target=_send_cw,
        args=(wpm, phrase),
        daemon=True
    )
    process.start()

    return jsonify(wpm=wpm, phrase=phrase)


def _send_cw(wpm, phrase):
    cw = CwSerial(rig_file)
    rp.set_ptt(1)
    time.sleep(0.5)
    r = cw.send(wpm, phrase)
    time.sleep(0.5)
    rp.set_ptt(0)
    return r


if __name__ == '__main__':
    main()