from api_calls.general_api_calls import get_actual_value


def get_regression_bad(server, query_list, model_list):
    prediction = 0
    index = 0

    for variable in query_list:
        multiplier = model_list[index][0]
        exp = model_list[index][1]
        actual_value = float(get_actual_value(server=server, query=variable)[1])
        prediction += multiplier * pow(actual_value, exp)
        index += 1

    prediction += model_list[index][0]
    prediction = round(prediction, 0)
    return prediction


def get_regression(server, case, variable_to_predict, app, datacenter):
    task = case[variable_to_predict]["task_type"]
    prediction = 0
    for model in case[variable_to_predict]["metrics"]:
        for metric in model:
            task_type = model[metric]["task_type"]
            query = metric + '{app=' + app + ',datacenter=' + datacenter + ',task_type="' + task + \
                    '",event_type="' + task_type + '"}'
            actual_value = float(get_actual_value(server=server, query=query)[1])
            mult = float(model[metric]["value"])
            exp = float(model[metric]["exp"])
            prediction += mult * pow(actual_value, exp)

    prediction += float(case[variable_to_predict]["constant"])
    prediction = round(prediction, 0)
    return prediction
