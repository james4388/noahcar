import unittest
from hardware import utils, constants


class UtilsTestCase(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(constants.RPI_REVISION_MODEL['a21041'],
                         constants.RPI_2_MODEL_B)

    def test_bus_number(self):
        self.assertEqual(utils.get_bus_number(constants.RPI_3_MODEL_B), 1)
        self.assertEqual(utils.get_bus_number(constants.RPI_MODEL_A), 0)


if __name__ == '__main__':
    unittest.main()
