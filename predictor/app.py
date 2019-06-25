from alarms.alarm_system import check_alarm_percentage, send_alarm, double_check_alarm, double_forecast_check, \
    alarm_forecast, alarm_regression
from file_loader.config_loader import *
from api_calls.general_api_calls import get_actual_value, get_query_actual, get_values
from prediction.regression import get_regression_actual_search, reset_regression
from prediction.arima import get_forecasts_array
from slack_integration.slackbot import read_messages
import time
import threading


# Calculates the difference between previous_time and the actual time and checks if it's bigger than time_span. Also it
# will control if its time to activate the alarm system (because of a temporal disabling) and it will do it if necessary
# previous_time: timestamp of the last monitoring
# time_span: time between checks
# config_file: file with the configuration of the server
# Output: Boolean indicating if the difference of times is bigger than time_span
def check_time(previous_time, time_span, config_file):
    actual_time = time.time()
    paused_time = get_paused_time(config_file)
    alarm_paused = get_alarm_pause_status(config_file, "general")

    if (actual_time >= paused_time) and (paused_time > 0) and alarm_paused:
        modify_pause_alert(config_file, False)
        modify_pause_time(file=config_file, new_value=0)

    if actual_time >= (previous_time+time_span):
        return True
    else:
        return False


# With the information contained in the configuration file, a monitoring is done
# config_file: file with all the configuration for the monitoring
def monitor(config_file):
    # Variables
    app = get_app(config_file)                                                      # App to monitor
    datacenter = get_datacenter(config_file)                                        # Datacenter to monitor
    server = get_server(config_file)                                                # Server to monitor
    kubernetes_namespace = get_kubernetes_namespace(config_file)                    # Namespace of kubernetes to monitor
    token = get_slack_token(config_file)                                            # Slack token
    slack_channel = get_slack_channel(config_file)                                  # Slack channel
    forecast_time = get_forecast_time(config_file)                                  # How much time we forecast
    forecast_training_time = get_forecast_training_time(config_file)                # Time for forecast training
    regression_percentage = get_monitoring_regression_percentage(config_file)       # Max difference in regression
    regression_info = get_regression_info(file=config_file)                         # Regression info

    # We have cases, each one of them having a name (metric)
    for case in regression_info:
        for metric in case:
            print("----------------Name of metric: " + metric + "----------------")

            # We get the query for this metric
            query = get_query_actual(app=app, datacenter=datacenter, case=case, metric_to_check=metric,
                                     kubernetes_namespace=kubernetes_namespace)

            # Actual value
            actual_value = float(get_actual_value(server=server, query=query)[1])
            print("The number of tasks is: " + str(actual_value))

            # If the actual value is small, it will probably mean that a reset was done in the metrics. So we reset our
            # manual errors for the prediction too
            if actual_value < 2:
                print("it feels like there was a reset here")
                reset_regression(config=config_file, metric=metric)

            # Regression
            actual_value_regression = get_regression_actual_search(config=config_file, metric=metric)

            print("The number of tasks should be: " + str(actual_value_regression))

            # If the difference between the regression estimation and the actual value is big, we alert the admins
            if alarm_regression(actual_value=actual_value, calculated_value=actual_value_regression,
                                config_file=config_file):
                problem_text = "The alarm is sent because there is a big difference between the expected value and " \
                               "the current one. Expected: " + str(actual_value_regression) + ". Current value: " \
                               + str(actual_value)
                send_alarm(token=token, channel=slack_channel, metric_name=metric, problem_array=['actual', 'regression'],
                           problem_text=problem_text)

            # Forecast
            time_series = get_values(server=server, query=query, minutes=forecast_training_time)
            params = get_params_arima_metric(file=config_file, metric=metric)
            forecasts = get_forecasts_array(params=params, time_series=time_series, forecast_time=forecast_time)

            # If the forecast grows very fast, we alert the admins
            if alarm_forecast(forecasts=forecasts, config_file=config_file):
                problem_text = "The alarm is sent because the forecast of this metric is growing very fast!"
                send_alarm(token=token, channel=slack_channel, metric_name=metric,
                           problem_array=['actual', 'forecast'], problem_text=problem_text)

            # An alarm that is going to check if there is a big gap between the regression and the actual value, and
            # if the metric is not growing.
            if double_check_alarm(original_value=actual_value, regression_value=actual_value_regression,
                                  regression_percentage=regression_percentage, forecasts=forecasts,
                                  config_file=config_file):
                problem_text = "The alarm is sent because there is a big difference between the expected value and " \
                               "the current one and it doesn't seems like it's going to grow. Expected: " + \
                               str(actual_value_regression) + ". Current value: " + str(actual_value)

                send_alarm(token=token, channel=slack_channel, metric_name=metric,
                           problem_array=['actual', 'forecast', 'regression'], problem_text=problem_text)

            # This alarm will check if both the previous values and the future ones are growing in a fast pace, and
            # alert if this happens
            if double_forecast_check(metric, forecasts, config_file):
                problem_text = "The alarm is sent because the forecast of this metric is growing fast, even faster " \
                               "than previously"
                send_alarm(token=token, channel=slack_channel, metric_name=metric,
                           problem_array=['actual', 'forecast'], problem_text=problem_text)


# We will do a loop monitoring all the metrics indicated in config_file. Each X seconds this will be done, depending
# how is specified in the config_file
def run_prediction(config_file):
    previous_time = 0
    time_span = get_monitoring_time_span(config_file)
    time_span_sleep = get_monitoring_time_span_sleep(config_file)

    try:
        while True:
            if check_time(previous_time, time_span=time_span, config_file=config_file):
                previous_time = time.time()
                monitor(config_file=config_file)
            else:
                time.sleep(time_span_sleep)
    except Exception as e:
        print("error prediction" + e)
        time.sleep(time_span_sleep)
        pred = threading.Thread(target=run_prediction, args=(config_file,))
        pred.start()


# We start the slack bot
def run_slack(config_file):
    try:
        token = get_slack_token(config_file)
        read_messages(token=token)
    except Exception as e:
        print("error slack " + e)
        run_slack(config_file)


# We start the program. We create an independent thread that will monitor the metrics and we start reading messages in
# slack
def run():
    try:
        config_file = "predictor/configuration.yaml"
        pred = threading.Thread(target=run_prediction, args=(config_file, ))
        pred.start()
        run_slack(config_file=config_file)
    except Exception as e:
        print("Error: unable to start thread")
        print(e)
