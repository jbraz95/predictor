from api.general_api_calls import adapt_time_series, get_query_actual_search, get_values
from file_loader.config_loader import get_server, get_monitoring_time_span, get_forecast_time, \
    get_forecast_training_time, get_params_arima_metric
from prediction.arima import get_forecasts_array
from prediction.regression import get_regression_array_search


# It generates a chart for timeseries (the timeseries that have not been adapted)
# timeseries: array of a timeseries to be adapted and then used in the chart
# name: name of the chart
# Output: An url that redirects yot to the chart
def generate_timeseries_chart(timeseries, name):
    data_parsed = adapt_time_series(timeseries)
    values = data_parsed[1]
    time = data_parsed[0]

    values_str = list_to_str(values)

    min_y = str(min(values))
    max_y = str(max(values))

    url = generate_url_chart(data=values_str, name=name, max_y=max_y, min_y=min_y)
    return url


# It generates a chart with data
# data: array of data to be put on the chart
# name: name of the chart
# Output: An url that redirects yot to the chart
def generate_data_chart(data, name):
    values_str = list_to_str(data)

    min_y = str(min(data))
    max_y = str(max(data))

    url = generate_url_chart(data=values_str, name=name, max_y=max_y, min_y=min_y)

    return url


# Generates the url of the chart to be displayed
# data: string with the data to be displayed in the chart
# name: name of the chart
# max_y: max value of axis Y
# min_y: min value of axis Y
# Output: An url that redirects you to the chart
def generate_url_chart(data, name, max_y, min_y):
    base_url = "https://image-charts.com/chart"
    type_chart = "?cht=lc"
    size = "&chs=700x200"

    data_url = "&chd=a:" + data

    axis = "&chxt=x,y&chxs=0,s|1,s"
    range_chart = "&chxr=1," + min_y + "," + max_y
    title_chart = "&chtt=" + name

    chart_extras = axis + range_chart + title_chart

    url = base_url + type_chart + size + chart_extras + data_url
    return url


# Transforms a list to a string to put it into the URL generator
# values: values to be transformed to a string
# Output: A string with the values of the list
def list_to_str(values):
    value_str = ""
    for value in values:
        value_str += str(value) + ","

    # removing last character of string because of extra comma
    value_str = value_str[:-1]
    return value_str


# This function will generate the data to create a multichart (a chart with multiple variables). It will get the
# information from two arrays (one with the data, the other with the names) and will create a string that will be used
# in the generate_url_multichart
# array_data: array with n arrays, each of them with the values of a metric
# array_names: array with n names corresponding to array_data metric names
# time: how much time of information we are going to show (each metric has X minutes of information)
# Output: The data parsed for using it in other functions
def generate_data_multichart(array_data, array_names, time):
    data = "&chd=a:"
    index = 0
    for array in array_data:

        if 'forecast' in array_names[index]:
            data += list_to_str(range(time, time+time))
        else:
            data += list_to_str(range(0, time))

        data += "|"

        if isinstance(array[0], list):
            data_parsed = adapt_time_series(array)
            array = data_parsed[1]

        length = len(array) - 1
        start = length - time
        if start < 0:
            start = 0

        array = array[start:length]
        data += list_to_str(array)

        data += "|"
        index += 1
    data = data[:-1]
    return data


# This function will generate an url that will redirect you to a chart that will show several metrics. It will get the
# information from two arrays (one with the data, the other with the names) and will create an url
# array_data: array with n arrays, each of them with the values of a metric
# array_names: array with n names corresponding to array_data metric names (regression, actual and/or forecast)
# name: name of the chart
# time: how much time of information we are going to show (each metric has X minutes of information)
# Output: The url of the multichart according to the array_data introduced
def generate_url_multichart(array_data, array_names, name, time):
    base_url = "https://image-charts.com/chart"
    type_chart = "?cht=lxy"
    size = "&chs=700x200"
    data = generate_data_multichart(array_data=array_data, array_names=array_names, time=time)
    max_y = None
    min_y = None

    # for each metric in the array_data we parse the information and we get its max and min values to adapt the chart
    for array in array_data:
        if isinstance(array[0], list):
            data_parsed = adapt_time_series(array)
            array = data_parsed[1]

        local_max_y = max(array)
        local_min_y = min(array)

        if max_y is None or local_max_y > max_y:
            max_y = local_max_y

        if min_y is None or local_min_y < min_y:
            min_y = local_min_y

    # We adapt that information for the image-charts.com format
    axis = "&chxt=x,y&chxs=0,s|1,s"
    range_chart = "&chxr=1," + str(min_y) + "," + str(max_y)
    title_chart = "&chtt=" + name

    legend = "&chdl="
    for legend_name in array_names:
        legend += legend_name + "|"
    legend = legend[:-1]

    chart_extras = axis + range_chart + title_chart + legend
    url = base_url + type_chart + size + chart_extras + data

    return url


# This function will output the url of an image with the information of different metrics. The input will be the metric
# you want to get and the type of information you want to get (actual, forecast and/or regression)
# arrays_to_get: array with the type of information you want to get (actual, forecast and/or regression)
# metric: name of the metric to get the information
# Output: an url with the metric information.
def get_url_image(arrays_to_get, metric):
    config_file = "predictor/configuration.yaml"

    server = get_server(config_file)
    time = get_monitoring_time_span(config_file)
    query = get_query_actual_search(config=config_file, metric=metric)

    multi_data = []
    array_names = []

    if 'actual' in arrays_to_get:
        actual = get_values(server=server, query=query, minutes=time)
        multi_data.append(actual)
        array_names.append('actual')

    if 'regression' in arrays_to_get:
        regression_array = get_regression_array_search(config=config_file, metric=metric)
        multi_data.append(regression_array)
        array_names.append('regression')

    if 'forecast' in arrays_to_get:
        forecast_time = get_forecast_time(config_file)
        forecast_training_time = get_forecast_training_time(config_file)
        time_series_training = get_values(server=server, query=query, minutes=forecast_training_time)
        params = get_params_arima_metric(file=config_file, metric=metric)

        forecasts = get_forecasts_array(params=params, time_series=time_series_training, forecast_time=forecast_time)

        for set_arima in forecasts:
            array_names.append("forecast:" + set_arima[0])
            multi_data.append(set_arima[1])

    url = generate_url_multichart(array_data=multi_data, array_names=array_names, name=metric,
                                  time=time)

    return url
