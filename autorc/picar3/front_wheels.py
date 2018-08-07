'''
**********************************************************************
* Filename    : front_wheels
* Description : A module to control the front wheels of RPi Car
* Author      : Cavon
* Brand       : SunFounder
* E-mail      : service@sunfounder.com
* Website     : www.sunfounder.com
* Update      : Cavon    2016-09-13    New release
*               Cavon    2016-11-04    fix for submodules
**********************************************************************
'''
from autorc.picar3 import Servo
from autorc.picar3.base import Component


class Front_Wheels(Component):
    ''' Front wheels control class '''
    FRONT_WHEEL_CHANNEL = 0

    _DEBUG_INFO = 'DEBUG "front_wheels":'

    def __init__(self, debug=False, db="config", bus_number=1,
                 channel=FRONT_WHEEL_CHANNEL):
        ''' setup channels and basic stuff '''
        super(Front_Wheels, self).__init__()
        self._channel = channel
        self._straight_angle = 90
        self.turning_max = 20
        self._turning_offset = 0    # Read from config

        self.wheel = Servo.Servo(self._channel, bus_number=bus_number,
                                 offset=self.turning_offset)
        self.debug = debug
        self.log('Front wheel PWM channel:', self._channel)
        self.log('Front wheel offset value:', self.turning_offset)

        self._angle = {
            "left": self._min_angle,
            "straight": self._straight_angle,
            "right": self._max_angle
        }
        self.log('left angle: %s, straight angle: %s, right angle: %s' % (
            self._angle["left"], self._angle["straight"], self._angle["right"]
        ))

    def turn_left(self):
        ''' Turn the front wheels left '''
        self.log("Turn left")
        self.wheel.write(self._angle["left"])

    def turn_straight(self):
        ''' Turn the front wheels back straight '''
        self.log("Turn straight")
        self.wheel.write(self._angle["straight"])

    def turn_right(self):
        ''' Turn the front wheels right '''
        self.log("Turn right")
        self.wheel.write(self._angle["right"])

    def turn(self, angle):
        ''' Turn the front wheels to the giving angle '''
        self.log("Turn to %d", angle)
        if angle < self._angle["left"]:
            angle = self._angle["left"]
        if angle > self._angle["right"]:
            angle = self._angle["right"]
        self.wheel.write(angle)

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, chn):
        self._channel = chn

    @property
    def turning_max(self):
        return self._turning_max

    @turning_max.setter
    def turning_max(self, angle):
        self._turning_max = angle
        self._min_angle = self._straight_angle - angle
        self._max_angle = self._straight_angle + angle
        self._angle = {
            "left": self._min_angle,
            "straight": self._straight_angle,
            "right": self._max_angle
        }

    @property
    def turning_offset(self):
        return self._turning_offset

    @turning_offset.setter
    def turning_offset(self, value):
        if not isinstance(value, int):
            raise TypeError('"turning_offset" must be "int"')
        self._turning_offset = value
        # self.db.set('turning_offset', value)
        self.wheel.offset = value
        self.turn_straight()

    def ready(self):
        ''' Get the front wheels to the ready position. '''
        self.log('Turn to "Ready" position')
        self.wheel.offset = self.turning_offset
        self.turn_straight()

    def calibration(self):
        ''' Get the front wheels to the calibration position. '''
        self.log('Turn to "Calibration" position')
        self.turn_straight()
        self.cali_turning_offset = self.turning_offset

    def cali_left(self):
        ''' Calibrate the wheels to left '''
        self.cali_turning_offset -= 1
        self.wheel.offset = self.cali_turning_offset
        self.turn_straight()

    def cali_right(self):
        ''' Calibrate the wheels to right '''
        self.cali_turning_offset += 1
        self.wheel.offset = self.cali_turning_offset
        self.turn_straight()

    def cali_ok(self):
        ''' Save the calibration value '''
        self.turning_offset = self.cali_turning_offset
        # self.db.set('turning_offset', self.turning_offset)
