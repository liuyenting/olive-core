from pprint import pprint

from olive.devices.protocols.serial import SerialDevice

sd = SerialDevice()
pprint(sd.discover())
