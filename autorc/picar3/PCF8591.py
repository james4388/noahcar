'''
**********************************************************************
* Filename    : PCF8591
* Description : A module to read the analog value with ADC PCF8591
* Author      : Dream
* Brand       : SunFounder
* E-mail      : service@sunfounder.com
* Website     : www.sunfounder.com
* Update      : Dream    2016-09-19    New release
**********************************************************************
'''
from autorc.picar3.base import BusModule


class PCF8591(BusModule):
    """ Light_Follow Module class """
    AD_CHANNEL = [0x43, 0x42, 0x41, 0x40]

    def __init__(self, address=0x48, bus_number=1):
        super(PCF8591, self).__init__(address=address, bus_number=bus_number)

    def read(self, channel):
        self.bus.write_byte(self.address, self.AD_CHANNEL[channel])
        self.bus.read_byte(self.address)  # dummy read to start conversion
        return self.bus.read_byte(self.address)

    @property
    def A0(self):
        return self.read(0)

    @property
    def A1(self):
        return self.read(1)

    @property
    def A2(self):
        return self.read(2)

    @property
    def A3(self):
        return self.read(3)
