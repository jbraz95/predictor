import requests


def get_actual_value(server, query):
    response = requests.get(server + '/api/v1/query', params={'query':  query+ "[2m]"})
    metric = response.json()['data']['result'][0]['values']
    if len(metric) > 1:
        metric = metric[1]
    else:
        metric = metric[0]

    return metric
