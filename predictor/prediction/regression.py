from api_calls.general_api_calls import get_actual_value, get_query_regression, itct_actual_forced, get_values, \
                                        adapt_time_series


# Using the model information, it checks all the actual values of the model and it calculates the regression of it to
# know the supposed value.
def get_regression(server, case, variable_to_predict, app, datacenter, kubernetes_namespace):
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

    prediction += float(case[variable_to_predict]["constant"])
    query_forced = itct_actual_forced(app=app, datacenter=datacenter, case=case, metric_to_check=variable_to_predict,
                                      kubernetes_namespace=kubernetes_namespace)
    forced_cases = float(get_actual_value(server=server, query=query_forced)[1])
    prediction -= forced_cases

    if prediction < 0:
        prediction = 0

    prediction = round(prediction, 0)
    return prediction


def get_regression_array(server, case, variable_to_predict, app, datacenter, kubernetes_namespace, time):
    prediction = [0] * time
    # For each model
    for model in case[variable_to_predict]["metrics"]:
        # We check the values of all the metrics of the model and we calculate the prediction
        for metric in model:
            query = get_query_regression(app=app, datacenter=datacenter, case=case,
                                         variable_to_predict=variable_to_predict, metric=metric, model=model,
                                         kubernetes_namespace=kubernetes_namespace)
            values = adapt_time_series(get_values(server, query, time))[1]

            exp = float(model[metric]["exp"])
            powered = [n**exp for n in values]
            mult = float(model[metric]["value"])

            actual_prediction = [i * mult for i in powered]
            if len(actual_prediction) < time:
                last_value = actual_prediction[len(actual_prediction)-1]
                actual_prediction += [last_value] * (time-len(actual_prediction))

            prediction = [new + old for new, old in zip(actual_prediction, prediction)]

    constant = float(case[variable_to_predict]["constant"])
    prediction = [i + constant for i in prediction]

    query_forced = itct_actual_forced(app=app, datacenter=datacenter, case=case, metric_to_check=variable_to_predict,
                                      kubernetes_namespace=kubernetes_namespace)
    forced_cases = adapt_time_series(get_values(server=server, query=query_forced, minutes=time))[1]
    if len(forced_cases) < time:
        last_value = forced_cases[len(forced_cases) - 1]
        forced_cases += [last_value] * (time - len(forced_cases))

    prediction = [pred - forced for pred, forced in zip(prediction, forced_cases)]

    #if prediction < 0:
    #    prediction = 0

    prediction = [round(pred) for pred in prediction]
    return prediction

