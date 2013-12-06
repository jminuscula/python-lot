"""
"""

from subprocess import call


class LedborgController:

    # Ledborg device path
    LED = '/dev/ledborg'

    # default ON/OFF colors (white and off)
    ON, OFF = '222', '000'

    # possible colors in order of brightness per color
    COLORS = {
        'white': '222',

        'blue': '002',
        'cyan': '022',
        'nightblue': '012',
        'lightblue': '122',
        'darkcyan': '011',
        'darkblue': '001',

        'green': '020',
        'limegreen': '120',
        'lightgreen': '121',
        'darkgreen': '010',
        'aquamarine': '021',

        'red': '200',
        'lightred': '211',
        'darkred': '100',

        'pink': '201',
        'violet': '102',
        'lightviolet': '112',
        'lightpurple': '202',
        'lightpink': '212',
        'purple': '101',

        'yellow': '220',
        'orange': '210',
        'lightyellow': '221',
        'darkyellow': '110',

        'black': '000',
        'grey': '111',
    }

    def is_on(self):
        with open(self.LED, 'r') as led:
            state = led.read()
            return state == self.ON

    def change_color(self, color):
        code = self.COLORS.get(color)
        if code:
            self.ON = code
        return True

    def _write_state(self, state):
        with open(self.LED, 'w') as led:
            led.write(state)
        return True

    def turn_on(self):
        return self._write_state(self.ON)

    def turn_off(self):
        return self._write_state(self.OFF)


class PowerSocketController:

    PLUG_ID = 1
    SYSTEM_ID = 11111
    ON, OFF = 1, 0

    RCSWITCH_PATH = '/usr/local/bin/rcswitch'

    def __init__(self):
        self.turn_off()

    def is_on(self):
        return None

    def change_color(self, color):
        return False

    def _write_state(self, state):
        return call((self.RCSWITCH_PATH, self.SYSTEM_ID, self.PLUG_ID, state))

    def turn_on(self):
        return self._write_state(self.ON)

    def turn_off(self):
        return self._write_state(self.OFF)
