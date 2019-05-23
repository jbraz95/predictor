import sys

import yaml


def load_file(file):
    try:
        with open(file, 'r') as yamlfile:
            config = yaml.safe_load(yamlfile)
            return config
    except yaml.parser.ParserError:
        print("Oops!", sys.exc_info()[0], "occured.")


def get_server(file):
    return load_file(file)["server"]["url"]


def get_datacenter(file):
    return load_file(file)["server"]["datacenter"]


def get_app(file):
    return load_file(file)["server"]["app"]


def get_kubernetes_namespace(file):
    return load_file(file)["server"]["kubernetes_namespace"]


def get_regression_info(file):
    return load_file(file)['regression']


def get_forecast_time(file):
    return load_file(file)["arima"]["forecast_time"]


def get_forecast_training_time(file):
    return load_file(file)["arima"]["forecast_training_time"]

