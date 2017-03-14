#!/bin/bash

# install the required modules.
# apt-get clean && apt-get update && apt-get install -y python-pip python-dev

# pip install influxdb
# pip install pyserial
# pip install spidev
# pip install py-opc

# Let user enter the parameter to customize(location, frequency etc.)
while getopts ":s:u:p:d:l:f:" opt; do
    case $opt in
        s)
            sensor=$OPTARG
            ;;
        u)
            user=$OPTARG
            ;;
        p)
            passwd=$OPTARG
            ;;
        d)
            database=$OPTARG
            ;;
        l) 
            location=$OPTARG
            ;;
        f)
            frequency=$OPTARG
            # echo "-f was triggered" >&2
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            exit 1
            ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            exit 1
            ;;
    esac
done

# Verify if the sensor is valid.
if [ "$sensor" == "ADC" ]; then
    run_script="nohup python $PWD/apolline/Alphasense_ADC/AlphasenseADC.py --user $user --password $passwd --database $database --location $location --frequency $frequency &"
    echo "The sensor is $sensor"
elif [ "$sensor" == "NDIR" ]; then
    run_script="nohup python $PWD/apolline/Alphasense_NDIR/AlphasenseNDIR.py --user $user --password $passwd --database $database --location $location --frequency $frequency &"
    echo "The sensor is $sensor"
elif [ "$sensor" == "OPC-N2" ]; then
    run_script="nohup python $PWD/apolline/Alphasense_OPC-N2/AlphasenseOPC.py --user $user --password $passwd --database $database --location $location --frequency $frequency &"
    echo "The sensor is $sensor"
else
    run_script=""
    echo "Not a valid sensor: $sensor"
fi

# Once it is a valid sensor
# rewrite the rc.local each time we run this script.
echo "Writing to rc.local"
(
cat << EOF 

# !/bin/sh -e

# rc.local

# This script is executed at the end of each multiuser runlevel.
# Make sure that the script will "exit 0" on success or any other
# value on error.

# in order to enable or disable this script just change the execution
# bits.

# By default this script does nothing.

# You can find log file at /tmp/rc.local.log if there are any problem.
exec 2> /tmp/rc.local.log
exec 1>&2
set -e

$run_script
exit 0
EOF
) > /etc/rc.local

echo "Writting to rc.local done, you can reboot the Raspberry."