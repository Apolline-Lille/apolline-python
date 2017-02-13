# Documentation for the collection of data without Internet

> take NDIR CO2 as an example.

## Global View

The problem in the program is that it send directly the data to InfluxDB without checking the Internet connection. This take the risk of losing the data in the absence of Internet connection.

![schema avant](https://drive.google.com/uc?id=0B_jq0BJo4ikCRXFJODNtUVBrRXM)

The solution I'd suggest is to esatablish a `cache` at local repository. That means the program will first save the data locally and check the Internet connection. If the connection is established, the data will send to the database.

![schema apres](https://drive.google.com/uc?id=0B_jq0BJo4ikCS0VuTDNVS1M4eXM)

Raspberry Pi 2 will save the data in a text file using `line protocol` of InfluxDB. There is no predefined interface to check the Internet connection. So a workaround here is make a homepage `HTTP Get` request and verify the response code : 200 for success and other codes for failure.

The function *run()* uses *sense_into_file()* and *write_from()* instead of *sense()*

## Simple calculation of storage

1 day = 86 400 seconds

If we use the default frequency (10 seconds), the sensor will collect 8640 lines of data within a day.

A line of data = 90 Bytes
The data within a day = 777 600 Bytes = 759.4 KB

## function reference

> sense_into_file(self)

This function collect the data of sensor, then call the method *write_into_file()*.

> write_from(self, directory_path, db=”apolline”)

This function send the data to Influx DB after have verified the Internet connection. It will also count the line number for reduce the overload of Internet.

> connection_established(self)

This function make a GET request to verify the Internet connection.

> name_file(cardinal, date=datetime.datetime.now().strftime("%Y%m%d")

This function name the file according to the date and the cardinality in thr form of YYYYmmddN00. The default value is the value of the system.

Example : 20170125N01.txt

> line_number_of_file(file)

This function calculate the line number of a given file.

> write_into_file(directory_path)

This function will control the procedure of writing into file. If no file for today it will create one; If file for today exists and it's line number is less than 4000, we continue write to this file; If the file's line number more than 4000 we create a new file for this day.