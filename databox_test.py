from pprint import pprint

import databox
from databox import PushData
from databox.rest import ApiException

from util.helper import create_date_from_month_year

# Configuration setup for the Databox API client
# The API token is used as the username for authentication
# It's recommended to store your API token securely, e.g., in an environment variable
configuration = databox.Configuration(
    host="https://push.databox.com",
    username="7e0b21ad3ea140ff9c38bd407848ee77",
    password=""
)

# It's crucial to specify the correct Accept header for the API request
with databox.ApiClient(configuration, "Accept", "application/vnd.databox.v2+json", ) as api_client:
    api_instance = databox.DefaultApi(api_client)

    # Define the data to be pushed to the Databox Push API# Prepare the data you want to push to Databox
    # The 'key' should match a metric in your Databox account, 'value' is the data point, 'unit' is optional, and 'date' is the timestamp of the data point

    push_data = [PushData(key="My_metric", value=155.0, unit="USD", var_date=create_date_from_month_year(2024, 6)),
                 PushData(key="My_metric", value=177.5, unit="USD", var_date=create_date_from_month_year(2024, 7))]

    try:
        api_instance.data_post(push_data=push_data)
    except ApiException as e:
        # Handle exceptions that occur during the API call, such as invalid data or authentication issues
        pprint("API Exception occurred: %s\n" % e)
    except Exception as e:
        # Handle any other unexpected exceptions
        pprint("An unexpected error occurred: %s\n" % e)
