from pprint import pprint

from olive.devices.protocols import SerialDevice

sd = SerialDevice()
pprint(sd.discover())
