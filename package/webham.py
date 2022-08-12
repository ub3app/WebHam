import Hamlib
import threading
import serial
import time
from os.path import exists
import sys
import logging
from logging import StreamHandler


class Webham:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)

    initialized = False

    rig = None
    rigModel = None
    rigDevice = None
    rigDataBits = None
    rigStopBits = None
    rigRate = None
    rigParity = None
    rigWriteDelay = None

    stop = False

    rig_skip_polling_flag = False
    rig_mode = None
    rig_width = 0
    rig_freq = 0

    def __init__(self):
        t_init = threading.Thread(target=self.__init)
        t_init.start()

        t_polling = threading.Thread(target=self.__rigPolling)
        t_polling.start()

    def __init(self):
        while not self.stop:
            if self.rigDevice is None:
                self.initialized = False
                self.logger.debug('rigDevice not set')
            elif self.rigModel is None:
                self.initialized = False
                self.logger.debug('rigModel not set')
            elif not exists(self.rigDevice):
                self.initialized = False
                self.logger.debug('rigDevice not exists: ' + self.rigDevice)
            else:
                if not self.initialized:
                    self.logger.debug('Start init')
                    if self.rig is not None:
                        self.rig.close()
                        self.rig = None

                    self.logger.debug('Try to search model: ' + self.rigModel)
                    model = getattr(Hamlib, self.rigModel)
                    self.logger.debug('Model id: ' + str(model))

                    Hamlib.rig_set_debug(Hamlib.RIG_DEBUG_NONE)

                    self.rig = Hamlib.Rig(model)
                    if self.rig.this is not None:
                        self.logger.debug('Device: %s' % self.rigDevice)
                        self.rig.state.rigport.pathname = self.rigDevice

                        if self.rigWriteDelay is not None:
                            # Doesn't work on some rig, get: -8, Protocol error
                            # self.logger.debug('Write delay: %i' % self.rigWriteDelay)
                            # self.rig.state.rigport.write_delay = self.rigWriteDelay
                            pass

                        if self.rigRate is not None:
                            self.logger.debug('Rate: %i' % self.rigRate)
                            self.rig.state.rigport.parm.serial.rate = self.rigRate

                        if self.rigDataBits is not None:
                            self.logger.debug('Data bits: %i' % self.rigDataBits)
                            self.rig.state.rigport.parm.serial.data_bits = self.rigDataBits

                        if self.rigStopBits is not None:
                            self.logger.debug('Stop bits: %i' % self.rigStopBits)
                            self.rig.state.rigport.parm.serial.stop_bits = self.rigStopBits

                        if self.rigParity is not None:
                            parity = getattr(Hamlib, self.rigParity)
                            self.logger.debug('Parity: %i (%s)' % (parity, self.rigParity))
                            self.rig.state.rigport.parm.serial.parity = parity

                        self.rig.open()
                        ser = serial.Serial(self.rigDevice)
                        ser.setDTR(False)
                        if self.rig.error_status == Hamlib.RIG_OK:
                            self.initialized = True
                            self.logger.debug('Successful initialized')
                        else:
                            self.logger.debug('Unsuccessful initialized')
                            self.logger.debug('error_status: ' +
                                              str(self.rig.error_status) +
                                              ', error_message: ' + Hamlib.rigerror(self.rig.error_status))
                    else:
                        self.logger.debug('Model not found')
                else:
                    self.logger.debug('Already initialized')
            self.logger.debug('Initializing sleep 5 sec...')
            time.sleep(5)

    def __rigPolling(self):
        while not self.stop:
            if self.initialized:
                if not self.rig_skip_polling_flag:
                    self.logger.debug('Rig pooling...')
                    (mode, self.rig_width) = self.rig.get_mode()
                    self.rig_mode = Hamlib.rig_strrmode(mode)
                    self.rig_freq = self.rig.get_freq()

                    if self.rig.error_status != Hamlib.RIG_OK:
                        self.initialized = False
                        self.logger.debug('Error pooing rig, reset to initializing')
                        self.logger.debug(
                            'error_status: ' + str(self.rig.error_status) + ', error_message: ' + Hamlib.rigerror(
                                self.rig.error_status))
                    else:
                        self.logger.debug('Successful pooling, Mode: %s, Width: %s, Freq: %s' % (
                            self.rig_mode,
                            str(self.rig_width),
                            str(self.rig_freq)))
                else:
                    self.logger.debug('Skip pooling by flag')
            self.logger.debug('Rig pooling sleep 3 sec...')
            time.sleep(3)

    def close(self):
        self.logger.debug('Stopping threads...')
        if self.rig is not None:
            self.rig.close()
        self.stop = True

    def getStatus(self):
        return self.initialized

    def setRig(self,
               rigModel, rigDevice,
               rigDataBits=None, rigStopBits=None, rigRate=None, rigParity=None,
               rigWriteDelay=None):

        if rigModel is None:
            raise ValueError("rigModel can not be empty!")

        if rigDevice is None:
            raise ValueError("rigDevice can not be empty!")

        self.rigModel = 'RIG_MODEL_' + rigModel
        self.rigDevice = rigDevice

        if rigDataBits is not None:
            if isinstance(rigDataBits, str):
                self.rigDataBits = int(rigDataBits)

        if rigStopBits is not None:
            if isinstance(rigStopBits, str):
                self.rigStopBits = int(rigStopBits)

        if rigRate is not None:
            if isinstance(rigRate, str):
                self.rigRate = int(rigRate)

        if rigParity is not None:
            self.rigParity = 'RIG_PARITY_' + rigParity

        if rigWriteDelay is not None:
            if isinstance(rigWriteDelay, str):
                self.rigWriteDelay = int(rigWriteDelay)

        self.initialized = False

    def getRigs(self):
        result = []
        for item in dir(Hamlib):
            if item.startswith("RIG_MODEL_"):
                item = item.replace('RIG_MODEL_', '')
                result.append(item)
        return result

    def getParitys(self):
        result = []
        for item in dir(Hamlib):
            if item.startswith("RIG_PARITY_"):
                item = item.replace('RIG_PARITY_', '')
                result.append(item)
        return result

    def setPtt(self, ptt):
        self.__checkInitialized()
        if ptt not in [0, 1]:
            raise ValueError("PTT must be 0 or 1")

        if ptt == 1:
            self.rig_skip_polling_flag = True
            self.rig.set_ptt(Hamlib.RIG_VFO_CURR, 1)
            if self.rig.error_status != Hamlib.RIG_OK:
                self.rig_skip_polling_flag = False
                self.logger.debug("Error to set TX")
                self.logger.debug(
                    'error_status: ' + str(self.rig.error_status) + ', error_message: ' + Hamlib.rigerror(
                        self.rig.error_status))
        else:
            self.rig_skip_polling_flag = False
            self.rig.set_ptt(Hamlib.RIG_VFO_CURR, 0)
            if self.rig.error_status != Hamlib.RIG_OK:
                self.logger.debug("Error to set RX")
                self.logger.debug(
                    'error_status: ' + str(self.rig.error_status) + ', error_message: ' + Hamlib.rigerror(
                        self.rig.error_status))
        return ptt

    def getPtt(self):
        self.__checkInitialized()
        vfo = self.rig.get_vfo()
        return self.rig.get_ptt(vfo)

    def __checkInitialized(self):
        if not self.initialized:
            raise Exception("Not initialized")

    def getFreq(self):
        self.__checkInitialized()
        return self.rig_freq

    def getMode(self):
        self.__checkInitialized()
        return self.rig_mode


class RigError(Exception):
    def __init__(self, rig=None):
        super(RigError, self).__init__()
        self.status = rig.error_status
        self.message = Hamlib.rigerror(self.status) if rig is not None else "Model not found"

    def __str__(self):
        args = (self.__class__.__name__,
                self.status,
                self.message)
        return "{0} ({1}): {2}".format(*args)
