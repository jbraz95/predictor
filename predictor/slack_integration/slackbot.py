import asyncio
import slack

from api_calls.general_api_calls import get_values, get_query_actual_search
from file_loader.config_loader import get_server, get_monitoring_time_span
from generate_images.image_generator import generate_data_chart, generate_timeseries_chart
from prediction.regression import get_regression_array, get_regression_array_search


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


@slack.RTMClient.run_on(event='message')
async def ask_actual_data(**payload):
    config_file = "predictor/configuration.yaml"
    data = payload['data']
    if 'actual' in data['text'].lower():
        metric = select_metric(data)
        server = get_server(config_file)
        time = get_monitoring_time_span(config_file)

        query = get_query_actual_search(config=config_file, metric=metric)
        array = get_values(server=server, query=query, minutes=time)
        print(array)
        url = generate_timeseries_chart(array, metric)

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
async def ask_regression(**payload):
    config_file = "predictor/configuration.yaml"
    data = payload['data']
    if 'regression' in data['text'].lower():
        metric = select_metric(data)

        regression_array = get_regression_array_search(config=config_file, metric=metric)
        url = generate_data_chart(regression_array, metric)

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


def read_messages(token):
    print("SlackBot Running")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    rtm_client = slack.RTMClient(token=token, run_async=True, loop=loop)
    loop.run_until_complete(rtm_client.start())
