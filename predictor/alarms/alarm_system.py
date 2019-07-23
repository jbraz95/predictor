from api.general_api_calls import get_query_actual_search, get_values, adapt_time_series
from file_loader.config_loader import get_alarm_pause_status, get_alarm_minimum_difference, get_forecast_time, \
    get_monitoring_forecast_percentage, get_server, get_monitoring_regression_percentage, \
    get_monitoring_forecast_percentage_nc
from slack_integration.slackbot import send_image, send_message
from generate_images.image_generator import get_url_image


# Calculates the percentage of how much a has increased over b
def calculate_percentage(a, b):
    if b != 0:
        return (a - b)/b
    else:
        return a


# If the alerts are activated, it will check if the difference between the two values(actual_value and calculated_value)
# are bigger than the minimum difference and if the percentage increase is bigger than percentage_change,
# and if so return a True boolean
# actual_value = the actual value
# calculated_value = the calculated value
# percentage_change = maximum difference in percentage between actual_value and calculated_value (p.e. 20%)
# config_file = configuration file for the rest of parameters
# output: a boolean indicating if there is an alarm or not
def check_alarm_percentage(actual_value, calculated_value, percentage_change, min_diff):

    percentage = calculate_percentage(actual_value, calculated_value)

    # We also want to see what is the numerical difference between 2 values. The difference between 4 and 5 is a 25%
    # but it will not be an anomaly.
    difference_number = abs(actual_value - calculated_value)

    print("The difference between the new value and the original one is: " + str(percentage))

    if (abs(percentage) > percentage_change) and (difference_number > min_diff):
        return True
    else:
        return False


# An alarm to study if the difference between the expected value and the actual value is very different
# actual_value: the actual value of the metric
# calculated_value: the expected value calculated by the regressive model
# output: a boolean indicating if there is an alarm or not
def alarm_regression(actual_value, calculated_value, config_file):
    alarm_paused = get_alarm_pause_status(config_file, "regression")

    if not alarm_paused:
        regression_percentage = get_monitoring_regression_percentage(config_file)
        min_diff = get_alarm_minimum_difference(config_file)

        alarm = check_alarm_percentage(actual_value=actual_value, calculated_value=calculated_value,
                                          percentage_change=regression_percentage, min_diff=min_diff)

        return alarm
    else:
        return False


# An alarm to study if the forecast is giving a trend that is growing faster than indicated in the configuration file.
# We will get both forecasts, with constant(c) and without(nc), and if C is growing too fast we will send a True
# boolean.
# forecasts: set of forecast (with and without constant) for a metric
# config_file: file with all the parameters and configurations
# mode: for what forecast they trigger
#       c -> constant forecast
#       nc -> No constant forecast
#       both -> Both forecast
#       any -> Any forecast
# output: a boolean indicating if there is an alarm or not
def alarm_forecast(forecasts, config_file, mode):
    alarm_paused = get_alarm_pause_status(config_file, "forecast")

    if not alarm_paused:
        forecast_time = get_forecast_time(config_file)                                  # How much time we forecast
        if mode == "nc":
            forecast_percentage = get_monitoring_forecast_percentage_nc(config_file)  # Max increase in forecast
        else:
            forecast_percentage = get_monitoring_forecast_percentage(config_file)  # Max increase in forecast


        alarm = True
        for forecast in forecasts:
            #if forecast[0] == 'nc':
                #print("The next " + str(forecast_time) + " minutes will have these values (no constant): ")
            #else:
                #print("The next " + str(forecast_time) + " minutes will have these values (constant): ")

            if mode == 'any':
                max_forecast = max(forecast[1])
                min_forecast = min(forecast[1])
                if check_alarm_percentage(actual_value=max_forecast, calculated_value=min_forecast,
                                          percentage_change=forecast_percentage, min_diff=0):
                    alarm = alarm or True
                else:
                    alarm = alarm or False
            elif (forecast[0] == mode) or (mode == 'both'):
                max_forecast = max(forecast[1])
                min_forecast = min(forecast[1])
                if check_alarm_percentage(actual_value=max_forecast, calculated_value=min_forecast,
                                          percentage_change=forecast_percentage, min_diff=0):
                    alarm = alarm and True
                else:
                    alarm = alarm and False

            # print(forecast[1])

        return alarm
    else:
        return False


