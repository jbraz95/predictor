from file_loader.config_loader import get_alarm_pause_status
from slack_integration.slackbot import send_image, send_message, get_url_image


def check_alarm_percentage(new_value, original_value, percentage_change, config_file):
    alarm_paused = get_alarm_pause_status(config_file)

    if original_value == 0:
        percentage = 0
    else:
        increase = new_value - original_value
        percentage = (increase / original_value)

    print("The difference between the new value and the original one is: " + str(percentage))

    if (abs(percentage) > percentage_change) and not alarm_paused:
        return True
    else:
        return False


def send_alarm(token, channel, metric_name, problem_array, problem_text):
    url = get_url_image(arrays_to_get=problem_array, metric=metric_name)

    message = "Hi! It seems that there is an anomaly in " + metric_name + '.\n' + problem_text

    send_message(token=token, channel=channel, message=message)
    send_image(token=token, channel=channel, message=metric_name, image_url=url)
    return 1
