import argparse
import serial
import time
from os.path import exists

class CwSerial:
    rig_file = ""
    wpm_to_ms = 500

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

    def __init__(self, rigfile):
        self.rig_file = rigfile
        #print("rig_file:" + self.rig_file)

    def isDevice(self):
        if exists(self.rig_file):
            return True
        else:
            raise Exception("Device file not found: " + self.rig_file)


    def send(self, w, phrase):
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

        dit = round(self.wpm_to_ms / wpm * 3 / 1000, 4)
        dah = round(self.wpm_to_ms / wpm * 7 / 1000, 4)

        cwseq = ''
        
        for element in p:
            if element != ' ':
                if element in self.cw:
                    cwseq += self.cw[element] + '1'
            else:
                cwseq += '3'

        ser = serial.Serial(self.rig_file)
        ser.setDTR(False)
        ser.setRTS(False)
        time.sleep(dit)

        for element in cwseq:
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
                ser.setDTR(False)
                space = dit * int(element)
                time.sleep(space)


        return "wpm: " + str(wpm) + ", phrase:" + p

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