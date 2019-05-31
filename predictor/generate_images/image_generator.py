from api_calls.general_api_calls import adapt_time_series

def list_to_str(values):
    value_str = ""
    for value in values:
        value_str += str(value) + ","
    return value_str


def generate_timeseries_chart(timeseries, name):
    data_parsed = adapt_time_series(timeseries)
    values = data_parsed[1]
    time = data_parsed[0]

    values_str = list_to_str(values)

    min_y = str(values[0])
    max_y = str(values[len(values) - 1])

    url = generate_url_chart(data=values_str, name=name, max_y=max_y, min_y=min_y)
    return url


def generate_data_chart(data, name):
    values_str = list_to_str(data)

    min_y = str(data[0])
    max_y = str(data[len(data) - 1])

    url = generate_url_chart(data=values_str, name=name, max_y=max_y, min_y=min_y)

    return url


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
