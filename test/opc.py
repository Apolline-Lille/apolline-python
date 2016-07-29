#!/usr/bin/env python
"""
Test for the Alphasense OPC-N2
"""
import spidev
import time

spi = spidev.SpiDev(0, 0)
spi.open(0, 0)
spi.mode = 1
spi.max_speed_hz = 500000

info_string = []
spi.xfer([0x3F])
time.sleep(9e-3)

for i in range(60):
    resp = spi.xfer([0x00])
    info_string.append(chr(resp[0]))

''.join(info_string)
