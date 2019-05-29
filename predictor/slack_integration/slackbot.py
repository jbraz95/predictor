import slack


def send_message(token, channel, message):
    client = slack.WebClient(token)
    client.chat_postMessage(
        channel=channel,
        text=message
    )
