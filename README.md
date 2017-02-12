# Apolline Python Agent for Raspberry

## Instructions

You first need to clone the repository:

```bash
git clone https://github.com/Spirals-Team/apolline-python.git
```

Then, run the setup script with the parameters:

| Parameters | Descriptions                                                                               |
|-----------:|:-------------------------------------------------------------------------------------------|
| -s         | It stands for the using sensor. Three types of sensor supported : ADC, NDIR, OPC-N2        |
| -u         | It stands for the user to login the InfluxDB                                               |
| -p         | It stands for the password for InfluxDB                                                    |
| -d         | It stands for the database's name                                                          |
| -l         | It stands for the location of the Raspberry pi and which will be used as the name of table |
| -f         | It stands for the frequency of the sensor                                                  |

* Let's take NDIR for example :

```bash
cd apolline-python
sudo ./setup.sh -s NDIR -u USER -p PASSWD -d DB_NAME -l LOC -f 10
```

Then you should restart the Raspberry Pi.

Or if you want to run the script manually, run the apolline scripts as follow:

```bash
./ndir.sh --user USER --password PASSWD --database DB_NAME --location LOC --frequency 10
./adc.sh --user USER --password PASSWD --database DB_NAME --location LOC --frequency 10
```
