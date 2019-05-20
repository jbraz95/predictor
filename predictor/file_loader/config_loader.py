import yaml


def load_file(file):
    with open(file, 'r') as yamlfile:
        config = yaml.safe_load(yamlfile)
        return config


def get_server(file):
    return load_file(file)["server"]["url"]


def get_datacenter(file):
    return load_file(file)["server"]["datacenter"]


def get_app(file):
    return load_file(file)["server"]["app"]
