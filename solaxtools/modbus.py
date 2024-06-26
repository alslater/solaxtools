from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils
import signal
from configparser import ConfigParser
from os import path, getenv

config_file = path.join(getenv('HOME'), '.config/solaxtools.conf')

config = ConfigParser()
config.read(config_file)

_mb_host=config.get('modbus', 'host', fallback="localhost")

mb_client = ModbusClient(host=_mb_host, port=502, unit_id=1, auto_open=True, timeout=30)

_solax_registers = {
    "inverter_temp": 0x08,
    "pvpower": 0x0A,
    "battery_capacity": 0x1C,
    "battery_temp": 0x18,
    "battery_power": 0x16,
    "feedin_power": 0x46,
}


# Something seems to put the solax wifi dongle into a bad mood and it stops replying
# causing receive errors.  I am just wondering if interrupting a call does that.
# hence the disable_sigint decorator to stop me doing that
def disable_sigint(func):
    def wrapper(*args, **kwargs):
        # Ignore SIGINT signal
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        try:
            # Call the function
            return func(*args, **kwargs)
        finally:
            # Restore default SIGINT behavior after the function call
            signal.signal(signal.SIGINT, signal.default_int_handler)
    return wrapper


@disable_sigint
def get_values():
    if regs:= mb_client.read_input_registers(_solax_registers['pvpower'], 2):
        pvpower = sum(regs)
    else:
        pvpower = 0

    if regs:= mb_client.read_input_registers(_solax_registers['feedin_power'], 2):
        # Signed int, negative is inbound from the grid, positive is outbound to the grid
        feedin = utils.get_list_2comp(regs, 16)[0]
    else:
        feedin = 0

    if regs := mb_client.read_input_registers(_solax_registers['battery_capacity'], 1):
        soc = regs[0]
    else:
        soc = 0

    if regs := mb_client.read_input_registers(_solax_registers['battery_temp'], 1):
        battery_temp = regs[0]
    else:
        battery_temp = 0

    if regs := mb_client.read_input_registers(_solax_registers['inverter_temp'], 1):
        inverter_temp = regs[0]
    else:
        inverter_temp = 0

    if regs := mb_client.read_input_registers(_solax_registers["battery_power"], 1):
        # Signed int, negative battery discharging, positive battery charging
        battery_power = utils.get_list_2comp(regs, 16)[0]
    else:
        battery_power = 0

    if pvpower == 0 and feedin == 0 and soc == 0 and battery_temp == 0 and inverter_temp == 0 and battery_power == 0:
        return None

    result = {
        'pvpower': pvpower,
        'feedin': feedin,
        'soc': soc,
        'battery_temp': battery_temp,
        'inverter_temp': inverter_temp,
        'battery_power': battery_power,
        'grid_voltage': "0"
    }

    return result