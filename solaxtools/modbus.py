
from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils

c = ModbusClient(host="192.168.86.61", port=502, unit_id=1, auto_open=True, timeout=30)

def get_values():
    if regs:= c.read_input_registers(0x0A, 2):
        pvpower = sum(regs)
    else:
        pvpower = 0

    if regs:= c.read_input_registers(0x46, 2):
        feedin = utils.get_list_2comp(regs, 16)[0]
    else:
        feedin = 0

    if regs := c.read_input_registers(0x1C, 1):
        soc = regs[0]
    else:
        soc = 0

    if regs := c.read_input_registers(0x18, 1):
        battery_temp = regs[0]
    else:
        battery_temp = 0

    if regs := c.read_input_registers(0x08, 1):
        inverter_temp = regs[0]
    else:
        inverter_temp = 0

    if regs := c.read_input_registers(0x16, 1):
        battery_power = utils.get_list_2comp(regs, 16)[0]
    else:
        battery_power = 0


    return pvpower, feedin, soc, battery_temp, inverter_temp, battery_power