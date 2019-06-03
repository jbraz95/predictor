import slack


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


