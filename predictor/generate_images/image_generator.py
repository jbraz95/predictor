from api_calls.general_api_calls import adapt_time_series


# It generates a chart for timeseries (the timeseries that have not been adapted)
# timeseries: array of a timeseries to be adapted
# name: name of the chart
def generate_timeseries_chart(timeseries, name):
    data_parsed = adapt_time_series(timeseries)
    values = data_parsed[1]
    time = data_parsed[0]

    values_str = list_to_str(values)

    min_y = str(values[0])
    max_y = str(values[len(values) - 1])

    url = generate_url_chart(data=values_str, name=name, max_y=max_y, min_y=min_y)
    return url


# It generates a chart
# data: array of data to be put on the chart
# name: name of the chart
def generate_data_chart(data, name):
    values_str = list_to_str(data)

    min_y = str(data[0])
    max_y = str(data[len(data) - 1])

    url = generate_url_chart(data=values_str, name=name, max_y=max_y, min_y=min_y)

    return url


# Transforms a list to a string to put it into the URL generator
# values: values to be transformed to a string
def list_to_str(values):
    value_str = ""
    for value in values:
        value_str += str(value) + ","

    # removing last character of string because of extra comma
    value_str = value_str
    return value_str[:-1]


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
