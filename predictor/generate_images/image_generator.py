import math

from api_calls.general_api_calls import adapt_time_series


# It generates a chart for timeseries (the timeseries that have not been adapted)
# timeseries: array of a timeseries to be adapted
# name: name of the chart
def generate_timeseries_chart(timeseries, name):
    data_parsed = adapt_time_series(timeseries)
    values = data_parsed[1]
    time = data_parsed[0]

    values_str = list_to_str(values)

    min_y = str(min(values))
    max_y = str(max(values))

    url = generate_url_chart(data=values_str, name=name, max_y=max_y, min_y=min_y)
    return url


# It generates a chart
# data: array of data to be put on the chart
# name: name of the chart
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
def list_to_str(values):
    value_str = ""
    for value in values:
        value_str += str(value) + ","

    # removing last character of string because of extra comma
    value_str = value_str[:-1]
    return value_str


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
            values = data_parsed[1]

            length = len(values) - 1
            start = length-time
            if start < 0:
                start = 0

            values = values[start:length]
            data += list_to_str(values)
        else:
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


def generate_url_multichart(array_data, array_names, name, time):
    base_url = "https://image-charts.com/chart"
    type_chart = "?cht=lxy"
    size = "&chs=700x200"
    data = generate_data_multichart(array_data=array_data, array_names=array_names, time=time)
    max_y = None
    min_y = None

    for array in array_data:
        if isinstance(array[0], list):
            data_parsed = adapt_time_series(array)
            values = data_parsed[1]
            local_max_y = max(values)
            local_min_y = min(values)
        else:
            local_max_y = max(array)
            local_min_y = min(array)

        if max_y is None or local_max_y > max_y:
            max_y = local_max_y

        if min_y is None or local_min_y < min_y:
            min_y = local_min_y

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
