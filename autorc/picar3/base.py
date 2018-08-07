from __future__ import print_function
import logging

import smbus2 as smbus

from autorc.picar3.utils import get_bus_number, get_pi_revision


class Component(object):
    ''' Base class for component '''
    _DEBUG = False
    _DEBUG_INFO = 'DEBUG "Component":'
    logger = None

    def __init__(self, debug=False, *args, **kwargs):
        if 'logger' in kwargs:
            self.logger = kwargs.pop('logger')
        if not self.logger:
            self.logger = logging.getLogger(self.__class__.__name__)
        self._DEBUG = debug

    def log(self, msg, *args, **kwargs):
        return  # Temporary suspress hardware log
        ''' Print debug info '''
        if self.logger:
            self.logger.info(msg, *args, **kwargs)
        else:
            print(msg)

    def debug(self, msg, *args, **kwargs):
        return  # Temporary suspress hardware log
        ''' Print debug info '''
        if self.logger:
            self.logger.debug(msg, *args, **kwargs)
        else:
            print(msg)


class BusModule(Component):
    ''' Base class for bus component '''
    _DEBUG_INFO = 'DEBUG "BusComponent":'

    def __init__(self, bus_number=None, address=None, debug=False):
        super(BusModule, self).__init__()
        self._DEBUG = debug
        self.address = address
        if bus_number is None:
            bus_number = get_bus_number(get_pi_revision())
        self.bus_number = bus_number
        self.bus = smbus.SMBus(self.bus_number)
