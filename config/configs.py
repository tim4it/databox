import logging
import os
from dataclasses import dataclass
from enum import Enum

import databox
import yaml

from util.helper import from_str_to_enum

logger = logging.getLogger(__name__)
# config folder for local config
CONFIG_FOLDER = "config"


class RequestType(Enum):
    AVERAGE_PAY = 1
    BIRTH_RATE = 2
    DEATH_RATE = 3
    BIRTH_DEATH_RATIO = 4


@dataclass
class RequestPost:
    url: str
    data: dict
    metric_key: str
    type: RequestType


@dataclass
class RequestTimeout:
    connection_timeout: int
    request_timeout: int
    request_databox_total: int


@dataclass
class AppConfig:
    requests: dict
    request_timeouts: dict
    databox_config: dict

    def __post_init__(self):
        average_pay_main = RequestType.AVERAGE_PAY.name.lower()
        birth_rate_main = RequestType.BIRTH_RATE.name.lower()
        death_rate_main = RequestType.DEATH_RATE.name.lower()
        average_pay = RequestPost(self.requests[average_pay_main]["url"],
                                  self.requests[average_pay_main]["data"],
                                  self.requests[average_pay_main]["metric_key"],
                                  from_str_to_enum(RequestType, average_pay_main))
        birth_rate = RequestPost(self.requests[birth_rate_main]["url"],
                                 self.requests[birth_rate_main]["data"],
                                 self.requests[birth_rate_main]["metric_key"],
                                 from_str_to_enum(RequestType, birth_rate_main))
        death_rate = RequestPost(self.requests[death_rate_main]["url"],
                                 self.requests[death_rate_main]["data"],
                                 self.requests[death_rate_main]["metric_key"],
                                 from_str_to_enum(RequestType, death_rate_main))
        self.birth_death_ratio_metric_key: str = self.requests["birth_death_ratio"]["metric_key"]
        self.request_timeout = RequestTimeout(int(self.request_timeouts["connect_sec"]),
                                              int(self.request_timeouts["request_sec"]),
                                              int(self.request_timeouts["request_databox_total"]))
        self.databox_configuration = databox.Configuration(
            host=self.databox_config["host"],
            username=self.databox_config["username"],
            password="")
        self.databox_push_parallel = bool(self.databox_config["push_parallel"])
        self.requests: list[RequestPost] = [average_pay, birth_rate, death_rate]


def get_local_config() -> AppConfig:
    local_config_path = os.path.join(os.getcwd(), CONFIG_FOLDER, "config.yml")
    # try to open local config file
    with open(local_config_path, "r") as yml_file:
        local_config_data = yaml.load(yml_file, Loader=yaml.FullLoader)
        local_config = AppConfig(**local_config_data)
    return local_config
