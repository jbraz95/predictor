from api_calls.general_api_calls import get_actual_value, get_query_regression


# Using the model information, it checks all the actual values of the model and it calculates the regression of it to
# know the supposed value.
def get_regression(server, case, variable_to_predict, app, datacenter, kubernetes_namespace):
    prediction = 0
    # For each model
    for model in case[variable_to_predict]["metrics"]:
        # We check the values of all the metrics of the model and we calculate the prediction
        for metric in model:
            query = get_query_regression(app=app, datacenter=datacenter, case=case, variable_to_predict=variable_to_predict,
                                         metric=metric, model=model, kubernetes_namespace=kubernetes_namespace)
            actual_value = float(get_actual_value(server=server, query=query)[1])
            mult = float(model[metric]["value"])
            exp = float(model[metric]["exp"])
            prediction += mult * pow(actual_value, exp)

    prediction += float(case[variable_to_predict]["constant"])
    prediction = round(prediction, 0)
    return prediction
