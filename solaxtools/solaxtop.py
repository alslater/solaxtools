import contextlib
from time import sleep, time
from millify import millify
import tableprint as tp
from datetime import datetime
from .modbus import get_values as get_modbus_values
from .local_api import get_values as get_local_values
import termios
import sys
import tty
import select
from configparser import ConfigParser
from os import getenv, path

config_file = path.join(getenv('HOME'), '.config/solaxtools.conf')

config = ConfigParser()
config.read(config_file)

_mode = config.get('solaxtop', 'mode', fallback="api")

def set_input_nonblocking():
    # Set stdin to non-blocking mode
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    with contextlib.suppress(termios.error):
        tty.setcbreak(fd)
    return old_settings


def restore_input_blocking(old_settings):
    # Restore stdin to blocking mode
    fd = sys.stdin.fileno()
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def wait(timeout = 10):
    """wait for maximum of timeout seconds, if 'q' is pressed then return True, else False.

    Args:
        timeout (int, optional): wait timeout. Defaults to 10.

    Returns:
        boolean: 'q' pressed
    """
    start_time = time()
    while True:
        remaining_time = timeout - (time() - start_time)
        if remaining_time <= 0:
            return False
        rlist, _, _ = select.select([sys.stdin], [], [], remaining_time)
        if rlist:
            key = sys.stdin.read(1)
            if key == 'q':
                return True
        else:
            sleep(0.1)


def solaxtop():
    tty_settings = set_input_nonblocking()

    header = [_mode, 'PV', 'Grid', 'Battery', 'Usage', 'SOC', 'BatTemp', 'InvTemp', 'GridV']
    try:
        with tp.TableContext(headers=header, style="round") as table:
            lines = 0
            while True:
                if lines > 20:
                    table(header)
                    lines = 0
                else:
                    lines += 1

                sv = get_modbus_values() if _mode == "modbus" else get_local_values()

                if sv is None:
                    table(
                        [
                            f'{datetime.now().strftime("%H:%M:%S")}',
                            '*',
                            '*',
                            '*',
                            '*',
                            '*',
                            '*',
                            '*',
                            '*'
                        ]
                    )
                else:
                    pvpower = sv['pvpower']
                    feedin = sv['feedin']
                    battery_power = sv['battery_power']

                    usage = millify(pvpower + -feedin - battery_power, precision=2)

                    pvpower = millify(pvpower, precision=2)
                    feedin = millify(feedin, precision=2)
                    battery_power = millify(battery_power, precision=2)

                    table(
                        [
                            f'{datetime.now().strftime("%H:%M:%S")}',
                            f'{pvpower}W',
                            f'{feedin}W',
                            f'{battery_power}W',
                            f'{usage}W',
                            f'{sv["soc"]}%',
                            f'{sv["battery_temp"]}°C',
                            f'{sv["inverter_temp"]}°C',
                            f'{sv["grid_voltage"]}V'
                        ]
                    )

                if wait(10):
                    break

    except KeyboardInterrupt:
        pass
    except Exception:
        restore_input_blocking(tty_settings)
        raise

    restore_input_blocking(tty_settings)