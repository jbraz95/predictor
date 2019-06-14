from alarms.alarm_system import check_alarm_percentage, send_alarm
from file_loader.config_loader import *
from api_calls.general_api_calls import get_actual_value, get_query_actual, get_values
from prediction.regression import get_regression_actual
from prediction.arima import get_forecast_array
from slack_integration.slackbot import read_messages
import time
import threading


# Check the time to know if we have to do a monitoring
# previous_time: timestamp of the last monitoring
# time_span: time between checks
def check_time(previous_time, time_span):
    actual_time = time.time()
    if actual_time >= (previous_time+time_span):
        return True
    else:
        return False


# With the information contained in the configuration file, a monitoring is done
# config_file: file with all the configuration for the monitoring
def monitor(config_file):
    # Variables
    app = get_app(config_file)
    datacenter = get_datacenter(config_file)
    server = get_server(config_file)
    kubernetes_namespace = get_kubernetes_namespace(config_file)
    token = get_slack_token(config_file)
    slack_channel = get_slack_channel(config_file)
    forecast_time = get_forecast_time(config_file)
    forecast_training_time = get_forecast_training_time(config_file)
    forecast_percentage = get_monitoring_forecast_percentage(config_file)
    regression_percentage = get_monitoring_regression_percentage(config_file)
    regression_info = get_regression_info(file=config_file)

    for case in regression_info:
        for metric in case:
            print("----------------Name of metric: " + metric + "----------------")

            query = get_query_actual(app=app, datacenter=datacenter, case=case, metric_to_check=metric,
                                     kubernetes_namespace=kubernetes_namespace)

            # Actual value
            actual_value = float(get_actual_value(server=server, query=query)[1])
            print("The number of tasks is: " + str(actual_value))

            manual_error = get_manual_error(config_file, metric)
            print("The manual error is: " + str(manual_error))

            print("The number of tasks with the manual error is: " + str(actual_value+manual_error))

            # Regression
            actual_value_regression = get_regression_actual(server=server, case=case, variable_to_predict=metric,
                                                            app=app, datacenter=datacenter,
                                                            kubernetes_namespace=kubernetes_namespace)
            print("The number of tasks should be: " + str(actual_value_regression))
            if check_alarm_percentage(actual_value, actual_value_regression, regression_percentage, config_file):
                problem_text = "The alarm is sent because there is a big difference between the expected value and " \
                               "the current one. Expected: " + str(actual_value_regression) + ". Current value: " \
                               + str(actual_value)
                send_alarm(token=token, channel=slack_channel, metric_name=metric, problem_array=['actual', 'regression'],
                           problem_text=problem_text)

            # Forecast
            time_series = get_values(server=server, query=query, minutes=forecast_training_time)
            params = get_params_arima_metric(file=config_file, metric=metric)
            forecasts = get_forecast_array(params=params, time_series=time_series, forecast_time=forecast_time)

            forecast_alarm = False
            for forecast in forecasts:
                if forecast[0] == 'nc':
                    print("The next " + str(forecast_time) + " minutes will have these values (no constant): ")
                else:
                    print("The next " + str(forecast_time) + " minutes will have these values (constant): ")
                print(forecast[1])

                max_forecast = max(forecast[1])
                min_forecast = min(forecast[1])
                if check_alarm_percentage(new_value=max_forecast, original_value=min_forecast,
                                          percentage_change=forecast_percentage, config_file=config_file):
                    forecast_alarm = True
            if forecast_alarm:
                problem_text = "The alarm is sent because the forecast of this metric is growing very fast!"
                send_alarm(token=token, channel=slack_channel, metric_name=metric, problem_array=['actual', 'forecast'],
                           problem_text=problem_text)


def run_prediction(config_file):
    previous_time = 0
    time_span = get_monitoring_time_span(config_file)
    time_span_sleep = get_monitoring_time_span_sleep(config_file)

    while True:
        if check_time(previous_time, time_span=time_span):
            previous_time = time.time()
            monitor(config_file=config_file)
        else:
            time.sleep(time_span_sleep)


def run_slack(config_file):
    try:
        token = get_slack_token(config_file)
        read_messages(token=token)
    except Exception as e:
        print(e)


def run():
    try:
        config_file = "predictor/configuration.yaml"
        pred = threading.Thread(target=run_prediction, args=(config_file, ))
        pred.start()
        run_slack(config_file=config_file)
    except Exception as e:
        print("Error: unable to start thread")
        print(e)
