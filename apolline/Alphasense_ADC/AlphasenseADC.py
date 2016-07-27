#!/usr/bin/env python
"""
Alphasense ADC Driver for Apolline
"""
import argparse
import serial
import time
from influxdb import InfluxDBClient
from influxdb import SeriesHelper

class ADCSensor:
    """
    ?  Alphasense ADC
    N  1281.1
    T  26.6
    V  400
    """
    def __init__(self,database='apolline'):
        self.dbname = database
        self.parser = argparse.ArgumentParser(description='Apolline agent for Alphasense ADC sensor')
        self.parser.add_argument('--host', type=str, required=False,
            default='apolline.lille.inria.fr', help='hostname of Apolline backend')
        self.parser.add_argument('--port', type=int, required=False,
            default=8086, help='port of Apolline backend')
        self.parser.add_argument('--device', type=str, required=False,
            default='/dev/ttyUSB0', help='serial device used to measure')
        self.parser.add_argument('--location', type=str, required=False,
            default='unknown', help='physical location of the sensor')
        self.parser.add_argument('--database', type=str, required=False,
            default='sandbox', help='remote database used to upload the measurements')
        self.parser.add_argument('--frequency', type=int, required=False,
            default=60, help='data retrieval frequency in seconds')
        self.parser.add_argument('--user', type=str, required=True,
            help='user login to upload data online')
        self.parser.add_argument('--password', type=str, required=True,
            help='user password to upload data online')

    def configure(self):
        args = self.parser.parse_args()
        self.location = args.location
        self.device = args.device
        self.frequency = args.frequency
        self.connection = InfluxDBClient(args.host, args.port, args.user, args.password, args.database)

    def run(self):
        self.configure()
        while 1:
            self.sense()
            time.sleep(self.frequency)

    def sense(self):
        class ADCHelper(SeriesHelper):
            class Meta:
                series_name = 'events.stats.{location}'
                fields = ['temperature','CO_1','CO_1V','CO_2','CO_2V','NO_1','NO_1V','NO_2','NO_2V','NO2_1','NO2_1V','NO2_2','NO2_2V']
                tags = ['location']
                client = self.connection
                autocommit = False
        try:
            ser=serial.Serial(self.device, 19200, timeout=123)
            line=ser.readline()
            ser.close()
            if not line: return
            line=line.replace("\r\n","")
            value=line.split(";")
            ADCHelper(location=self.location, temperature=value[1], CO_1=value[2], CO_1V=value[3], CO_2=value[4], CO_2V=value[5], NO_1=value[6], NO_1V=value[7], NO_2=value[8], NO_2V=value[9], NO2_1=value[10], NO2_1V=value[11], NO2_2=value[12], NO2_2V=value[13])
            ADCHelper.commit()
        except:
            print "Failed to read some values from sensor"



if __name__ == '__main__':
    sensor = ADCSensor()
    sensor.run()
