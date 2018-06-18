import unittest
import time

from hardware import PCA9685


class PWMCase(unittest.TestCase):
    def test_PWM(self):
        pwm = PCA9685.PWM()
        pwm.frequency = 60
        for i in range(16):
            time.sleep(0.5)
            print('\nChannel %d\n' % i)
            time.sleep(0.5)
            for j in range(4096):
                pwm.write(i, 0, j)
                print('PWM value: %d' % j)
                time.sleep(0.0003)


if __name__ == '__main__':
    unittest.main()
