'''
**********************************************************************
* Filename    : back_wheels.py
* Description : A module to control the back wheels of RPi Car
* Author      : Cavon
* Brand       : SunFounder
* E-mail      : service@sunfounder.com
* Website     : www.sunfounder.com
* Update      : Cavon    2016-09-13    New release
*               Cavon    2016-11-04    fix for submodules
**********************************************************************
'''

from autorc.picar3 import TB6612
from autorc.picar3 import PCA9685
from autorc.picar3.base import Component


class Back_Wheels(Component):
    ''' Back wheels control class '''
    Motor_A = 17
    Motor_B = 27

    PWM_A = 4
    PWM_B = 5

    _DEBUG_INFO = 'DEBUG "back_wheels.py":'

    def __init__(self, debug=False, bus_number=1):
        ''' Init the direction channel and pwm channel '''
        self.forward_A = True
        self.forward_B = True

        self.forward_A = 0
        self.forward_B = 0

        self.left_wheel = TB6612.Motor(self.Motor_A, offset=self.forward_A)
        self.right_wheel = TB6612.Motor(self.Motor_B, offset=self.forward_B)

        self.pwm = PCA9685.PWM(bus_number=bus_number)

        def _set_a_pwm(value):
            pulse_wide = self.pwm.map(value, 0, 100, 0, 4095)
            self.pwm.write(self.PWM_A, 0, pulse_wide)

        def _set_b_pwm(value):
            pulse_wide = self.pwm.map(value, 0, 100, 0, 4095)
            self.pwm.write(self.PWM_B, 0, pulse_wide)

        self.left_wheel.pwm = _set_a_pwm
        self.right_wheel.pwm = _set_b_pwm

        self._speed = 0

        self.debug = debug
        self.log('Set left wheel to #%d, PWM channel to %d' % (
            self.Motor_A, self.PWM_A))
        self.log('Set right wheel to #%d, PWM channel to %d' % (
            self.Motor_B, self.PWM_B))

    def forward(self):
        ''' Move both wheels forward '''
        self.left_wheel.forward()
        self.right_wheel.forward()
        self.log('Running forward')

    def backward(self):
        ''' Move both wheels backward '''
        self.left_wheel.backward()
        self.right_wheel.backward()
        self.log('Running backward')

    def stop(self):
        ''' Stop both wheels '''
        self.left_wheel.stop()
        self.right_wheel.stop()
        self.log('Stop')

    @property
    def speed(self, speed):
        return self._speed

    @speed.setter
    def speed(self, speed):
        self._speed = speed
        ''' Set moving speeds '''
        self.left_wheel.speed = self._speed
        self.right_wheel.speed = self._speed
        self.log('Set speed to %d', self._speed)

    def ready(self):
        ''' Get the back wheels to the ready position. (stop) '''
        self.log('Turn to "Ready" position')
        self.left_wheel.offset = self.forward_A
        self.right_wheel.offset = self.forward_B
        self.stop()

    def calibration(self):
        ''' Get the front wheels to the calibration position. '''
        self.log('Turn to "Calibration" position')
        self.speed = 50
        self.forward()
        self.cali_forward_A = self.forward_A
        self.cali_forward_B = self.forward_B

    def cali_left(self):
        ''' Reverse the left wheels forward direction in calibration '''
        self.cali_forward_A = (1 + self.cali_forward_A) & 1
        self.left_wheel.offset = self.cali_forward_A
        self.forward()

    def cali_right(self):
        ''' Reverse the right wheels forward direction in calibration '''
        self.cali_forward_B = (1 + self.cali_forward_B) & 1
        self.right_wheel.offset = self.cali_forward_B
        self.forward()

    def cali_ok(self):
        ''' Save the calibration value '''
        self.forward_A = self.cali_forward_A
        self.forward_B = self.cali_forward_B
        self.db.set('forward_A', self.forward_A)
        self.db.set('forward_B', self.forward_B)
        self.stop()
