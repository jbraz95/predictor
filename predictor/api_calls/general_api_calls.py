import requests


def get_actual_value(server, metric, filters):
    response = requests.get(server + '/api/v1/query', params={'query': metric + filters + "[2m]"})
    metric = response.json()['data']['result'][0]['values']

    if len(metric) > 1:
        metric = metric[1]

    return metric
