import base
import time
import serial
import re
from multiprocessing.queues import Empty

class Uart(base.Abstract):
    ser = None

    def __init__(self):
        pass

    def connect(self, glade, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS):

        device = glade.get_object('serial_device_entry').get_text()
        baudrate = glade.get_object('serial_baudrate_entry').get_text() if not '' else 115200

        # Configure the serial connections (the parameters differs on the device you are connecting to)
        self.ser = serial.Serial(
            port = device,
            baudrate = baudrate,
            parity = parity,
            stopbits = stopbits,
            bytesize = bytesize
        )

    def isOpen(self):
        return  self.ser and hasattr(self.ser, 'isOpen') and self.ser.isOpen()

    def close(self):
        if self.isOpen():
            self.ser.close()

    def send(self, input):
        if self.isOpen():
            for c in input + '\x00':
                self.ser.write(c)

    def listen(self, conn, queue):
        while self.isOpen():
            try:
                input = queue.get_nowait()
                if isinstance(input, basestring):
                    self.ser.write(input + '\00')

            except Empty:
                pass

            line = self.ser.readline()

            if line != '':
                print ">>" + line

                conn.send('>> %s' % (re.sub(r'^\r', r'', line)))
