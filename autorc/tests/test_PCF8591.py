import unittest
from hardware.PCF8591 import PCF8591


class PCF8591TestCase(unittest.TestCase):
    def test_PCF8591(self):
        ADC = PCF8591(0x48)
        ADC.A0()
        ADC.A1()
        ADC.A2()
        ADC.A3()
        # Not sure how to test this


if __name__ == '__main__':
    unittest.main()
