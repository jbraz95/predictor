import sys

import yaml


def load_file(file):
    try:
        with open(file, 'r') as yamlfile:
            config = yaml.safe_load(yamlfile)
            return config
    except yaml.parser.ParserError:
        print("Oops!", sys.exc_info()[0], "occured.")


def write_file(file, file_doc):
    try:
        with open(file, 'w') as f:
            yaml.dump(file_doc, f)
    except yaml.parser.ParserError:
        print("Oops!", sys.exc_info()[0], "occured.")


def modify_pause_alert(file, new_value):
    file_doc = load_file(file)

    file_doc["alerting"]["paused"] = new_value

    write_file(file, file_doc)


def modify_pause_time(file, new_value):
    file_doc = load_file(file)

    file_doc["alerting"]["paused_time"] = new_value

    write_file(file, file_doc)


def modify_manual_error(file, metric, value):
    file_doc = load_file(file)

    regression_info = file_doc["regression"]

    index = -1

    for metric_info in regression_info:
        index += 1
        for metric_name in metric_info:
            if metric_name == metric:
                file_doc["regression"][index][metric_name]["manual_error"] = value

    write_file(file, file_doc)


def get_manual_error(file, metric):
    file_doc = load_file(file)
    regression_info = file_doc["regression"]
    index = -1

    for metric_info in regression_info:
        index += 1
        for metric_name in metric_info:
            if metric_name == metric:
                value = file_doc["regression"][index][metric_name]["manual_error"]

    return value


def get_server(file):
    return load_file(file)["server"]["url"]


def get_slack_token(file):
    return load_file(file)["slack"]["token"]


def get_monitoring_regression_percentage(file):
    return float(load_file(file)["alerting"]["regression_percentage"])


def get_monitoring_forecast_percentage(file):
    return float(load_file(file)["alerting"]["forecast_percentage"])

def get_monitoring_forecast_percentage_nc(file):
    return float(load_file(file)["alerting"]["forecast_percentage_nc"])


def get_alarm_pause_status(file, alert):
    general = bool(load_file(file)["alerting"]["paused"])

    if alert is "general":
        return general
    else:
        return general or bool(load_file(file)["alerting"]["alerts_paused"][alert])


def get_paused_time(file):
    return float(load_file(file)["alerting"]["paused_time"])


def get_alarm_minimum_difference_regression(file):
    return int(load_file(file)["alerting"]["regression_min_difference"])


def get_alarm_maximum_difference_regression(file):
    return int(load_file(file)["alerting"]["regression_max_difference"])


def get_alarm_minimum_difference_forecast(file):
    return int(load_file(file)["alerting"]["forecast_min_difference"])


def get_alarm_maximum_difference_forecast(file):
    return int(load_file(file)["alerting"]["forecast_max_difference"])

def get_slack_channel(file):
    return load_file(file)["slack"]["channel"]


def get_datacenter(file):
    return load_file(file)["monitoring"]["datacenter"]


def get_app(file):
    return load_file(file)["monitoring"]["app"]


def get_kubernetes_namespace(file):
    return load_file(file)["monitoring"]["kubernetes_namespace"]


def get_monitoring_time_span(file):
    return load_file(file)["monitoring"]["time_span"]


def get_monitoring_time_span_sleep(file):
    return load_file(file)["monitoring"]["time_span_sleep"]


def get_regression_info(file):
    return load_file(file)['regression']


def get_regression_info_metric(file, metric_searched):
    regression_info = load_file(file)['regression']
    number_case = 0

    for case in regression_info:
        for metric in case:
            if metric == metric_searched:
                return regression_info[number_case][metric_searched]
            else:
                number_case += 1

    return ""


def get_forecast_time(file):
    return load_file(file)["arima"]["forecast_time"]


def get_forecast_training_time(file):
    return load_file(file)["arima"]["forecast_training_time"]


def get_params_arima_metric(file, metric):
    for metric_set in load_file(file)["arima"]["metrics"]:
        metric_name = list(metric_set.keys())[0]
        if metric == metric_name:
            return metric_set[metric]

