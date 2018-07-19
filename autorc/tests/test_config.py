import unittest
from unittest.mock import mock_open, patch


TEST_FOR_CONFIG = 'pick_me_up'
do_not_pick_me = False


class ConfigTestCase(unittest.TestCase):
    def test_config_json(self):
        from autorc.config import Config
        m = mock_open(
            read_data='''{"TEST_KEY":"OK", "do_not_pick_this_one": false}''')
        with patch('autorc.config.open', m):
            config = Config(config_file='_mock_file_')

        m.assert_called_once_with('_mock_file_')
        self.assertEqual(config.TEST_KEY, "OK")
        self.assertEqual(hasattr(config, 'do_not_pick_this_one'), False)

    def test_config_module(self):
        from autorc.config import Config
        config = Config(config_module=__name__)
        self.assertEqual(config.TEST_FOR_CONFIG, TEST_FOR_CONFIG)
        self.assertEqual(hasattr(config, 'do_not_pick_me'), False)


if __name__ == '__main__':
    unittest.main()
