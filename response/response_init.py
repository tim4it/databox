from dataclasses import dataclass

from databox import PushData

from config.configs import RequestType
from util.helper import assert_true, create_date_from_year


@dataclass
class ResponseData:
    date: str
    value: float


@dataclass
class ResponseUnit:
    data_units: list[ResponseData]
    databox_units: list[PushData]
    data_type: RequestType
    response_status: int


class ResponseInit:

    def __init__(self, raw_response: dict,
                 request_type: RequestType,
                 metric_key: str,
                 response_status: int) -> None:
        self.raw_response = raw_response
        self.request_type = request_type
        self.response_status = response_status
        self.metric_key = metric_key

    def _get_birth_death_response_unit(self, unit: str):
        dates_raw = self.raw_response["dimension"]["LETO"]["category"]["label"]
        values_raw = self.raw_response["value"]
        assert_true(len(dates_raw), len(values_raw))
        dates = [create_date_from_year(int(date)) for date in dates_raw.values()]
        values = [float(val) for val in values_raw]
        data_units: list[ResponseData] = list()
        databox_units: list[PushData] = list()
        for idx, date in enumerate(dates):
            value_unit = values[idx]
            data_units.append(ResponseData(date, value_unit))
            databox_units.append(PushData(key=self.metric_key, value=value_unit, unit=unit, var_date=date))

        return ResponseUnit(data_units, databox_units, self.request_type, self.response_status)
