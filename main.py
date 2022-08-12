#!/usr/bin/env python3
import threading

from flask import Flask, render_template, request, jsonify, abort
from multiprocessing import Process
import time
import sys
import configparser
import logging
from logging import StreamHandler

from package.serialutil import SerialUtil
from package.cwserial import CwSerial
from package.webham import Webham

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

app = Flask(__name__)

configfilename = 'config.ini'
config = configparser.ConfigParser()
config.read(configfilename)

if not config.has_section('server'):
    config.add_section('server')

    if not config.has_option('server', 'host'):
        config['server']['host'] = '0.0.0.0'

    if not config.has_option('server', 'port'):
        config['server']['port'] = '5000'

    with open(configfilename, 'w') as configfile:
        config.write(configfile)

host = config['server']['host']
port = config['server']['port']

if config.has_option('rig', 'Model'):
    sModel = config['rig']['Model']
else:
    sModel = None

if config.has_option('rig', 'Device'):
    sDevice = config['rig']['Device']
else:
    sDevice = None

if config.has_option('rig', 'DataBits'):
    sDataBits = config['rig']['DataBits']
else:
    sDataBits = None

if config.has_option('rig', 'StopBits'):
    sStopBits = config['rig']['StopBits']
else:
    sStopBits = None

if config.has_option('rig', 'Rate'):
    sRate = config['rig']['Rate']
else:
    sRate = None

if config.has_option('rig', 'Parity'):
    sParity = config['rig']['Parity']
else:
    sParity = None

if config.has_option('rig', 'WriteDelay'):
    sWriteDelay = config['rig']['WriteDelay']
else:
    sWriteDelay = None


wh = Webham()
cw = CwSerial()

if sModel is not None and sDevice is not None:
    cw.setDevice(sDevice)
    wh.setRig(sModel, sDevice, sDataBits, sStopBits, sRate, sParity, sWriteDelay)


def main():
    app.run(host=host, port=port)
    wh.close()


def saveconfig(rigModel, rigDevice, rigDataBits, rigStopBits, rigRate, rigParity, rigWriteDelay):
    logger.debug('Save config...')
    config = configparser.ConfigParser()
    config.read(configfilename)

    global sModel
    sModel = rigModel
    global sDevice
    sDevice = rigDevice
    global sDataBits
    sDataBits = rigDataBits
    global sStopBits
    sStopBits = rigStopBits
    global sRate
    sRate = rigRate
    global sParity
    sParity = rigParity
    global sWriteDelay
    sWriteDelay = rigWriteDelay

    if not config.has_section('rig'):
        config.add_section('rig')

    if rigModel is not None:
        config['rig']['Model'] = rigModel
    else:
        if config.has_option('rig', 'Model'):
            config.remove_option('rig', 'Model')

    if rigDevice is not None:
        config['rig']['Device'] = rigDevice
    else:
        if config.has_option('rig', 'Device'):
            config.remove_option('rig', 'Device')

    if rigDataBits is not None:
        config['rig']['DataBits'] = rigDataBits
    else:
        if config.has_option('rig', 'DataBits'):
            config.remove_option('rig', 'DataBits')

    if rigStopBits is not None:
        config['rig']['StopBits'] = rigStopBits
    else:
        if config.has_option('rig', 'StopBits'):
            config.remove_option('rig', 'StopBits')

    if rigRate is not None:
        config['rig']['Rate'] = rigRate
    else:
        if config.has_option('rig', 'Rate'):
            config.remove_option('rig', 'Rate')

    if rigParity is not None:
        config['rig']['Parity'] = rigParity
    else:
        if config.has_option('rig', 'Parity'):
            config.remove_option('rig', 'Parity')

    if rigWriteDelay is not None:
        config['rig']['WriteDelay'] = rigWriteDelay
    else:
        if config.has_option('rig', 'WriteDelay'):
            config.remove_option('rig', 'WriteDelay')

    with open(configfilename, 'w') as configfile:
        config.write(configfile)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/init')
def init():
    return jsonify({"rig": {
        "rigModel": sModel,
        "rigDevice": sDevice,
        "rigDataBits": sDataBits,
        "rigStopBits": sStopBits,
        "rigRate": sRate,
        "rigParity": sParity,
        "rigWriteDelay": sWriteDelay
        }})


