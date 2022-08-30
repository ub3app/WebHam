import argparse
import logging
from logging import StreamHandler
import sys

import serial
import time
import threading
from os.path import exists


class CwSerial:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)

    port = None
    wpm_to_ms = 430
    killcw = False

    inprogress = False

    cw = {
        'A': '.-',
        'B': '-...',
        'C': '-.-.',
        'D': '-..',
        'E': '.',
        'F': '..-.',
        'G': '--.',
        'H': '....',
        'I': '..',
        'J': '.---',
        'K': '-.-',
        'L': '.-..',
        'M': '--',
        'N': '-.',
        'O': '---',
        'P': '.--.',
        'Q': '--.-',
        'R': '.-.',
        'S': '...',
        'T': '-',
        'U': '..-',
        'V': '...-',
        'W': '.--',
        'X': '-..-',
        'Y': '-.--',
        'Z': '--..',
        '1': '.----',
        '2': '..---',
        '3': '...--',
        '4': '....-',
        '5': '.....',
        '6': '-....',
        '7': '--...',
        '8': '---..',
        '9': '----.',
        '0': '-----',
        '?': '..--..',
        '/': '-..-.',
        '.': '.-.-.-',
        ',': '--..--',
        '=': '-...-',
        'Ч': '---.',
        'Ш': '----',
        'Э': '..--..',
        'Ю': '..--',
        'Я': '.-.-'}

    symb_en = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    symb_ru = 'АБЦДЕФГХИЙКЛМНОПЩРСТУЖВЬЫЗ'

    def __init__(self):
        pass

    def setDevice(self, port):
        self.port = port

    def breakcw(self):
        self.killcw = True

    def getKeying(self):
        return self.inprogress

    def send(self, w, phrase):
        if self.inprogress is True:
            self.logger.debug('Skip cw already in cw')
            return
        try:
            wpm = int(w)
        except Exception as ex:
            return "error: wpm must be integer"

        if 10 <= wpm <= 35:
            pass
        else:
            return "error: wpm must be between 10 and 35"

        if not phrase:
            return "error: phrase can't be empty"

        if exists(self.port):
            self.logger.debug('CwSerial set port: ' + self.port)
            ser = serial.Serial()
            ser.port = self.port
            ser.rts = False
            ser.dtr = False
            ser.open()
        else:
            raise Exception("Device file not found: " + self.port)

        p = phrase.upper()

        p_tr = ""
        tr = False
        for c in p:
            for i, s in enumerate(self.symb_ru):
                if c == s:
                    p_tr += self.symb_en[i]
                    tr = True
                    break
            if not tr:
                p_tr += c
            else:
                tr = False

        p = p_tr
        self.logger.debug('CwSerial phrase: ' + p)

        self.killcw = False
        self.inprogress = True
        t = threading.Thread(target=self._send, args=(wpm, p, ser,))
        t.start()
        t.join()
        self.inprogress = False
        if ser.is_open:
            ser.close()

        return "wpm: " + str(wpm) + ", phrase:" + p

    def _send(self, wpm, phrase, ser):
        if not ser.is_open:
            return

        dit = round(self.wpm_to_ms / wpm * 3 / 1000, 4)
        dah = round(self.wpm_to_ms / wpm * 7 / 1000, 4)

        cwseq = ''

        for element in phrase:
            if element != ' ':
                if element in self.cw:
                    cwseq += self.cw[element] + '1'
            else:
                cwseq += '3'

        time.sleep(0.1)

        for element in cwseq:
            if self.killcw:
                self.inprogress = False
                break

            if element == '.':
                ser.setDTR(True)
                time.sleep(dit)
                ser.setDTR(False)
                time.sleep(dit)
            elif element == '-':
                ser.setDTR(True)
                time.sleep(dah)
                ser.setDTR(False)
                time.sleep(dit)
            else:
                space = dit * int(element)
                time.sleep(space)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='cwserial')
    parser.add_argument('-d', required=True, type=str, default='/dev/ttyACM0', help='device')
    parser.add_argument('-wpm', required=True, type=int, default=16, help='WPM')
    parser.add_argument('phrase', type=str, help='Phrase')
    args = parser.parse_args()

    device = args.d
    wpm = args.wpm
    phrase = args.phrase

    cw = CwSerial()
    cw.setDevice(device)
    print(cw.send(wpm, phrase))
