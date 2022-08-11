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

    ser = None
    wpm_to_ms = 500
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
        '=': '-...-'}

    def __init__(self):
        pass

    def setDevice(self, port):
        if exists(port):
            self.logger.debug('CwSerial set port: ' + port)
            self.ser = serial.Serial(port)
            self.ser.setDTR(False)
        else:
            raise Exception("Device file not found: " + port)

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

        p = phrase.upper()

        self.killcw = False
        self.inprogress = True
        t = threading.Thread(target=self._send, args=(wpm, p,))
        t.start()
        t.join()
        self.inprogress = False

        return "wpm: " + str(wpm) + ", phrase:" + p

    def _send(self, wpm, phrase):
        if self.ser is None:
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
            if self.killcw == True:
                self.inprogress = False
                break

            if element == '.':
                self.ser.setDTR(True)
                time.sleep(dit)
                self.ser.setDTR(False)
                time.sleep(dit)
            elif element == '-':
                self.ser.setDTR(True)
                time.sleep(dah)
                self.ser.setDTR(False)
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

    cw = CwSerial(device)
    print(cw.send(wpm, phrase))
