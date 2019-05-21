import requests


def get_actual_value(server, query):
    response = requests.get(server + '/api/v1/query', params={'query':  query + "[2m]"})
    if len(response.json()['data']['result']) == 0:
        return [0,0]

    metric = response.json()['data']['result'][0]['values']
    if len(metric) > 1:
        metric = metric[1]
    else:
        metric = metric[0]

    return metric


def itct(app, datacenter, case, variable_to_predict):
    task_type = case[variable_to_predict]['task_type']
    metric = case[variable_to_predict]['predict']
    query = metric + '{app=' + app + ',datacenter=' + datacenter + ',task_type="' + task_type + '",force="false"}'
    return query


def tif(app, datacenter, case, variable_to_predict):
    metric = case[variable_to_predict]['predict']
    query = metric + '{app=' + app + ',datacenter=' + datacenter + ',kubernetes_namespace="production-task-manager"}'
    return query


def get_query(app, datacenter, case, variable_to_predict):
    possible_metrics={'incoming_task_count_total' : itct, 'task_in_failure': tif}
    metric = case[variable_to_predict]['predict']
    result = possible_metrics[metric](app=app, datacenter=datacenter, case=case,
                                      variable_to_predict=variable_to_predict)
    return result
