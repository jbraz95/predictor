def list_to_str(values):
    value_str = ""
    for value in values:
        value_str += str(value) + ","
    return value_str


def adapt_time_series(series):
    value_series = []
    time_series = []
    for time, value in series:
        value_series.append(int(value))
        time_series.append(float(time))
    return [time_series, value_series]


def generate_line_chart(timeseries, name):
    base_url = "https://image-charts.com/chart"
    type_chart = "?cht=lc"
    size = "&chs=700x200"

    data_parsed = adapt_time_series(timeseries)
    values = data_parsed[1]
    time = data_parsed[0]

    values_str = list_to_str(values)

    data_url = "&chd=a:" + values_str

    min_y = str(values[0])
    max_y = str(values[len(values) - 1])

    axis = "&chxt=x,y&chxs=0,s"
    range_chart = "&chxr=1," + min_y + "," + max_y
    title_chart = "&chtt=" + name

    chart_extras = axis + range_chart + title_chart

    url = base_url + type_chart + size + chart_extras + data_url
    return url
