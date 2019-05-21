from file_loader.config_loader import *
from api_calls.general_api_calls import get_actual_value, get_query_actual
from prediction.regression import get_regression
from prediction.arima import get_arima_forecast


def run():
    # Variables
    config_file = "predictor/configuration.yaml"
    app = get_app(config_file)
    datacenter = get_datacenter(config_file)
    server = get_server(config_file)
    kubernetes_namespace = get_kubernetes_namespace(config_file)

    regression_info = get_regression_info(file=config_file)
    for case in regression_info:
        for metric in case:
            print("Name of metric: " + metric)

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
            prediction = get_arima_forecast()
            print(prediction)
