import unittest
import time
from hardware.front_wheels import Front_Wheels


class FronWheelTestCase(unittest.TestCase):
    def test_front_wheel(self):
        front_wheels = Front_Wheels(channel=0)
        try:
            while True:
                print("turn_left")
                front_wheels.turn_left()
                time.sleep(1)
                print("turn_straight")
                front_wheels.turn_straight()
                time.sleep(1)
                print("turn_right")
                front_wheels.turn_right()
                time.sleep(1)
                print("turn_straight")
                front_wheels.turn_straight()
                time.sleep(1)
        except KeyboardInterrupt:
            front_wheels.turn_straight()
        # Not sure how to test this


if __name__ == '__main__':
    unittest.main()
