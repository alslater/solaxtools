import daemon
import time
from pid import PidFile
from .modbus import get_values
from influxdb import InfluxDBClient
from configparser import ConfigParser
from os import getenv, path
from time import sleep
from datetime import datetime


config_file = path.join(getenv('HOME'), '.config/solaxtools.conf')

config = ConfigParser()
config.read(config_file)

_series = "solaxdata"

_influx = InfluxDBClient(
    host=config.get('influxdb', 'host', fallback="localhost"),
    port=config.getint('influxdb', 'port', fallback=8086),
    username=config.get('influxdb', 'user', fallback=""),
    password=config.get('influxdb', 'password', fallback=""),
    database=config.get('influxdb', 'database', fallback="solax"),
)

def write_series(values):
    if not config.getboolean('daemon', 'enabled', fallback=False):
        print(values)

    _influx.write_points([
        {
            "measurement": _series,
            "tags": {
                "solax": "yes"
            },
            "time": datetime.now().isoformat(),
            "fields": values
        }
    ])

def run():
    if config.getboolean('daemon', 'enabled', fallback=False):
        print('Starting daemon')
        pid_file = PidFile('/tmp/solax2influx.pid')
        with daemon.DaemonContext(pidfile=pid_file):
            solax_to_influxdb()
    else:
        solax_to_influxdb()

def solax_to_influxdb():
    while True:
        sv = get_values()

        if sv is not None:
            pvpower = sv['pvpower']
            feedin = sv['feedin']
            battery_power = sv['battery_power']

            sv['pvpower'] = sv['pvpower'] / 1000
            sv['feedin'] = sv['feedin'] / 1000
            sv['battery_power'] = sv['battery_power'] / 1000
            usage = (pvpower + -feedin - battery_power) / 1000
            sv['usage'] = usage

            write_series(sv)

        sleep(30)
