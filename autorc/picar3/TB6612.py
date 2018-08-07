'''
**********************************************************************
* Filename    : TB6612.py
* Description : A driver module for TB6612
* Author      : Cavon
* Brand       : SunFounder
* E-mail      : service@sunfounder.com
* Website     : www.sunfounder.com
* Update      : Cavon    2016-09-23    New release
**********************************************************************
'''
import RPi.GPIO as GPIO

from autorc.picar3.base import Component


class Motor(Component):
    ''' Motor driver class
        Set direction_channel to the GPIO channel which connect to MA,
        Set motor_B to the GPIO channel which connect to MB,
        Both GPIO channel use BCM numbering;
        Set pwm_channel to the PWM channel which connect to PWMA,
        Set pwm_B to the PWM channel which connect to PWMB;
        PWM channel using PCA9685, Set pwm_address to your address,
        if is not 0x40
        Set debug to True to print(out debug informations.)
    '''
    _DEBUG_INFO = 'DEBUG "TB6612":'

    def __init__(self, direction_channel, pwm=None, offset=True):
        super(Motor, self).__init__()
        '''Init a motor on giving direction. channel and PWM channel.'''
        self.direction_channel = direction_channel
        self._pwm = pwm
        self._offset = offset
        self.forward_offset = self._offset

        self.backward_offset = not self.forward_offset
        self._speed = 0

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        self.log('setup motor direction channel at', direction_channel)
        self.log('setup motor pwm channel as',
                 self._pwm.__name__ if self._pwm else None)
        GPIO.setup(self.direction_channel, GPIO.OUT)

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, speed):
        ''' Set Speed with giving value '''
        if speed not in range(0, 101):
            raise ValueError(
                'speed ranges fron 0 to 100, not "{0}"'.format(speed))
        if not callable(self._pwm):
            raise ValueError('pwm is not callable, please set Motor.pwm to a '
                             'pwm control function with only 1 veriable speed')
        self.log('Set speed to %d:', speed)
        self._speed = speed
        self._pwm(self._speed)

    def forward(self):
        ''' Set the motor direction to forward '''
        GPIO.output(self.direction_channel, self.forward_offset)
        self.speed = self._speed
        self.log('Motor moving forward (%s)' % str(self.forward_offset))

    def backward(self):
        ''' Set the motor direction to backward '''
        GPIO.output(self.direction_channel, self.backward_offset)
        self.speed = self._speed
        self.log('Motor moving backward (%s)' % str(self.backward_offset))

    def stop(self):
        ''' Stop the motor by giving a 0 speed '''
        self.log('Motor stop')
        self.speed = 0

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        ''' Set offset for much user-friendly '''
        if value not in (True, False):
            raise ValueError(
                'offset value must be Bool value, not"{0}"'.format(value))
        self.forward_offset = value
        self.backward_offset = not self.forward_offset
        if self._DEBUG:
            print(self._DEBUG_INFO, 'Set offset to %d' % self._offset)

    @property
    def pwm(self):
        return self._pwm

    @pwm.setter
    def pwm(self, pwm):
        self.log('pwm set')
        self._pwm = pwm
