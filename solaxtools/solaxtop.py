from time import sleep
from millify import millify
import tableprint as tp
from datetime import datetime
from .modbus import get_values

header = ['', 'PV', 'Grid', 'Battery', 'Usage', 'SOC', 'BatTemp', 'InvTemp']
try:
    with tp.TableContext(headers=header, style="round") as table:
        lines = 0
        while True:
            if lines > 20:
                table(header)
                lines = 0
            else:
                lines += 1

            pvpower, feedin, soc, battery_temp, inverter_temp, battery_power = get_values()

            usage = millify(pvpower + (abs(feedin) if feedin < 0 else 0) + (abs(battery_power) if battery_power < 0 else 0), precision=2)

            pvpower = millify(pvpower, precision=2)
            feedin = millify(feedin, precision=2)

            table(
                [
                   f'{datetime.now().strftime("%H:%M:%S")}',
                   f'{pvpower}W',
                   f'{feedin}W',
                   f'{battery_power}W',
                   f'{usage}W',
                   f'{soc}%',
                   f'{battery_temp}°C',
                   f'{inverter_temp}°C'
                ]
            )

            sleep(10)

except KeyboardInterrupt:
    pass