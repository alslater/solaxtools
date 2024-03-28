from configparser import ConfigParser
from os import path, getenv
import requests

config_file = path.join(getenv('HOME'), '.config/solaxtools.conf')

config = ConfigParser()
config.read(config_file)

_api_host=config.get('api', 'host', fallback="localhost")
_api_serial=config.get('api', 'serial', fallback="localhost")

def _decode_from_uint16(value):
    return ((value ^ 65535) + 1) * -1 if value & 32768 else value


def get_values():
    try:
        params= {
            "optType": "ReadRealTimeData",
            "pwd": _api_serial
        }

        r = requests.post(f"http://{_api_host}", data=params, timeout=(2, 2))
        r.raise_for_status()

        res = r.json()

        data = res['Data']

        return {
            'pvpower': float(data[8] + data[9]),
            'feedin': float(_decode_from_uint16(data[32])),
            'soc': float(data[18]),
            'battery_temp': data[17],
            'inverter_temp': data[39],
            'battery_power': float(_decode_from_uint16(data[16])),
        }
    except Exception:
        return None