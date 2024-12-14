import unittest
from unittest import TestCase

from config.configs import RequestType
from util.helper import create_date_from_year, create_date_from_month_year, from_str_to_enum


class TestHelper(TestCase):

    def test_create_date_from_year(self):
        self.assertEqual(create_date_from_year(1977), "1977-01-01T00:00:00")
        self.assertEqual(create_date_from_year(2000), "2000-01-01T00:00:00")
        self.assertEqual(create_date_from_year(2055), "2055-01-01T00:00:00")

    def test_create_date_from_year_fail(self):
        with self.assertRaises(ValueError):
            self.assertEqual(create_date_from_year(-1), "N/A")
            self.assertEqual(create_date_from_year(0), "N/A")
            self.assertEqual(create_date_from_year(1), "N/A")
            self.assertEqual(create_date_from_year(3561), "N/A")

    def test_create_date_from_month_year(self):
        self.assertEqual(create_date_from_month_year(1988, 1), "1988-01-01T00:00:00")
        self.assertEqual(create_date_from_month_year(2000, 2), "2000-02-01T00:00:00")
        self.assertEqual(create_date_from_month_year(2055, 3), "2055-03-01T00:00:00")
        self.assertEqual(create_date_from_month_year(2099, 12), "2099-12-01T00:00:00")

    def test_create_date_from_month_year_fail(self):
        with self.assertRaises(ValueError):
            self.assertEqual(create_date_from_month_year(1988, 0), "1988-01-01T00:00:00")
            self.assertEqual(create_date_from_month_year(2000, 13), "2000-02-01T00:00:00")
            self.assertEqual(create_date_from_month_year(2055, -1), "2055-03-01T00:00:00")

    def test_from_str_to_enum(self):
        self.assertEqual(from_str_to_enum(RequestType, "average_PAY"), RequestType.AVERAGE_PAY)
        self.assertEqual(from_str_to_enum(RequestType, "    birth_rate"), RequestType.BIRTH_RATE)
        self.assertEqual(from_str_to_enum(RequestType, "DEATH_rate "), RequestType.DEATH_RATE)
        self.assertEqual(from_str_to_enum(RequestType, "  BIRTH_death_rATIO "), RequestType.BIRTH_DEATH_RATIO)

    def test_from_str_to_enum_fail(self):
        with self.assertRaises(NotImplementedError):
            from_str_to_enum(RequestType, "average_PAY_")
            from_str_to_enum(RequestType, "    birth_rate1")
            from_str_to_enum(RequestType, " ")
            from_str_to_enum(RequestType, "  BIRTH_death_rATeO ")


if __name__ == '__main__':
    unittest.main()
