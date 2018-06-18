import unittest
import time

from hardware.TB6612 import Motor
import RPi.GPIO as GPIO


class MotorTestCase(unittest.TestCase):
    def test_Motor(self):
        print("********************************************")
        print("*                                          *")
        print("*           SunFounder TB6612              *")
        print("*                                          *")
        print("*          Connect MA to BCM17             *")
        print("*          Connect MB to BCM18             *")
        print("*         Connect PWMA to BCM27            *")
        print("*         Connect PWMB to BCM12            *")
        print("*                                          *")
        print("********************************************")
        GPIO.setmode(GPIO.BCM)
        GPIO.setup((27, 22), GPIO.OUT)
        a = GPIO.PWM(27, 60)
        b = GPIO.PWM(22, 60)
        a.start(0)
        b.start(0)

        def a_speed(value):
            a.ChangeDutyCycle(value)

        def b_speed(value):
            b.ChangeDutyCycle(value)

        motorA = Motor(23)
        motorB = Motor(24)
        motorA.debug = True
        motorB.debug = True
        motorA.pwm = a_speed
        motorB.pwm = b_speed

        delay = 0.05

        motorA.forward()
        for i in range(0, 101):
            motorA.speed = i
            time.sleep(delay)
        for i in range(100, -1, -1):
            motorA.speed = i
            time.sleep(delay)

        motorA.backward()
        for i in range(0, 101):
            motorA.speed = i
            time.sleep(delay)
        for i in range(100, -1, -1):
            motorA.speed = i
            time.sleep(delay)

        motorB.forward()
        for i in range(0, 101):
            motorB.speed = i
            time.sleep(delay)
        for i in range(100, -1, -1):
            motorB.speed = i
            time.sleep(delay)

        motorB.backward()
        for i in range(0, 101):
            motorB.speed = i
            time.sleep(delay)
        for i in range(100, -1, -1):
            motorB.speed = i
            time.sleep(delay)


if __name__ == '__main__':
    unittest.main()
