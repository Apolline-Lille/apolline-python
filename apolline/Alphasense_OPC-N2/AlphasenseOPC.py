#!/usr/bin/env python
"""
Alphasense OPC-N2 Driver for Apolline
"""
import argparse
import spidev
import time
from opc import OPCN2
from influxdb import InfluxDBClient
from influxdb import SeriesHelper

class OPCSensor:
    """
    Alphasense OPC-N2 sensor
    """
    SPI_MODE     = 1
    SPI_CLK      = 500000
    SPI_MSBFIRST = True

    def __init__(self,database='apolline'):
        self.dbname = database
        self.parser = argparse.ArgumentParser(description='Apolline agent for Alphasense OPC-N2 sensor')
        self.parser.add_argument('--host', type=str, required=False,
            default='apolline.lille.inria.fr', help='hostname of Apolline backend')
        self.parser.add_argument('--port', type=int, required=False,
            default=8086, help='port of Apolline backend')
        self.parser.add_argument('--location', type=str, required=False,
            default='unknown', help='physical location of the sensor')
        self.parser.add_argument('--frequency', type=int, required=False,
            default=60, help='data retrieval frequency in seconds')
        self.parser.add_argument('--user', type=str, required=True,
            help='user login to upload data online')
        self.parser.add_argument('--password', type=str, required=True,
            help='user password to upload data online')
        self.parser.add_argument('--device', type=int, required=False,
            default=0, help='device id used to measure')
        self.parser.add_argument('--bus', type=int, required=False,
            default=0, help='bus id used to measure')

    def configure(self):
        args = self.parser.parse_args()
        self.location = args.location
        self.device = args.device
        self.frequency = args.frequency
        self.connection = InfluxDBClient(args.host, args.port, args.user, args.password, self.dbname)
        spi = spidev.SpiDev()
        spi.open(args.bus, args.device)
        spi.mode         = OPCSensor.SPI_MODE
        spi.max_speed_hz = OPCSensor.SPI_CLK
        spi.lsbfirst     = not OPCSensor.SPI_MSBFIRST
        self.alpha = OPCN2(spi)

    def run(self):
        self.configure()
        try:
            self.alpha.on()
            while 1:
                self.sense()
                time.sleep(self.frequency)
        finally:
            self.alpha.off()

    def sense(self):
        class OPCHelper(SeriesHelper):
            class Meta:
                series_name = 'events.stats.{location}'
                fields = ['temperature', 'pressure', 'PM1', 'PM2_5', 'PM10']
                tags = ['location']
                client = self.connection
                autocommit = True

        try:
            hist = self.alpha.read_histogram()
            OPCHelper(location=self.location, 
                      temperature = int(hist['Temperature']),
                      pressure    = float(hist['Pressure']),
                      PM1         = float(hist['PM1']),
                      PM2_5       = float(hist['PM2.5']),
                      PM10        = float(hist['PM10']))
        except:
            print "Failed to read some values from sensor"


if __name__ == '__main__':
    sensor = OPCSensor()
    sensor.run()
