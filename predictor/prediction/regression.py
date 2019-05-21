from api_calls.general_api_calls import get_actual_value, get_query


def get_regression(server, case, variable_to_predict, app, datacenter):
    prediction = 0
    for model in case[variable_to_predict]["metrics"]:
        for metric in model:
            query = get_query(app=app, datacenter=datacenter, case=case, variable_to_predict=variable_to_predict)
            actual_value = float(get_actual_value(server=server, query=query)[1])
            mult = float(model[metric]["value"])
            exp = float(model[metric]["exp"])
            prediction += mult * pow(actual_value, exp)

    prediction += float(case[variable_to_predict]["constant"])
    prediction = round(prediction, 0)
    return prediction
