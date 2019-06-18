import asyncio
import slack

from file_loader.config_loader import modify_pause_alert
from generate_images.image_generator import get_url_image
from prediction.regression import reset_regression


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

    try:
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
    except Exception as e:
        print("EXCEPTION!!!!!!!! : " + e)
        client.chat_postMessage(
            channel=channel,
            text="There was an error, try again"
        )


def get_subtype_bot(data):
    if "subtype" in data:
        subtype = data['subtype']
    else:
        subtype = ""

    return subtype


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


def select_arrays_to_get(data):
    arrays_to_get = []
    if 'actual' in data['text'].lower():
        arrays_to_get.append('actual')

    if 'forecast' in data['text'].lower() or 'prediction' in data['text'].lower():
        arrays_to_get.append('forecast')

    if 'regression' in data['text'].lower():
        arrays_to_get.append('regression')

    return arrays_to_get


@slack.RTMClient.run_on(event='message')
async def ask_charts(**payload):
    data = payload['data']
    subtype = get_subtype_bot(data)

    arrays_to_get = select_arrays_to_get(data)
    metric = select_metric(data)

    if metric != "" and arrays_to_get != [] and subtype != "bot_message":
        url = get_url_image(arrays_to_get, metric)

        try:
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
        except Exception as e:
            print("EXCEPTION!!!!!!!! : " + e)
            channel_id = data.get("channel")
            webclient = payload['web_client']
            webclient.chat_postMessage(
                channel=channel_id,
                text="There was an error, try again"
            )


@slack.RTMClient.run_on(event='message')
async def ask_help(**payload):
    data = payload['data']
    subtype = get_subtype_bot(data)

    if 'help' in data['text'].lower() and subtype != "bot_message":
        text = "Welcome to the predictorBot! These are the instructions for using it:\n" \
               "Alarms: the bot will inform you when some anomaly occurs in the task-manager. " \
               "You can stop these alarms by saying 'stop alarms'. You can resume then by saying 'resume alarms'\n" \
               "Resetting alarms: If you want to reset the regression of one alarm (to stop errors in a precise" \
               "task_type metric, you only have to type 'resetregresion' plus the name of the task_type. Per example:" \
               "'resetregression basic preparation'. This will add a constant to the metric and will 'reset it'\n" \
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
    subtype = get_subtype_bot(data)

    config_file = "predictor/configuration.yaml"
    inform = False

    if 'stop' in data['text'].lower() and 'alarms' in data['text'].lower() and subtype != "bot_message":
        modify_pause_alert(config_file, True)
        inform = True

    elif 'resume' in data['text'].lower() and 'alarms' in data['text'].lower() and subtype != "bot_message":
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


@slack.RTMClient.run_on(event='message')
async def ask_reset_regression(**payload):
    data = payload['data']
    config_file = "predictor/configuration.yaml"
    subtype = get_subtype_bot(data)

    if 'resetregression' in data['text'].lower() and subtype != "bot_message":
        metric = select_metric(data)
        value = reset_regression(config_file, metric)

        message = "We are adding this constant: " + str(value)

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