# Alarm that is going to check if there is an anomaly in the regression and in the forecast, and if both are true then
# it will output a True boolean.
# Original_value = actual value of the metric
# regression_value = calculated value in the regression
# forecasts = sets of forecasts of the metric (constant and no constants)
# config_file = file with all extra info for configuration
# mode: for what forecast they trigger
#       c -> constant forecast
#       nc -> No constant forecast
#       both -> Both forecast
#       any -> Any of the two
# output: a boolean indicating if there is an alarm or not
def double_check_alarm(original_value, regression_value, forecasts, config_file, mode):
    alarm_paused = get_alarm_pause_status(config_file, "double_check")
    regression_percentage = get_monitoring_regression_percentage(config_file)

    if not alarm_paused:
        min_diff = get_alarm_minimum_difference(config_file)

        regression_anomaly = check_alarm_percentage(actual_value=original_value, calculated_value=regression_value,
                                                    percentage_change=regression_percentage, min_diff=min_diff)

        forecast_anomaly = True
        for forecast in forecasts:
            if mode == 'any':
                max_forecast = max(forecast[1])
                min_forecast = min(forecast[1])
                if check_alarm_percentage(actual_value=max_forecast, calculated_value=min_forecast,
                                          percentage_change=forecast_percentage, min_diff=0):
                    alarm = alarm or True
                else:
                    alarm = alarm or False
            elif(forecast[0] == mode) or (mode == 'both'):
                min_forecast = min(forecast[1])
                max_forecast = max(forecast[1])
                if (abs(max_forecast) - abs(min_forecast)) == 0:
                    forecast_anomaly = forecast_anomaly and True
                else:
                    forecast_anomaly = forecast_anomaly and False

        if regression_anomaly and forecast_anomaly:
            return True
    else:
        return False


# Alarm that double checks the forecast. See if during the past the metric has been growing fast and also sees if the
# forecast predicts to do the same in the next minutes. If so, returns a True Boolean
# Metric: the metric to study
# forecasts: the forecasts of the metric
# config_file: the file with the configuration and extra information
# mode: for what forecast they trigger
#       c -> constant forecast
#       nc -> No constant forecast
#       both -> Both forecast
#       any -> Any forecast
# output: a boolean indicating if there is an alarm or not
def double_forecast_check(metric, forecasts, config_file, mode):
    alarm_paused = get_alarm_pause_status(config_file, "double_forecast")

    if not alarm_paused:
        forecast_percentage = get_monitoring_forecast_percentage(config_file)
        forecast_time = get_forecast_time(config_file)
        server = get_server(config_file)
        query = get_query_actual_search(metric=metric, config=config_file)

        actual_values = adapt_time_series(get_values(server, query, forecast_time))
        max_actual = max(actual_values[1])
        min_actual = min(actual_values[1])
        difference_actual = calculate_percentage(max_actual, min_actual)

        if difference_actual > forecast_percentage:
            forecast_anomaly = True
            for forecast in forecasts:
                if mode == 'any':
                    max_forecast = max(forecast[1])
                    min_forecast = min(forecast[1])
                    if check_alarm_percentage(actual_value=max_forecast, calculated_value=min_forecast,
                                              percentage_change=forecast_percentage, min_diff=0):
                        alarm = alarm or True
                    else:
                        alarm = alarm or False
                elif (forecast[0] == mode) or (mode == 'both'):
                    min_forecast = min(forecast[1])
                    max_forecast = max(forecast[1])
                    difference_forecast = calculate_percentage(max_forecast, min_forecast)

                    if difference_forecast >= difference_actual:
                        forecast_anomaly = forecast_anomaly and True
                    else:
                        forecast_anomaly = forecast_anomaly and False

            if forecast_anomaly:
                return True
    else:
        return False


# This function sends an alarm with a graph that shows the anomaly
# token: slack token
# channel: to which channel you send the alarm
# metric_name: name of the metric with an anomaly
# problem_array: array with the graphs that have to be sent (actual, regression and/or forecast)
# problem_text: text describing the anomaly.
def send_alarm(token, channel, metric_name, problem_array, problem_text):
    url = get_url_image(arrays_to_get=problem_array, metric=metric_name)

    message = "Hi! It seems that there is an anomaly in " + metric_name + '.\n' + problem_text

    send_message(token=token, channel=channel, message=message)
    send_image(token=token, channel=channel, message=metric_name, image_url=url)
    return 1
