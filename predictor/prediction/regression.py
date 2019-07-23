from api.general_api_calls import get_actual_value, get_query_regression, itct_actual_forced_query, get_values, \
    adapt_time_series, get_query_actual_search
from file_loader.config_loader import get_server, get_app, get_datacenter, get_kubernetes_namespace, \
    get_monitoring_time_span, get_regression_info, modify_manual_error


# Using the model information, it checks all the actual values of the model and it calculates the regression of it to
# know the supposed value.
# Server: Where to do the regression
# Case: information about the metric to check (filters)
# variable_to_predict: metric that we want to predict
# app: the app to check
# datacenter: the datacenter to check
# kubernetes_namespace = kubernetes information to do the query
# Output: the expected actual value (only one value, not an array)
def get_regression_actual(server, case, variable_to_predict, app, datacenter, kubernetes_namespace):
    prediction = 0
    # For each model
    for model in case[variable_to_predict]["metrics"]:
        # We check the values of all the metrics of the model and we calculate the prediction
        for metric in model:
            query = get_query_regression(app=app, datacenter=datacenter, case=case,
                                         variable_to_predict=variable_to_predict, metric=metric, model=model,
                                         kubernetes_namespace=kubernetes_namespace)
            actual_value = float(get_actual_value(server=server, query=query)[1])
            mult = float(model[metric]["value"])
            exp = float(model[metric]["exp"])
            prediction += mult * pow(actual_value, exp)

    # We get the information of forced queries (done manually) and we remove them from the prediction (as they are
    # not related to the model)
    prediction += float(case[variable_to_predict]["constant"])
    query_forced = itct_actual_forced_query(app=app, datacenter=datacenter, case=case, metric_to_check=variable_to_predict,
                                            kubernetes_namespace=kubernetes_namespace)
    forced_cases = float(get_actual_value(server=server, query=query_forced)[1])
    prediction -= forced_cases

    # We add the manual error (added to reset the variable)
    prediction += float(case[variable_to_predict]["manual_error"])

    if prediction < 0:
        prediction = 0

    prediction = round(prediction, 0)
    return prediction


# This function will get you the supposed value of a metric without the need to search all the information of other
# functions
# Config: the configuration file to search information of the metric
# Metric: the name of the metric
# Output: the expected actual value (only one value, not an array)
def get_regression_actual_search(config, metric):
    server = get_server(config)
    regression_info = get_regression_info(config)
    for case in regression_info:
        for metric_case in case:
            if metric_case == metric:
                case_selected = case

    app = get_app(config)
    datacenter = get_datacenter(config)
    kubernetes_namespace = get_kubernetes_namespace(config)

    return get_regression_actual(server=server, case=case_selected, variable_to_predict=metric, app=app,
                                 datacenter=datacenter, kubernetes_namespace=kubernetes_namespace)


# Using the model information, it checks all the values of the model and it calculates the regression of it to
# know the supposed values in the last "time" minutes
# Server: Where to do the regression
# Case: information about the metric to check (filters)
# variable_to_predict: metric that we want to predict
# app: the app to check
# datacenter: the datacenter to check
# kubernetes_namespace = kubernetes information to do the query
# time: how many minutes in the past you are going to check
# Output: an array with the last "time" minutes of expected values
def get_regression_array(server, case, variable_to_predict, app, datacenter, kubernetes_namespace, time):
    prediction = [0] * time
    # For each model
    for model in case[variable_to_predict]["metrics"]:
        # We check all the metrics of the model and we calculate the prediction
        for metric in model:
            query = get_query_regression(app=app, datacenter=datacenter, case=case,
                                         variable_to_predict=variable_to_predict, metric=metric, model=model,
                                         kubernetes_namespace=kubernetes_namespace)
            values = adapt_time_series(get_values(server, query, time))[1]

            # We multiply the values according to the model
            exp = float(model[metric]["exp"])
            powered = [n**exp for n in values]
            mult = float(model[metric]["value"])
            actual_prediction = [i * mult for i in powered]

            # if the prediction is smaller than requested, we extend it taking the last value
            if len(actual_prediction) < time:
                last_value = actual_prediction[len(actual_prediction)-1]
                actual_prediction += [last_value] * (time-len(actual_prediction))

            # we add this metric to the previous ones
            prediction = [new + old for new, old in zip(actual_prediction, prediction)]

    # We add the constant of the model and the manual error to the prediction
    constant = float(case[variable_to_predict]["constant"])
    manual_error = float(case[variable_to_predict]["manual_error"])
    prediction = [i + constant + manual_error for i in prediction]

    # We remove the forced cases to the prediction as they are not related to the model
    query_forced = itct_actual_forced_query(app=app, datacenter=datacenter, case=case, metric_to_check=variable_to_predict,
                                            kubernetes_namespace=kubernetes_namespace)
    forced_cases = adapt_time_series(get_values(server=server, query=query_forced, minutes=time))[1]

    if len(forced_cases) < time:
        last_value = forced_cases[len(forced_cases) - 1]
        forced_cases += [last_value] * (time - len(forced_cases))

    prediction = [pred - forced for pred, forced in zip(prediction, forced_cases)]

    prediction = [round(pred) for pred in prediction]
    return prediction


# This function will get you the supposed values of a metric without the need to search all the information of other
# functions
# Config: the configuration file to search information of the metric
# Metric: the name of the metric
# Output: the expected values (An array)
def get_regression_array_search(config, metric):
    server = get_server(config)
    regression_info = get_regression_info(config)
    for case in regression_info:
        for metric_case in case:
            if metric_case == metric:
                case_selected = case

    app = get_app(config)
    datacenter = get_datacenter(config)
    kubernetes_namespace = get_kubernetes_namespace(config)
    time = get_monitoring_time_span(config)

    return get_regression_array(server=server, case=case_selected, variable_to_predict=metric, app=app, datacenter=datacenter,
                                kubernetes_namespace=kubernetes_namespace, time=time)


# When there is an anomaly and it has been fixed, we have to reset the regression. To do so, we add a manual error to
# the regression.
# config: file with the configuration
# metric: name of the metric to reset
# output: the difference to reset the metric
def reset_regression(config, metric):
    modify_manual_error(config, metric, 0)
    actual_regression = get_regression_actual_search(config, metric)
    actual_query = get_query_actual_search(config, metric)
    server = get_server(config)
    actual_value = float(get_actual_value(server, actual_query)[1])

    difference = actual_value - actual_regression

    modify_manual_error(config, metric, difference)

    return difference
