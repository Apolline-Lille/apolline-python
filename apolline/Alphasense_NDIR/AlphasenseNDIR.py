"""
Alphasense NDIR Driver for Apolline
"""
import argparse
import serial
import time
from influxdb import InfluxDBClient
from influxdb import SeriesHelper

# myclient.create_database(dbname)
# myclient.create_retention_policy('awesome_policy', '3d', 3, default=True)

class NDIRSensor:
    """
    ?  Alphasense NDIR
    N  1281.1
    T  26.6
    V  400
    """
    def __init__(self,database='apolline'):
        self.dbname = database
        self.parser = argparse.ArgumentParser(description='Apolline agent for Alphasense NDIR sensor')
        self.parser.add_argument('--host', type=str, required=False,
            default='apolline.lille.inria.fr', help='hostname of Apolline backend')#192.168.99.100
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
        class NDIRHelper(SeriesHelper):
            class Meta:
                series_name = 'events.stats.{location}'
                fields = ['CO2', 'temperature', 'voltage']
                tags = ['location']
                client = self.connection
                autocommit = False

        try:
            ser=serial.Serial(self.device, 19200, timeout=67)
            ser.write("N\r")
            carbon=float(ser.readline())
            ser.write("T\r")
            temp=float(ser.readline())
            ser.write("V\r")
            volt=float(ser.readline())
            ser.close()
            NDIRHelper(location=self.location, CO2=carbon, temperature=temp, voltage=volt)
            NDIRHelper.commit()
        except:
            print "Failed to read some values from sensor"



if __name__ == '__main__':
    sensor = NDIRSensor()
    sensor.run()
