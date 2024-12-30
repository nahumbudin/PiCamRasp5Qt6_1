#!/usr/bin/env python
import struct
import smbus
import sys
import time
# import RPi.GPIO as GPIO
import gpiod

# Global settings
# GPIO26 is for x728 V2.1/V2.2/V2.3, GPIO13 is for X728 v2.0/v1.2/v1.3
GPIO_POWER_MANAGEMENT = 26
# Indicates when the external power source is connected (Low) or disconnected (High)
GPIO_INPUT_POWER = 6
# Buzzer control
GPIO_BUZZER_CONTROL = 20
# I2C interface address
I2C_ADDR = 0x36


class BatX728:
    """
        This class provides an interface to the Geekworm X728 UPS power management board.
        https://geekworm.com/products/raspberry-pi-x728-max-5-1v-8a-18650-ups-power-management-board
        https://wiki.geekworm.com/X728.
        It is based on the board library: https://github.com/geekworm-com/x728

        Author: Nahum Budin
        Date: 2023-08-05
        Version: 1.0.0
    """
    def __init__(self):

        """
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(GPIO_POWER_MANAGEMENT, GPIO.OUT)
        GPIO.setup(GPIO_INPUT_POWER, GPIO.IN)
        GPIO.setup(GPIO_BUZZER_CONTROL, GPIO.OUT)
        GPIO.setwarnings(False)

        self.bus = smbus.SMBus(1)  # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
"""

    def read_voltage(self):
        """ Reads the batteries voltage """
        address = I2C_ADDR
        read = self.bus.read_word_data(address, 2)
        swapped = struct.unpack("<H", struct.pack(">H", read))[0]
        voltage = swapped * 1.25 / 1000 / 16
        return voltage

    def read_capacity(self):
        """ Reads the batteries remaining capacity """
        address = I2C_ADDR
        read = self.bus.read_word_data(address, 4)
        swapped = struct.unpack("<H", struct.pack(">H", read))[0]
        capacity = swapped / 256
        return capacity

    def get_input_power_status(self):
        return GPIO.input(GPIO_INPUT_POWER)

    def set_buzzer_on(self):
        GPIO.output(GPIO_BUZZER_CONTROL, 1)

    def set_buzzer_off(self):
        GPIO.output(GPIO_BUZZER_CONTROL, 0)


if __name__ == "__main__":
    batMon = BatX728()
    while True:
        print("******************")
        print("Voltage:%5.2fV" % batMon.read_voltage())
        print("Battery:%5i%%" % batMon.read_capacity())
        time.sleep(2)

# if readCapacity(bus) == 100:
#        print ("Battery FULL")
# if readCapacity(bus) < 20:
#        print ("Battery Low")

# Set battery low voltage to shut down, you can modify the 3.00 to other value
# if readVoltage(bus) < 3.00:
#       print ("Battery LOW!!!")
#        print ("Shutdown in 10 seconds")
#        time.sleep(10)
#       GPIO.output(GPIO_PORT, GPIO.HIGH)
#        time.sleep(3)
#       GPIO.output(GPIO_PORT, GPIO.LOW)
