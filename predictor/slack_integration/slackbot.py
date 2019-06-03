import asyncio
import time
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


def read_messages(token, channel):
    @slack.RTMClient.run_on(event='message')
    def say_hello(**payload):
        data = payload['data']
        print(data)
        if 'Hello' in data['text']:
            channel_id = data.get("channel")
            user = data.get("user")

            webclient = payload['web_client']
            webclient.chat_postMessage(
                channel=channel_id,
                text="Hi <@{}>!".format(user)
            )

    print("pre running")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    rtm_client = slack.RTMClient(token=token, run_async=True, loop=loop)
    loop.run_until_complete(rtm_client.start())
