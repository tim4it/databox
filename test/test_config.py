import unittest
from unittest import TestCase

from config.configs import get_local_config


class TestConfig(TestCase):

    def test_load_config(self):
        app_config = get_local_config()
        self.assertEqual(len(app_config.requests), 3)
        self.assertTrue(bool(app_config.birth_death_ratio_metric_key))
        self.assertTrue(app_config.request_timeout.connection_timeout > 0)
        self.assertTrue(app_config.request_timeout.request_timeout > 0)
        self.assertTrue(app_config.request_timeout.request_databox_total > 0)
        self.assertTrue(bool(app_config.databox_configuration.username))
        self.assertTrue(bool(app_config.databox_configuration.host))


if __name__ == '__main__':
    unittest.main()
