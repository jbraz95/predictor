from file_loader.config_loader import *
from api_calls.general_api_calls import get_actual_value, get_query
from prediction.regression import get_regression


def run():
    # Variables
    config_file = "predictor/configuration.yaml"
    app = get_app(config_file)
    datacenter = get_datacenter(config_file)
    server = get_server(config_file)

    regression_info = get_regression_info(file=config_file)
    for case in regression_info:
        for variable_to_predict in case:
            print("Name of metric: " + variable_to_predict)

            # Prediction
            regression = get_regression(server=server, case=case, variable_to_predict=variable_to_predict, app=app,
                                        datacenter=datacenter)
            print("The number of tasks should be: " + str(regression))

            # Actual value
            query = get_query(app=app, datacenter=datacenter, case=case, variable_to_predict=variable_to_predict)
            actual_value = get_actual_value(server=server, query=query)[1]
            print("The number of tasks is: " + str(actual_value))
