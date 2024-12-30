#!/usr/bin/env python3
# This python script is only suitable for UPS Shield X1200, X1201 and X1202

import struct
import smbus
import gpiod
import time
from subprocess import call

# I2C interface address
I2C_ADDR = 0x36
# Charging ON bit
PLD_PIN = 6


class BatX1201:
    """
            This class provides an interface to the Geekworm X1201 UPS power management board.
            https://geekworm.com/products/x1201
            https://wiki.geekworm.com/X1201
            It is based on the board library: https://github.com/suptronics/x120x.git

            Author: Nahum Budin
            Date: 2024-02-10
            Version: 1.0.0
        """

    def __init__(self):
        self.bus = smbus.SMBus(1)
        self.address = I2C_ADDR

        self.chip = gpiod.Chip('gpiochip4')
        self.pld_line = None

    def read_bat_voltage(self):
        read = self.bus.read_word_data(self.address, 2)
        swapped = struct.unpack("<H", struct.pack(">H", read))[0]
        voltage = swapped * 1.25 / 1000 / 16
        return voltage

    def read_bat_capacity(self):
        read = self.bus.read_word_data(self.address, 4)
        swapped = struct.unpack("<H", struct.pack(">H", read))[0]
        capacity = swapped / 256
        return capacity

    def get_power_connection_state(self):
        try:
            self.pld_line = self.chip.get_line(PLD_PIN)
            self.pld_line.request(consumer="PLD", type=gpiod.LINE_REQ_DIR_IN)
            pld_state = self.pld_line.get_value()
            return pld_state
        finally:
            self.pld_line.release()


if __name__ == "__main__":

    import time

    batx1201 = BatX1201()

    while True:
        print("Voltage:%5.2fV" % batx1201.read_bat_voltage())

        print("Battery:%5i%%" % batx1201.read_bat_capacity())

        if batx1201.get_power_connection_state() == 1:
            print("Power connected")
        else:
            print("Power disconnected")

        time.sleep(1)

