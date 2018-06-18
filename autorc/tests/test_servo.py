import unittest
import time

from hardware.Servo import Servo


class ServoTestCase(unittest.TestCase):
    def test_Servo(self):
        # Warning this may make servo stuck if it already installed
        a = Servo(1)
        a.setup()
        for i in range(0, 180, 5):
            print(i)
            a.write(i)
            time.sleep(0.1)
        for i in range(180, 0, -5):
            print(i)
            a.write(i)
            time.sleep(0.1)
        for i in range(0, 91, 2):
            a.write(i)
            time.sleep(0.05)
        print(i)


if __name__ == '__main__':
    unittest.main()
