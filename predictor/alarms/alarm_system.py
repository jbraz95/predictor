from file_loader.config_loader import get_alarm_pause_status, get_alarm_minimum_difference
from slack_integration.slackbot import send_image, send_message
from generate_images.image_generator import get_url_image


def check_alarm_percentage(actual_value, calculated_value, percentage_change, config_file):
    alarm_paused = get_alarm_pause_status(config_file)
    min_diff = get_alarm_minimum_difference(config_file)

    if calculated_value == 0:
        percentage = 0
    else:
        increase = actual_value - calculated_value
        percentage = (increase / calculated_value)

    difference = abs(actual_value - calculated_value)

    print("The difference between the new value and the original one is: " + str(percentage))

    if (abs(percentage) > percentage_change) and (difference > min_diff) and (not alarm_paused):
        return True
    else:
        return False


def double_check_alarm(original_value, regression_value, regression_percentage, forecasts, config_file):
    regression_anomaly = check_alarm_percentage(actual_value=original_value, calculated_value=regression_value,
                                                percentage_change=regression_percentage, config_file=config_file)

    forecast_anomaly = False
    for forecast in forecasts:
        min_forecast = min(forecast[1])
        max_forecast = max(forecast[1])
        if (abs(max_forecast) - abs(min_forecast)) == 0:
            forecast_anomaly = True

    if regression_anomaly and forecast_anomaly:
        return True
    else:
        return False


def send_alarm(token, channel, metric_name, problem_array, problem_text):
    url = get_url_image(arrays_to_get=problem_array, metric=metric_name)

    message = "Hi! It seems that there is an anomaly in " + metric_name + '.\n' + problem_text

    send_message(token=token, channel=channel, message=message)
    send_image(token=token, channel=channel, message=metric_name, image_url=url)
    return 1
