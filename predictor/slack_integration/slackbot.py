import asyncio
import slack
import time

from file_loader.config_loader import modify_pause_alert, modify_pause_time
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
        print("EXCEPTION!!!!!!!! : ")
        print(e)
        client.chat_postMessage(
            channel=channel,
            text="There was an error, try again"
        )


# Gets the subtype of the user sending the message. Used to know if the message is sent by the bot or not.
# data: the message information
# Output: the subtype of the user sending the message (if available)
def get_subtype_bot(data):
    if "subtype" in data:
        subtype = data['subtype']
    else:
        subtype = ""

    return subtype


# Given some data from an user message, we will extract which metrics he's interested in getting information from.
# data: the message information
# output: the metric selected by the user
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


# Given a message from a user, we will study which information he wants to get from a metric (the actual information,
# the forecast or the regression information).
# data: the message information
# output: an array with the information to get (regression, forecast and/or actual)
def select_arrays_to_get(data):
    arrays_to_get = []
    if 'actual' in data['text'].lower():
        arrays_to_get.append('actual')

    if 'forecast' in data['text'].lower() or 'prediction' in data['text'].lower():
        arrays_to_get.append('forecast')

    if 'regression' in data['text'].lower() and not ('resetregression' in data['text'].lower()):
        arrays_to_get.append('regression')

    return arrays_to_get


# This function will parse the minutes the user wants to stop the alerts
# data: the message information
# output: the time the alerts have to pause (in minutes)
def get_time_pause_alert(data):
    info = data['text'].lower()

    a = info.find('pause alarms ')
    a_length = len('pause alarms ')
    b = info.find(' minutes')
    time_pause = int(info[a+a_length:b])

    return time_pause


# This function will receive messages from slack and see if they are asking for a chart. If so, a message with that
# information will be sent
@slack.RTMClient.run_on(event='message')
async def ask_charts(**payload):
    data = payload['data']
    subtype = get_subtype_bot(data)

    # get which metrics we want and what information we want from them
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
            print("EXCEPTION!!!!!!!!")
            print(e)
            channel_id = data.get("channel")
            webclient = payload['web_client']
            webclient.chat_postMessage(
                channel=channel_id,
                text="There was an error, try again"
            )


# This function will receive messages from slack and see if they are asking for help. If so, a message with that
# information will be sent
@slack.RTMClient.run_on(event='message')
async def ask_help(**payload):
    data = payload['data']
    subtype = get_subtype_bot(data)

    if 'help' in data['text'].lower() and subtype != "bot_message":
        text = "Welcome to the predictorBot! These are the instructions for using it:\n\n" \
               "*Alarms*: the bot will inform you when some anomaly occurs in the task-manager.\n " \
               "You can stop these alarms by writing _stop alarms_. \n" \
               "You can resume then by writing _resume alarms_ \n" \
               "You can also stop temporarily alarms by typing _pause alarms X minutes_ \n\n" \
               "*Resetting alarms*: If you want to reset the regression of one alarm (to stop errors in a precise " \
               "task_type metric, you only have to type _resetregresion_ plus the name of the task_type. \n" \
               "Per example: _resetregression basic preparation_. This will add a constant to the metric and " \
               "will 'reset it'\n\n" \
               "*Charts*: You can ask for the actual charts at any moment. For doing so you only have to say what do " \
               "you want to see (*actual*, *regression*, *forecast* or a mix of the three of them) and the name of " \
               "the task type (*basic preparation*, *toa*, *pmt*, etc...). \n" \
               "Per example: _actual forecast toa_"

        channel_id = data.get("channel")
        webclient = payload['web_client']
        webclient.chat_postMessage(
            channel=channel_id,
            text=text
        )


# This function will receive messages from slack and see if they are asking for pausing or resume the alarms. If so, the
# alarm system will be modified and we will inform the user
@slack.RTMClient.run_on(event='message')
async def modify_pause(**payload):
    data = payload['data']
    subtype = get_subtype_bot(data)

    config_file = "predictor/configuration.yaml"
    inform = False

    if 'stop' in data['text'].lower() and 'alarms' in data['text'].lower() and subtype != "bot_message":
        modify_pause_alert(config_file, True)
        message = "The alarm system has been stopped"
        inform = True

    elif 'resume' in data['text'].lower() and 'alarms' in data['text'].lower() and subtype != "bot_message":
        modify_pause_alert(config_file, False)
        modify_pause_time(file=config_file, new_value=0)
        inform = True
        message = "The alarm system has been resumed"

    elif 'pause' in data['text'].lower() and 'alarms' in data['text'].lower() and subtype != "bot_message":
        time_pause_user = get_time_pause_alert(data)
        time_pause = time_pause_user * 60 + time.time()
        modify_pause_time(file=config_file, new_value=time_pause)
        modify_pause_alert(config_file, True)
        inform = True
        message = "We are going to pause alarms for: " + str(time_pause_user) + " minutes"

    if inform:
        channel_id = data.get("channel")
        webclient = payload['web_client']
        webclient.chat_postMessage(
            channel=channel_id,
            text=message
        )

# This function will receive messages from slack and see if they are asking for resetting the regression. If so, the
# regression will be reset and the user will be informed
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


# Starts the reading messages process
# token: the slack token
def read_messages(token):
    while True:
        print("SlackBot Running")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        rtm_client = slack.RTMClient(token=token, run_async=True, loop=loop)
        loop.run_until_complete(rtm_client.start())
        print("Error in slackbot. Resetting in 3")
        time.sleep(3)
