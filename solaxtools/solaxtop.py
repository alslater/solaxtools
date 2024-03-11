from time import sleep, time
from millify import millify
import tableprint as tp
from datetime import datetime
from .modbus import get_values
import termios
import sys
import tty
import select

def set_input_nonblocking():
    # Set stdin to non-blocking mode
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
    except termios.error:  # Ignore if already in non-blocking mode
        pass
    return old_settings


def restore_input_blocking(old_settings):
    # Restore stdin to blocking mode
    fd = sys.stdin.fileno()
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def wait(timeout = 10):
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

                sv = get_values()

                pvpower = sv['pvpower']
                feedin = sv['feedin']
                battery_power = sv['battery_power']

                usage = millify(pvpower + (abs(feedin) if feedin < 0 else 0) + (abs(battery_power) if battery_power < 0 else 0), precision=2)

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
                        f'{sv["inverter_temp"]}°C'
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