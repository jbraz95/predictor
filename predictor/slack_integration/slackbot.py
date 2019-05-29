import slack


def run_bot(token, channel):
    client = slack.WebClient(token)
    client.chat_postMessage(
        channel=channel,
        text='Sending message!'
    )
