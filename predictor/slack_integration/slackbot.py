import asyncio
import slack

from api_calls.general_api_calls import get_values, get_query_actual_search
from file_loader.config_loader import get_server, get_monitoring_time_span, get_params_arima_metric, get_forecast_time, \
    get_forecast_training_time, modify_pause_alert
from generate_images.image_generator import generate_url_multichart
from prediction.arima import get_forecast_array
from prediction.regression import get_regression_array_search


# Function that sends a message to slack
# token: Token for the bot
# channel: Slack channel where to send the message
# message: message to send
def send_message(token, channel, message):
    client = slack.WebClient(token)
    client.chat_postMessage(
        channel=channel,
        text=message
    )


# Function that sends an image with a message to slack
# token: Token for the bot
# channel: Slack channel where to send the message
# message: message to send
# image_url: url with the image to show
def send_image(token, channel, message, image_url):
    client = slack.WebClient(token)
    client.chat_postMessage(
        channel=channel,
        text=message,
        blocks=[
            {
                "type": "image",
                "title": {
                    "type": "plain_text",
                    "text": message
                },
                "block_id": "image4",
                "image_url": image_url,
                "alt_text": message
            }
        ]
    )


def select_metric(data):
    metric = ""
    if 'basic' and 'preparation' in data['text'].lower():
        metric = "incoming_task_count_total-BASIC_PREPARATION"
    elif 'create' and 'jpegs' in data['text'].lower():
        metric = "incoming_task_count_total-CREATE_JPEGS"
    elif 'fubo' in data['text'].lower():
        metric = "incoming_task_count_total-FUBO"
    elif 'pmt' in data['text'].lower():
        metric = "incoming_task_count_total-PMT"
    elif 'toa' and '4k' in data['text'].lower():
        metric = "incoming_task_count_total-TOA_4K"
    elif 'toa' in data['text'].lower():
        metric = "incoming_task_count_total-TOA"
    elif 'veset' and 'belgium' in data['text'].lower():
        metric = "incoming_task_count_total-VESET_BELGIUM"
    elif 'task' and 'failure' in data['text'].lower():
        metric = "task_in_failure"

    return metric


def get_url_image(arrays_to_get, metric):
    config_file = "predictor/configuration.yaml"

    server = get_server(config_file)
    time = get_monitoring_time_span(config_file)
    query = get_query_actual_search(config=config_file, metric=metric)

    multi_data = []
    array_names = []

    if 'actual' in arrays_to_get:
        actual = get_values(server=server, query=query, minutes=time)
        multi_data.append(actual)
        array_names.append('actual')

    if 'regression' in arrays_to_get:
        regression_array = get_regression_array_search(config=config_file, metric=metric)
        multi_data.append(regression_array)
        array_names.append('regression')

    if 'forecast' in arrays_to_get:
        forecast_time = get_forecast_time(config_file)
        forecast_training_time = get_forecast_training_time(config_file)
        time_series_training = get_values(server=server, query=query, minutes=forecast_training_time)
        params = get_params_arima_metric(file=config_file, metric=metric)

        forecasts = get_forecast_array(params=params, time_series=time_series_training, forecast_time=forecast_time)

        for set_arima in forecasts:
            array_names.append("forecast:" + set_arima[0])
            multi_data.append(set_arima[1])

    url = generate_url_multichart(array_data=multi_data, array_names=array_names, name=metric,
                                  time=time)

    return url


def select_arrays_to_get(data):
    arrays_to_get = []
    if 'actual' in data['text'].lower():
        arrays_to_get.append('actual')

    if 'forecast' in data['text'].lower():
        arrays_to_get.append('forecast')

    if 'regression' in data['text'].lower():
        arrays_to_get.append('regression')

    return arrays_to_get


@slack.RTMClient.run_on(event='message')
async def ask_charts(**payload):
    data = payload['data']

    arrays_to_get = select_arrays_to_get(data)
    metric = select_metric(data)

    if metric != "" and arrays_to_get != []:
        url = get_url_image(arrays_to_get, metric)

        channel_id = data.get("channel")
        webclient = payload['web_client']
        webclient.chat_postMessage(
            channel=channel_id,
            text=metric,
            blocks=[
                {
                    "type": "image",
                    "title": {
                        "type": "plain_text",
                        "text": metric
                    },
                    "block_id": "image4",
                    "image_url": url,
                    "alt_text": metric
                }
            ]
        )


@slack.RTMClient.run_on(event='message')
async def ask_help(**payload):
    data = payload['data']

    if 'help' in data['text'].lower():
        text = "Welcome to the predictorBot! These are the instructions for using it:\n" \
               "Alarms: the bot will inform you when some anomaly occurs in the task-manager. " \
               "You can stop these alarms by saying 'stop alarms'. You can resume then by saying 'resume alarms'\n" \
               "Charts: You can ask for the actual charts at any moment. For doing so you only have to say what do you" \
               "want to see (actual, regression, forecast or a mix of the three of them) and the name of the task type " \
               "(basic preparation, toa, pmt, etc...)"

        channel_id = data.get("channel")
        webclient = payload['web_client']
        webclient.chat_postMessage(
            channel=channel_id,
            text=text
        )


@slack.RTMClient.run_on(event='message')
async def modify_pause(**payload):
    data = payload['data']
    config_file = "predictor/configuration.yaml"
    inform = False

    if 'stop' in data['text'].lower() and 'alarms' in data['text'].lower():
        modify_pause_alert(config_file, True)
        inform = True

    elif 'resume' in data['text'].lower() and 'alarms' in data['text'].lower():
        modify_pause_alert(config_file, False)
        inform = True

    if inform:
        message = "The alarm system has been modified"

        channel_id = data.get("channel")
        webclient = payload['web_client']
        webclient.chat_postMessage(
            channel=channel_id,
            text=message
        )


def read_messages(token):
    print("SlackBot Running")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    rtm_client = slack.RTMClient(token=token, run_async=True, loop=loop)
    loop.run_until_complete(rtm_client.start())
