from __future__ import print_function

import smbus2 as smbus

from .utils import get_bus_number


class Component(object):
    ''' Base class for component '''
    _DEBUG = False
    _DEBUG_INFO = 'DEBUG "Component":'

    def __init__(self, debug=False, *args, **kwargs):
        self._DEBUG = debug

    def log(self, *args):
        ''' Print debug info '''
        if self._DEBUG:
            print(self._DEBUG_INFO, *args)

    @property
    def debug(self):
        return self._DEBUG

    @debug.setter
    def debug(self, debug):
        '''Set if debug information shows'''
        if debug in (True, False):
            self._DEBUG = debug
        else:
            raise ValueError('debug must be "True" (Set debug on) or "False"'
                             ' (Set debug off), not "{0}"'.format(debug))

        if self._DEBUG:
            print(self._DEBUG_INFO, "Set debug on")
        else:
            print(self._DEBUG_INFO, "Set debug off")


class BusModule(Component):
    ''' Base class for bus component '''
    _DEBUG_INFO = 'DEBUG "BusComponent":'

    def __init__(self, bus_number=None, address=None, debug=False):
        self._DEBUG = debug
        self.address = address
        if bus_number is None:
            bus_number = get_bus_number()
        self.bus_number = bus_number
        self.bus = smbus.SMBus(self.bus_number)
