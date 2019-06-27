import csv

from alarms.alarm_system import calculate_percentage, alarm_regression, alarm_forecast
from api_calls.general_api_calls import adapt_time_series
from file_loader.config_loader import get_regression_info, get_regression_info_metric, get_params_arima_metric, \
    get_forecast_time, get_monitoring_forecast_percentage
from prediction.arima import get_forecasts_array


def test_cases():
    cases = [['case1', 'incoming_task_count_total-BASIC_PREPARATION']]

    for case, regression in cases:
        test_case(case, regression)


def test_case(case, regression_name):
    file = "predictor/testing_data/" + case + "/" + case + ".csv"
    config_file = "predictor/configuration.yaml"

    #minutes_alarm_regression = test_regression(regression_name, file, config_file)
    #print(minutes_alarm_regression)

    span = 10
    #minutes_alarm_forecast = test_forecast(regression_name, file, config_file, span)
    #print("Minutes of alarm: " + str(minutes_alarm_forecast))

    #minutes_double_check = test_double_check(regression_name, file, config_file, span)
    #print("Minutes of alarm: " + str(minutes_double_check))

    minutes_double_forecast_check = test_double_forecast_check(regression_name, file, config_file, span, 'c')
    print("Minutes of alarm: " + str(minutes_double_forecast_check))


def test_double_forecast_check(regression_name, file, config_file, span, mode):
    time_series = prepare_timeseries(file, "ITCT")
    params = get_params_arima_metric(file=config_file, metric=regression_name)
    forecast_time = get_forecast_time(config_file)
    forecast_percentage = get_monitoring_forecast_percentage(config_file)
    start = 0
    finish = 60
    anomaly_minutes = 0

    while finish <= len(time_series):
        print("Minutes: " + str(start) + "-" + str(finish))
        time_series_reduced = time_series[start:finish]
        time_series_reduced_adapted = adapt_time_series(time_series_reduced)
        max_actual = max(time_series_reduced_adapted[1])
        min_actual = min(time_series_reduced_adapted[1])
        difference_actual = calculate_percentage(max_actual, min_actual)
        print(difference_actual)

        if difference_actual > forecast_percentage:
            print("Initially growing")

            forecast_anomaly = True
            forecasts = get_forecasts_array(params=params, time_series=time_series_reduced,
                                            forecast_time=forecast_time)

            for forecast in forecasts:
                if (forecast[0] == mode) or (mode == 'both'):
                    min_forecast = min(forecast[1])
                    max_forecast = max(forecast[1])
                    difference_forecast = calculate_percentage(max_forecast, min_forecast)
                    print(difference_forecast)

                    if difference_forecast > difference_actual:
                        forecast_anomaly = forecast_anomaly and True
                        print("growing more")
                    else:
                        forecast_anomaly = forecast_anomaly and False
                        print("not growing more")

            if forecast_anomaly:
                anomaly_minutes += span

        start += span
        finish += span

    return anomaly_minutes


def test_double_check(regression_name, file, config_file, span):
    minute = 0
    time_series = prepare_timeseries(file, "ITCT")
    start_timeseries = 0
    end_timeseries = 60
    forecast_time = get_forecast_time(config_file)
    params = get_params_arima_metric(file=config_file, metric=regression_name)
    anomaly_minutes = 0

    with open(file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=";")

        # Each row is a minute
        for row in csv_reader:
            # If the minute coincides with the span
            if minute % span == 0:
                print("minute: " + str(minute))

                # We get the variables
                alarm = True
                ITCT = float(row["ITCT"])
                IECT_ERROR = float(row["IECT-ERROR"])
                IECT_FINISHED = float(row["IECT-FINISHED"])
                IECT_STARTED = float(row["IECT-STARTED"])
                IECT_TERMINATED = float(row["IECT-TERMINATED"])

                # We check the regression
                regression_val = calculate_regression(error=IECT_ERROR, finished=IECT_FINISHED, started=IECT_STARTED,
                                                      terminated=IECT_TERMINATED, metric_regression=regression_name)
                if alarm_regression(actual_value=ITCT, calculated_value=regression_val, config_file=config_file):
                    alarm = alarm and True
                    print("alarm regression: yes")
                else:
                    alarm = alarm and False
                    print("alarm regression: no")

                # We check the forecast
                time_series_reduced = time_series[start_timeseries:end_timeseries]
                forecasts = get_forecasts_array(params=params, time_series=time_series_reduced,
                                                forecast_time=forecast_time)

                if alarm_forecast(forecasts=forecasts, config_file=config_file, mode='c'):
                    alarm = alarm and True
                    print("alarm forecast: yes")
                else:
                    alarm = alarm and False
                    print("alarm forecast: no")

                # We check both alarms
                if alarm:
                    print("general alarm: yes")
                    anomaly_minutes += span
                else:
                    print("general alarm: no")

                # We prepare variables for next iteration
                start_timeseries += span
                end_timeseries += span

            minute += 1

    return anomaly_minutes


def test_forecast(regression_name, file, config_file, span):
    # [[1561545165.181, '1254'], [1561545225.181, '1254'], [1561545285.181, '1254'],...]
    params = get_params_arima_metric(file=config_file, metric=regression_name)
    minutes_alarm = 0

    time_series = prepare_timeseries(file, "ITCT")

    start = 0
    finish = 60
    forecast_time = get_forecast_time(config_file)
    while finish <= len(time_series):
        time_series_reduced = time_series[start:finish]
        forecasts = get_forecasts_array(params=params, time_series=time_series_reduced, forecast_time=forecast_time)
        if alarm_forecast(forecasts=forecasts, config_file=config_file, mode='c'):
            print("alarma!")
            minutes_alarm += span

        start += span
        finish += span

    return minutes_alarm


def prepare_timeseries(file, metric_name):
    with open(file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=";")
        time_series = []

        for row in csv_reader:
            time = float(row["Time"])
            value = float(row[metric_name])
            set = [time, value]
            time_series.append(set)

    return time_series


def test_regression(regression_name, file, config_file):
    print("Testing regression")
    minutes_alarm = 0

    with open(file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=";")

        for row in csv_reader:
            ITCT = float(row["ITCT"])
            IECT_ERROR = float(row["IECT-ERROR"])
            IECT_FINISHED = float(row["IECT-FINISHED"])
            IECT_STARTED = float(row["IECT-STARTED"])
            IECT_TERMINATED = float(row["IECT-TERMINATED"])

            regression_val = calculate_regression(error=IECT_ERROR, finished=IECT_FINISHED, started=IECT_STARTED,
                                                  terminated=IECT_TERMINATED, metric_regression=regression_name)

            if alarm_regression(actual_value=ITCT, calculated_value=regression_val, config_file=config_file):
                minutes_alarm += 1

    return minutes_alarm


def calculate_regression(error, finished, started, terminated, metric_regression):
    config = "predictor/configuration.yaml"
    regression_info_metric = get_regression_info_metric(config, metric_regression)
    regression = 0

    for metric_set in regression_info_metric["metrics"]:
        for metric_name in metric_set:
            mult = float(metric_set[metric_name]["value"])
            exp = float(metric_set[metric_name]["exp"])
            if metric_set[metric_name]["event_type"] == 'STARTED':
                value = float(started)
            elif metric_set[metric_name]["event_type"] == 'FINISHED':
                value = float(finished)
            elif metric_set[metric_name]["event_type"] == 'TERMINATED':
                value = float(terminated)
            elif metric_set[metric_name]["event_type"] == 'ERROR':
                value = float(error)

            regression += mult * pow(value, exp)

    regression += float(regression_info_metric["constant"])

    return regression
