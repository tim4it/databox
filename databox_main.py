import asyncio
import json
import logging
import time

import aiohttp
import databox
from aiohttp import ClientSession
from databox import PushData, ApiException

from config.configs import get_local_config, RequestPost, RequestTimeout, RequestType, AppConfig
from response.average_pay import AveragePay
from response.birth_rate import BirthRate
from response.death_rate import DeathRate
from response.response_init import ResponseUnit
from util.helper import assert_true


async def push_data_to_databox(metrics: ResponseUnit, app_config: AppConfig) -> int:
    """
    Push individual data to databox
    :param metrics: metrics data
    :param app_config: application config
    :return: response status
    """
    with databox.ApiClient(app_config.databox_configuration, "Accept",
                           "application/vnd.databox.v2+json", ) as api_client:
        response_status = 200
        api_instance = databox.DefaultApi(api_client)
        try:
            api_instance.data_post(push_data=metrics.databox_units,
                                   _request_timeout=app_config.request_timeout.request_databox_total)
            return response_status
        except ApiException as api_err:
            # Handle exceptions that occur during the API call, such as invalid data or authentication issues
            logger.error(f"API Exception occurred: {api_err}")
            return 400
        except Exception as e:
            # Handle any other unexpected exceptions
            logger.error(f"An unexpected error occurred: {e}")
            return 500


async def push_to_databox(all_metrics: list[ResponseUnit],
                          app_config: AppConfig) -> list[int]:
    """
    Push data to databox in parallel on in serial - depends of configuration
    :param all_metrics: all metrics
    :param app_config: application config
    :return: response statuses from all tasks
    """
    if app_config.databox_push_parallel:
        tasks = []
        for metric in all_metrics:
            tasks.append(asyncio.create_task(push_data_to_databox(metric, app_config)))
        response_statuses: list[int] = await asyncio.gather(*tasks)
    else:
        response_statuses: list[int] = []
        for metric in all_metrics:
            response_status = await push_data_to_databox(metric, app_config)
            response_statuses.append(response_status)

    return response_statuses


async def make_post_request(request_post: RequestPost,
                            request_timeout: RequestTimeout,
                            session: ClientSession) -> ResponseUnit:
    """
    Makes a single POST request with timeouts.
    :param request_post: request data
    :param request_timeout: request timeouts
    :param session: client session
    :return: response unit with all the data
    """
    try:
        response_status = -1
        headers = {"Content-Type": "application/json"}
        logger.info(
            f"Making POST request to {request_post.url}, type {request_post.type.name} with data: {request_post.data}")
        async with session.post(request_post.url, json=request_post.data,
                                headers=headers,
                                timeout=aiohttp.ClientTimeout(connect=request_timeout.connection_timeout,
                                                              total=request_timeout.request_timeout)) as response:
            response_data = await response.text()
            response_dict = json.loads(response_data)
            response_status = response.status
            if request_post.type is RequestType.BIRTH_RATE:
                data_point = BirthRate(response_dict, request_post.type, request_post.metric_key, response_status)
            elif request_post.type is RequestType.DEATH_RATE:
                data_point = DeathRate(response_dict, request_post.type, request_post.metric_key, response_status)
            elif request_post.type is RequestType.AVERAGE_PAY:
                data_point = AveragePay(response_dict, request_post.type, request_post.metric_key, response_status)
            else:
                logger.error(f"Wrong request type. Available: {request_post.type}")
                raise ValueError("Wrong request type")
            return data_point.parse()
    except aiohttp.ClientError as e:
        logger.error(f"Error making request to {request_post}: {e}")
        return ResponseUnit([], [], request_post.type, response_status)
    except asyncio.TimeoutError:
        logger.error(f"Timeout occurred for request to {request_post.url}")
        return ResponseUnit([], [], request_post.type, response_status)
    except Exception as e:
        logger.error(f"An unexpected error occurred ({request_post}): {e}")
        return ResponseUnit([], [], request_post.type, response_status)


async def get_all_metrics(app_config: AppConfig) -> list[ResponseUnit]:
    """
    Get all the data in parallel
    :param app_config: application config
    :return:
    """
    async with aiohttp.ClientSession() as session:
        tasks = []
        request_timeout = app_config.request_timeout
        for request_post in app_config.requests:
            tasks.append(asyncio.create_task(make_post_request(request_post, request_timeout, session)))
        results: list[ResponseUnit] = await asyncio.gather(*tasks)

    return results


async def find_data_unit(response_units: list[ResponseUnit], request_type: RequestType) -> ResponseUnit:
    """
    Find data unit by RequestType
    :param response_units: response unit
    :param request_type: request type
    :return: response unit
    """
    for response_unit in response_units:
        if response_unit.data_type is request_type:
            return response_unit
    logger.error(f"Can' find match data for type: {request_type} in {[unit.data_type for unit in response_units]}")
    raise ValueError("Can' find match data")


async def get_birth_death_ratio(response_units: list[ResponseUnit],
                                app_config: AppConfig) -> list[PushData]:
    """
    Get birt death ratio. This means birth - death per year
    :param response_units: response unit
    :param app_config: application config
    :return: databox push data
    """
    birth_rates = await find_data_unit(response_units, RequestType.BIRTH_RATE)
    death_rates = await find_data_unit(response_units, RequestType.DEATH_RATE)
    assert_true(len(birth_rates.data_units), len(death_rates.data_units))
    death_rate_units = death_rates.data_units
    databox_units: list[PushData] = list()
    for idx, birth_rate in enumerate(birth_rates.data_units):
        death_rate = death_rate_units[idx]
        assert_true(birth_rate.date, death_rate.date)
        databox_units.append(
            PushData(key=app_config.birth_death_ratio_metric_key, value=(birth_rate.value - death_rate.value),
                     unit="Rt", var_date=birth_rate.date))
    return databox_units


async def main() -> None:
    try:
        app_config = get_local_config()
        all_metrics = await get_all_metrics(app_config)
        birth_death_ratio = await get_birth_death_ratio(all_metrics, app_config)
        all_metrics.append(ResponseUnit([], birth_death_ratio, RequestType.BIRTH_DEATH_RATIO, 200))
        response_statuses = await push_to_databox(all_metrics, app_config)
        for metric in all_metrics:
            logger.info(f"Metric({metric.data_type.name}): {metric}")
        logger.info(f"Databox responses: {response_statuses}")
    except BaseException as e:
        logger.error(f"Application error! {e}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    start_time = int(time.time_ns())
    asyncio.run(main())
    logger.info(f"Total execution time: {(int(time.time_ns()) - start_time) / 1_000_000:.2f} ms")