@app.route('/get_ports', methods=['GET'])
def get_ports():
    su = SerialUtil()
    ports = su.getAvailablePorts()
    return jsonify(ports=ports)


@app.route('/get_rigs', methods=['GET'])
def get_rigs():
    return jsonify(rigs=wh.getRigs())


@app.route('/get_paritys', methods=['GET'])
def get_paritys():
    return jsonify(paritys=wh.getParitys())


@app.route('/get_status', methods=['GET'])
def get_status():
    return jsonify(status=wh.getStatus())


@app.route('/set_rig', methods=['GET'])
def set_rig():
    rigModel = request.args.get('rigModel')
    rigDevice = request.args.get('rigDevice')

    if 'rigDataBits' in request.args:
        rigDataBits = request.args.get('rigDataBits')
        if rigDataBits == "":
            rigDataBits = None
    else:
        rigDataBits = None

    if 'rigStopBits' in request.args:
        rigStopBits = request.args.get('rigStopBits')
        if rigStopBits == "":
            rigStopBits = None
    else:
        rigStopBits = None

    if 'rigRate' in request.args:
        rigRate = request.args.get('rigRate')
        if rigRate == "":
            rigRate = None
    else:
        rigRate = None

    if 'rigParity' in request.args:
        rigParity = request.args.get('rigParity')
        if rigParity == "":
            rigParity = None
    else:
        rigParity = None

    if 'rigWriteDelay' in request.args:
        rigWriteDelay = request.args.get('rigWriteDelay')
        if rigWriteDelay == "":
            rigWriteDelay = None
    else:
        rigWriteDelay = None

    wh.setRig(rigModel, rigDevice, rigDataBits, rigStopBits, rigRate, rigParity, rigWriteDelay)

    cw.setDevice(rigDevice)

    saveconfig(rigModel, rigDevice, rigDataBits, rigStopBits, rigRate, rigParity, rigWriteDelay)

    return jsonify({"rig": {
        "rigModel": rigModel,
        "rigDevice": rigDevice,
        "rigDataBits": rigDataBits,
        "rigStopBits": rigStopBits,
        "rigRate": rigRate,
        "rigParity": rigParity,
        "rigWriteDelay": rigWriteDelay
        }})


@app.route('/get_freq', methods=['GET'])
def get_freq():
    try:
        f = wh.getFreq()
    except Exception as ex:
        logger.debug(ex)
        abort(404)
    if f % 1000 == 0:
        fs = "{:.3f}".format(round(f / 1000000, 3))
    else:
        fs = "{:.5f}".format(round(f / 1000000, 5))
    return jsonify(
        freq=f,
        freqs=fs
    )


@app.route('/get_mode', methods=['GET'])
def get_mode():
    try:
        m = wh.getMode()
    except Exception as ex:
        logger.debug(ex)
        abort(404)
    return jsonify(mode=m)


@app.route('/set_ptt', methods=['GET'])
def set_ptt():
    ptt = request.args.get('ptt')
    if ptt not in [0, 1, '0', '1', 'RX', 'TX', 'rx', 'tx']:
        abort(400)
    p = 0
    if ptt in [1, '1', 'TX', 'tx']:
        p = 1
    if ptt in [0, '0', 'RX', 'rx']:
        p = 0
    try:
        cw.breakcw()
        p = wh.setPtt(p)
    except ValueError as ex:
        logger.debug(ex)
        abort(400)
    except Exception as ex:
        logger.debug(ex)
        abort(404)
    return jsonify(ptt=p)


@app.route('/get_ptt', methods=['GET'])
def get_ptt():
    try:
        p = wh.getPtt()
    except Exception as ex:
        logger.debug(ex)
        abort(404)
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

    t = threading.Thread(target=_send_cw, args=(wpm, phrase,))
    t.start()

    return jsonify(wpm=wpm, phrase=phrase)

def _send_cw(wpm, phrase):
    if cw.getKeying():
        return
    if not wh.getStatus():
        return
    wh.setPtt(1)
    time.sleep(0.5)
    r = cw.send(wpm, phrase)
    time.sleep(0.5)
    wh.setPtt(0)
    return r

if __name__ == '__main__':
    main()
