#!/usr/bin/env python
"""
Alphasense NDIR Driver for Apolline
"""
import argparse
import serial
import os
import time
import requests
import datetime
from influxdb import InfluxDBClient
from influxdb import SeriesHelper

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
        self.host = args.host
        self.port = args.port
        self.location = args.location
        self.device = args.device
        self.frequency = args.frequency
        self.connection = InfluxDBClient(args.host, args.port, args.user, args.password, args.database)

    def run(self):
        self.configure()
        while 1:
            self.sense_into_file()
            self.write_from("data")
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
            
    def sense_into_file(self):
        # (Described at documentation that the max number for each insert query is 5000)
        # if no file exist in the directory, create a new file 
        # if it has files check the first file which has less than 5000 points.
        # add data into files
        # if the file depass 5000, turn to next file.
        # no file is less than 5000, create a new file.
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
            self.write_into_file("data", carbon, temp, volt)
        except:
            print "Failed to read some values from sensor"

    # There is no build-in ping functionality to check the status of DB's connection in the library InfluxDBClient.
    # In consequence I'll use the get request to verify if there is a connection.
    def connection_established(self):
        try:
            response = requests.get("http://{host}:{port}/query?pretty=true".format(host = self.host, port = self.port)
                                    , params="q=show DATABASES")
            return True
        except requests.exceptions.ConnectionError:
            print "Connection to influxDB failed, Is the server running ?"
            return False
    
    # File must match InfluxDB line protocol.
    # FILE MUST ENDED WITH LINUX LF END LINE.
    def write_from(self, directory_path, db="apolline"):
        files = [ x for x in os.listdir(directory_path)] # list all file.
        files.sort()
        for datafile in files:
            line_number = self.line_number_of_file(directory_path + "/" + datafile)
            if self.connection_established() and line_number >= 4000:
                try:
                    # write the data to the InfluxDB.
                    response = requests.post('http://{host}:{port}/write?db={db_name}'.format(host = self.host, port = self.port, db_name = db),
                                        data=(file(directory_path + "/" + datafile, "rb")).read())
                    os.remove(directory_path + "/" + datafile); # This file has been uploaded, delete it.
                    print "Upload and remove local file : " + datafile + "succeed..."
                except requests.exceptions.ConnectionError:
                    print "Write the data failed, please check response.text for more information"
            else:
                print "Time : {time} ".format(time = datetime.datetime.now())

    def file_exists(self, file_path):
        if not file_path:
            return False
        elif not os.path.isfile(file_path):
            return False
        else:
            return True
        
    def name_file(self, cardinal, date=datetime.datetime.now().strftime("%Y%m%d")):
    # Assume that for one day it will collect less than 100 * 5000 lines of data.
        if cardinal < 10:
            return date + "N0" + str(cardinal) + ".txt"
        else:
            return date + "N" + str(cardinal) + ".txt"

    def line_number_of_file(self, file):
        count = -1
        with open(file, "r") as f:
            for count, line in enumerate(f):
                pass
            count += 1
        return count

    def write_into_file(self, directory_path, carbon, temp, volt):
#       check all the file name
        files = [ x for x in os.listdir(directory_path)]
        files.sort()
        date_has_file = False
        cardinal = 1
        i = 0
#       compare with the date
        
        while i < len(files):
            if (files[i][:8] == datetime.datetime.now().strftime("%Y%m%d")):
                date_has_file = True
                file = files[i]
                cardinal = int(files[i][-6: -4]) + 1
            i += 1
#       if exist that date
        if date_has_file:
#           if lines numbers < 5000
            if self.line_number_of_file(directory_path + "/" + file) < 4000 :
#               write into file
                with open(directory_path + "/" + file,"a") as f:
                    f.write("\n{measurement},{tags} {fields} {timestamp}".format(measurement = "events.stats.{location}".format(location=self.location), 
                                                                        tags = "location=" + self.location, 
                                                                        fields = "CO2=" + str(carbon) + ",temperature=" + str(temp) + ",voltage=" + str(volt),
                                                                        timestamp = "".join(str("%.9f" %time.time()).split(".")) ))
#           else create new file && write in this new file.
            else:
                with open(directory_path + "/" + self.name_file(cardinal,file[:8]), "a") as f:
                    f.write("{measurement},{tags} {fields} {timestamp}".format(measurement = "events.stats.{location}".format(location=self.location), 
                                                                        tags = "location=" + self.location, 
                                                                        fields = "CO2=" + str(carbon) + ",temperature=" + str(temp) + ",voltage=" + str(volt),
                                                                        timestamp = "".join(str("%.9f" %time.time()).split(".")) ))
#       else the same 
        else:
            with open(directory_path + "/" + self.name_file(cardinal), "w") as f:
                f.write("{measurement},{tags} {fields} {timestamp}".format(measurement = "events.stats.{location}".format(location=self.location), 
                                                                            tags = "location=" + self.location, 
                                                                            fields = "CO2=" + str(carbon) + ",temperature=" + str(temp) + ",voltage=" + str(volt),
                                                                            timestamp = "".join(str("%.9f" %time.time()).split(".")) ))




    
if __name__ == '__main__':
    sensor = NDIRSensor()
    sensor.run()
    
