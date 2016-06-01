#!/bin/bash

apt-get clean && apt-get update && apt-get install -y python-pip python-dev

pip install influxdb
pip install pyserial
pip install spidev
pip install py-opc
