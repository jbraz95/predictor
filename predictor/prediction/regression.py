from api_calls.general_api_calls import get_actual_value


def get_prediction(server, query_list, model_list):
    prediction = 0
    index = 0

    for variable in query_list:
        multiplier = model_list[index][0]
        exp = model_list[index][1]
        actual_value = int(get_actual_value(server=server, query=variable)[1])
        prediction += multiplier * pow(actual_value, exp)
        index += 1

    prediction += model_list[index][0]
    prediction = round(prediction, 0)
    return prediction
