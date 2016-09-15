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
    """
    def __init__(self,database='apolline'):
        self.dbname = database
        self.parser = argparse.ArgumentParser(description='Apolline agent for Alphasense ADC sensor')
        self.parser.add_argument('--host', type=str, required=False,
            default='apolline.lille.inria.fr', help='hostname of Apolline backend')
        self.parser.add_argument('--port', type=int, required=False,
            default=8086, help='port of Apolline backend')
        self.parser.add_argument('--device', type=str, required=False,
            default='/dev/ttyUSB1', help='serial device used to measure')
        self.parser.add_argument('--location', type=str, required=False,
            default='unknown', help='physical location of the sensor')
        self.parser.add_argument('--database', type=str, required=False,
            default='sandbox', help='remote database used to upload the measurements')
        self.parser.add_argument('--frequency', type=float, required=False,
            default=0.5, help='data retrieval frequency in seconds')
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
        try:
            self.configure()
            ser=serial.Serial(self.device, 9600, timeout=123)
            while 1:
                self.sense(ser)
                time.sleep(self.frequency)
            ser.close()

    def sense(self,ser):
        class ADCHelper(SeriesHelper):
            class Meta:
                series_name = 'events.stats.{location}'
                fields = ['temperature','Voie_1','Voie_1V','Voie_2','Voie_2V','Voie_3','Voie_3V','Voie_4','Voie_4V','Voie_5','Voie_5V','Voie_6','Voie_6V']
                tags = ['location']
                client = self.connection
                autocommit = False
        try:
            line = ser.readline()
            if not line: return
            line = line.replace("\r\n","")
            value = line.split(";")
            if len(value) == 15:
                ADCHelper(location=self.location, temperature=value[2], Voie_1=value[3], Voie_1V=value[4], Voie_2=value[5], Voie_2V=value[6], Voie_3=value[7], Voie_3V=value[8], Voie_4=value[9], Voie_4V=value[10], Voie_1=value[11], Voie_1V=value[12], Voie_2=value[13], Voie_2V=value[14])
                ADCHelper.commit()
        except:
            print "Failed to read metrics from ADC sensor on "+self.device


if __name__ == '__main__':
    sensor = ADCSensor()
    sensor.run()
