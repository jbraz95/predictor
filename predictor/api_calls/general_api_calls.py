import requests


# Giving a server and a query, it gets you the actual value of the query
# Server: the server where we have to query
# Query: The query to be executed
from file_loader.config_loader import get_app, get_datacenter, get_kubernetes_namespace, get_regression_info


def get_actual_value(server, query):
    response = requests.get(server + '/api/v1/query', params={'query': query + "[2m]"})
    if len(response.json()['data']['result']) == 0:
        return [0, 0]

    metric = response.json()['data']['result'][0]['values']
    if len(metric) > 1:
        metric = metric[1]
    else:
        metric = metric[0]

    return metric


# Giving a server, a query and the number of minutes you want to get, it gets you the timeseries of the query
# Server: the server where we have to query
# Query: The query to be executed
# Minutes: Time in minutes that we want to get
def get_values(server, query, minutes):
    time_range = "["+str(minutes)+"m]"
    response = requests.get(server + '/api/v1/query', params={'query': query + time_range})

    if len(response.json()['data']['result']) == 0:
        return [[0, 0]]

    metric = response.json()['data']['result'][0]['values']

    return metric


# Gives you a query for knowing the actual value of incoming task count total
# app: the name of the app
# datacenter: the name of the datacenter
# case: all the information about the metric to check (filters)
# metric_to_check: metric that we want to study (for example incoming_task_count_total-FUBO)
# namespace = kubernetes information to do the query
def itct_actual(app, datacenter, case, metric_to_check, kubernetes_namespace):
    task_type = case[metric_to_check]['task_type']
    metric = case[metric_to_check]['predict']
    query = metric + '{app=' + app + ',datacenter=' + datacenter + ',kubernetes_namespace=' + kubernetes_namespace + \
            ',task_type="' + task_type + '",force="false"} '
    return query


# Gives you a query for knowing the actual value of forced incoming task count total
# app: the name of the app
# datacenter: the name of the datacenter
# case: all the information about the metric to check (filters)
# metric_to_check: metric that we want to study (for example incoming_task_count_total-FUBO)
# namespace = kubernetes information to do the query
def itct_actual_forced(app, datacenter, case, metric_to_check, kubernetes_namespace):
    task_type = case[metric_to_check]['task_type']
    metric = case[metric_to_check]['predict']
    query = metric + '{app=' + app + ',datacenter=' + datacenter + ',kubernetes_namespace=' + kubernetes_namespace + \
            ',task_type="' + task_type + '",force="true"} '
    return query


# Gives you a query for knowing the actual value of task in failure
# app: the name of the app
# datacenter: the name of the datacenter
# case: information about the metric to check (filters)
# metric_to_check: metric that we want to study (for example incoming_task_count_total-FUBO)
# namespace = kubernetes information to do the query
def tif_actual(app, datacenter, case, metric_to_check, kubernetes_namespace):
    metric = case[metric_to_check]['predict']
    query = metric + '{app=' + app + ',datacenter=' + datacenter + ',kubernetes_namespace=' + kubernetes_namespace + '}'
    return query


# Depending the metric to check, it gives you the query to know its actual value
# app: the name of the app
# datacenter: the name of the datacenter
# case: information about the metric to check (filters)
# metric_to_check: metric that we want to study (for example incoming_task_count_total-FUBO)
# namespace = kubernetes information to do the query
def get_query_actual(app, datacenter, case, metric_to_check, kubernetes_namespace):
    possible_metrics = {'incoming_task_count_total': itct_actual, 'task_in_failure': tif_actual}
    metric = case[metric_to_check]['predict']
    result = possible_metrics[metric](app=app, datacenter=datacenter, case=case,
                                      metric_to_check=metric_to_check, kubernetes_namespace=kubernetes_namespace)
    return result


def get_query_actual_search(config, metric):
    regression_info = get_regression_info(config)
    for case in regression_info:
        for metric_case in case:
            if metric_case == metric:
                case_selected = case

    app = get_app(config)
    datacenter = get_datacenter(config)
    kubernetes_namespace = get_kubernetes_namespace(config)

    return get_query_actual(app=app, datacenter=datacenter, case=case_selected, metric_to_check=metric,
                            kubernetes_namespace=kubernetes_namespace)


# Gives you a query for knowing the actual value of one of the values related to the incoming task count total model
# app: the name of the app
# datacenter: the name of the datacenter
# case: information about the metric to check (filters)
# variable_to_predict: metric that we want to predict
# metric: metric from the model to study
# model: model containing metrics that will predict variable_to_predict
# namespace = kubernetes information to do the query
def itct_query_regression(app, datacenter, case, variable_to_predict, metric, model, kubernetes_namespace):
    task_type = case[variable_to_predict]['task_type']
    event_type = model[metric]['event_type']
    query = metric + '{app=' + app + ',datacenter=' + datacenter + ',kubernetes_namespace=' + kubernetes_namespace + \
            ',task_type="' + task_type + '",event_type="' + event_type + '"}'
    return query


# Gives you a query for knowing the actual value of one of the values related to the task in failure model
# app: the name of the app
# datacenter: the name of the datacenter
# case: information about the metric to check (filters)
# variable_to_predict: metric that we want to predict
# metric: metric from the model to study
# model: model containing metrics that will predict variable_to_predict
# namespace = kubernetes information to do the query
def tif_query_regression(app, datacenter, case, variable_to_predict, metric, model, kubernetes_namespace):
    task_type = case[variable_to_predict]['task_type']
    event_type = model[metric]['event_type']
    query = metric + '{app=' + app + ',datacenter=' + datacenter + ',task_type="' + task_type + '",event_type="' + \
            event_type + '",kubernetes_namespace=' + kubernetes_namespace + '}'
    return query


# Depending the metric to predict, it gives you the query to check the actual value of one of the values related to the
# regression model
# app: the name of the app
# datacenter: the name of the datacenter
# case: information about the metric to check (filters)
# variable_to_predict: metric that we want to predict
# metric: metric from the model to study
# model: model containing metrics that will predict variable_to_predict
# namespace = kubernetes information to do the query
def get_query_regression(app, datacenter, case, variable_to_predict, metric, model, kubernetes_namespace):
    possible_metrics = {'incoming_task_count_total': itct_query_regression, 'task_in_failure': tif_query_regression}
    metric_to_predict = case[variable_to_predict]['predict']
    result = possible_metrics[metric_to_predict](app=app, datacenter=datacenter, case=case,
                                                 variable_to_predict=variable_to_predict, metric=metric, model=model,
                                                 kubernetes_namespace=kubernetes_namespace)
    return result


# It adapt the time series to a more easy to use format
# series: timeseries to be adapted
def adapt_time_series(series):
    value_series = []
    time_series = []
    for time, value in series:
        value_series.append(int(value))
        time_series.append(float(time))
    return [time_series, value_series]
