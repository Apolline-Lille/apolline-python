# Apolline Python Agent for Raspberry

## Instructions
You first need to clone the repository:
```bash
git clone https://github.com/Apolline-Lille/apolline-python.git
```

Then, you run the `setup.sh` script with the following parameters:

| Parameters | Descriptions                                                         |
|-----------:|:---------------------------------------------------------------------|
| `-s`       | The sensor to setup : `ADC`, `NDIR` or `OPC-N2` (not supported yet)  |
| `-u`       | The user to login in the InfluxDB database                           |
| `-p`       | The password to authenticate in the InfluxDB database                |
| `-d`       | The name of the database volume to be used (`apolline` or `sandbox`) |
| `-l`       | The physical location of the sensor                                  |
| `-f`       | The sampling frequency of the sensor (in seconds)                    |


## Examples
### Automated execution
To sample every 10 seconds with the NDIR sensor, you can execute the following command:
```bash
cd apolline-python/
sudo ./setup.sh -s NDIR -u [USER] -p [PASSWD] -d sandbox -l [LOCATION] -f 10
```

Then, you should restart the Raspberry Pi to apply the changes.

### Manual execution
If you rather prefer to run the script manually, run the apolline scripts as follows:
```bash
cd apolline-python/
./ndir.sh --user [USER] --password [PASSWD] --database sandbox --location [LOCATION] --frequency 10
./adc.sh --user [USER] --password [PASSWD] --database sandbox --location [LOCATION] --frequency 10
```
