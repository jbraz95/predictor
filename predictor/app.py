from file_loader.config_loader import *
from api_calls.general_api_calls import get_actual_value, get_query_actual, get_values
from prediction.regression import get_regression
from prediction.arima import get_arima_forecast
from slack_integration.slackbot import send_image, send_message
from generate_images.image_generator import generate_actual_chart, generate_arima_chart
import time


def check_time(previous_time, time_span):
    actual_time = time.time()
    if actual_time >= (previous_time+time_span):
        return True
    else:
        return False


def monitor(config_file):
    # Variables
    app = get_app(config_file)
    datacenter = get_datacenter(config_file)
    server = get_server(config_file)
    kubernetes_namespace = get_kubernetes_namespace(config_file)
    forecast_time = get_forecast_time(config_file)
    forecast_training_time = get_forecast_training_time(config_file)

    regression_info = get_regression_info(file=config_file)
    for case in regression_info:
        for metric in case:
            print("----------------Name of metric: " + metric + "----------------")

            # Actual value
            query = get_query_actual(app=app, datacenter=datacenter, case=case, metric_to_check=metric,
                                     kubernetes_namespace=kubernetes_namespace)
            actual_value = get_actual_value(server=server, query=query)[1]
            print("The number of tasks is: " + str(actual_value))

            # Regression
            regression = get_regression(server=server, case=case, variable_to_predict=metric, app=app,
                                        datacenter=datacenter, kubernetes_namespace=kubernetes_namespace)
            print("The number of tasks should be: " + str(regression))

            # Prediction
            query = get_query_actual(app=app, datacenter=datacenter, case=case, metric_to_check=metric,
                                     kubernetes_namespace=kubernetes_namespace)
            time_series = get_values(server=server, query=query, minutes=forecast_training_time)
            params = get_params_arima_metric(file=config_file, metric=metric)

            url = generate_actual_chart(timeseries=time_series, name=metric)
            print(url)

            # print(time_series)
            for param in params:
                name = list(param.keys())[0]
                p = param[name]['p']
                d = param[name]['d']
                q = param[name]['q']
                trend = param[name]['trend']

                arima = get_arima_forecast(series=time_series, p=p, d=d, q=q, forecast=forecast_time,
                                           trend=trend)

                if trend == 'nc':
                    print("The next " + str(forecast_time) + " minutes will have these values (no constant): ")
                else:
                    print("The next " + str(forecast_time) + " minutes will have these values (constant): ")
                print(arima)

                url = generate_arima_chart(timeseries=arima, name=metric)
                print(url)


def run():
    previous_time = 0
    config_file = "predictor/configuration.yaml"
    time_span = get_monitoring_time_span(config_file)
    time_span_sleep = get_monitoring_time_span_sleep(config_file)
    token = get_slack_token(config_file)
    channel = get_slack_channel(config_file)

    #send_message(token=token, channel=channel, message="Testing!")
    #send_image(token=token, channel=channel, message="A chart",
    #           image_url="https://upload.wikimedia.org/wikipedia/commons/9/92/Logo_XITE_2017_zwart.png")
    while True:
        if check_time(previous_time, time_span=time_span):
            previous_time = time.time()
            monitor(config_file=config_file)
        else:
            time.sleep(time_span_sleep)
