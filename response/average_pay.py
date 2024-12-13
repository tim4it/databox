import logging

from databox import PushData

from response.response_init import ResponseInit, ResponseUnit, ResponseData
from util.helper import assert_true, create_date_from_month_year

logger = logging.getLogger(__name__)


class AveragePay(ResponseInit):

    def parse(self) -> ResponseUnit:
        dates_raw = self.raw_response["dimension"]["MESEC"]["category"]["label"]
        values_raw = self.raw_response["value"]
        assert_true(len(dates_raw), len(values_raw))
        dates = [self._parse_to_date(date) for date in dates_raw.values()]
        values = [float(val) for val in values_raw]
        data_units: list[ResponseData] = list()
        databox_units: list[PushData] = list()
        for idx, date in enumerate(dates):
            value_unit = values[idx]
            data_units.append(ResponseData(date, value_unit))
            databox_units.append(PushData(key=self.metric_key, value=value_unit, unit="EUR", var_date=date))

        return ResponseUnit(data_units, databox_units, self.request_type, self.response_status)

    @classmethod
    def _parse_to_date(cls, raw_year_month: str) -> str:
        """Parses a string like "2006M01" into (year, month) integers with validation."""
        try:
            year = int(raw_year_month[:4])
            month_str = raw_year_month[5:]
            month = int(month_str)
            if 1 <= month <= 12 and 1900 <= year:
                return create_date_from_month_year(year, month)
            logger.error(f"Can't parse year and month from: {raw_year_month}")
            raise ValueError("Can't parse year and month")
        except (ValueError, IndexError):
            logger.error(f"Validation error on parse year and month from: {raw_year_month}")
