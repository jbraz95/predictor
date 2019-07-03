import csv

from alarms.alarm_system import calculate_percentage, alarm_regression, alarm_forecast
from api_calls.general_api_calls import adapt_time_series
from file_loader.config_loader import get_regression_info, get_regression_info_metric, get_params_arima_metric, \
    get_forecast_time, get_monitoring_forecast_percentage
from prediction.arima import get_forecasts_array


def test_cases():
    cases = [['case1', 'incoming_task_count_total-BASIC_PREPARATION']]

    for case, regression in cases:
        print("----------------Testing " + case + "----------------")
        test_case(case, regression)


def test_case(case, regression_name):
    file = "predictor/testing_data/" + case + "/" + case + ".csv"
    config_file = "predictor/configuration.yaml"
    span = 1

    minutes_alarm_regression = test_regression(regression_name, file, config_file, auto_reset=True)
    print("----------------------TESTING REGRESSION WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_alarm_regression)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_alarm_regression))
    print("------------------------------------------------------------------")

    print("----------------------TESTING FORECAST-C WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    minutes_alarm_forecast_c = test_forecast(regression_name, file, config_file, span, 'c')
    print(minutes_alarm_forecast_c)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_alarm_forecast_c)*span)
    print("------------------------------------------------------------------")

    print("----------------------TESTING FORECAST-NC WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    minutes_alarm_forecast_nc = test_forecast(regression_name, file, config_file, span, 'nc')
    print(minutes_alarm_forecast_nc)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_alarm_forecast_nc)*span)

    print("----------------------TESTING FORECAST-ANY WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    minutes_alarm_forecast_any = minutes_alarm_forecast_c or minutes_alarm_forecast_nc
    print(minutes_alarm_forecast_any)
    print(len(minutes_alarm_forecast_any)*span)
    print("------------------------------------------------------------------")

    print("----------------------TESTING FORECAST-BOTH WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    minutes_alarm_forecast_both = minutes_alarm_forecast_c and minutes_alarm_forecast_nc
    print(minutes_alarm_forecast_both)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_alarm_forecast_both)*span)
    print("------------------------------------------------------------------")

    print("----------------------TESTING DOUBLE_CHECK-C WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    minutes_double_check_c = test_double_check(minutes_alarm_regression, minutes_alarm_forecast_c)
    print(minutes_double_check_c)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_double_check_c)*span)
    print("------------------------------------------------------------------")

    print("----------------------TESTING DOUBLE_CHECK-NC WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    minutes_double_check_nc = test_double_check(minutes_alarm_regression, minutes_alarm_forecast_nc)
    print(minutes_double_check_nc)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_double_check_nc)*span)
    print("------------------------------------------------------------------")

    print("----------------------TESTING DOUBLE_CHECK-ANY WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    minutes_double_check_any = minutes_double_check_c or minutes_double_check_nc
    print(minutes_double_check_any)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_double_check_any) * span)
    print("------------------------------------------------------------------")

    print("----------------------TESTING DOUBLE_CHECK-BOTH WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    minutes_double_check_both = minutes_double_check_c and minutes_double_check_nc
    print(minutes_double_check_both)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_double_check_both)*span)
    print("------------------------------------------------------------------")

    print("----------------------TESTING DOUBLE_FORECAST-C WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    minutes_double_forecast_check_c = test_double_forecast(file, minutes_alarm_forecast_c, config_file)
    print(minutes_double_forecast_check_c)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_double_forecast_check_c)*span)
    print("------------------------------------------------------------------")

    print("----------------------TESTING DOUBLE_FORECAST-NC WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    minutes_double_forecast_check_nc = test_double_forecast(file, minutes_alarm_forecast_nc, config_file)
    print(minutes_double_forecast_check_nc)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_double_forecast_check_nc)*span)
    print("------------------------------------------------------------------")

    print("----------------------TESTING DOUBLE_FORECAST-ANY WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    minutes_double_forecast_check_any = minutes_double_forecast_check_c or minutes_double_forecast_check_nc
    print(minutes_double_forecast_check_any)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_double_forecast_check_any)*span)
    print("------------------------------------------------------------------")

    print("----------------------TESTING DOUBLE_FORECAST-BOTH WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    minutes_double_forecast_check_both = minutes_double_forecast_check_c and minutes_double_forecast_check_nc
    print(minutes_double_forecast_check_both)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_double_forecast_check_both)*span)
    print("------------------------------------------------------------------")


def test_double_forecast(file, minutes_alarm_forecast, config_file):
    time_series = prepare_timeseries(file, "ITCT")
    forecast_percentage = get_monitoring_forecast_percentage(config_file)
    anomaly_minutes = []

    for minutes in minutes_alarm_forecast:
        start = minutes - 60
        finish = minutes

        time_series_reduced = time_series[start:finish]
        time_series_reduced_adapted = adapt_time_series(time_series_reduced)
        max_actual = max(time_series_reduced_adapted[1])
        min_actual = min(time_series_reduced_adapted[1])
        difference_actual = calculate_percentage(max_actual, min_actual)

        if difference_actual > forecast_percentage:
            anomaly_minutes.append(finish)

    anomaly_minutes = anomaly_minutes and minutes_alarm_forecast

    return anomaly_minutes


def test_double_check(minutes_alarm_regression, minutes_alarm_forecast):
    minutes_double_check = minutes_alarm_regression and minutes_alarm_forecast

    return minutes_double_check


def test_forecast(regression_name, file, config_file, span, mode):
    params = get_params_arima_metric(file=config_file, metric=regression_name)
    minutes_alarm = []

    time_series = prepare_timeseries(file, "ITCT")

    start = 0
    finish = 60
    forecast_time = get_forecast_time(config_file)
    while finish <= len(time_series):
        time_series_reduced = time_series[start:finish]
        forecasts = get_forecasts_array(params=params, time_series=time_series_reduced, forecast_time=forecast_time)
        if alarm_forecast(forecasts=forecasts, config_file=config_file, mode=mode):
            minutes_alarm.append(finish)

        start += span
        finish += span
        print(forecasts)

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


def test_regression(regression_name, file, config_file, auto_reset):
    minutes_alarm = []
    previous_regression = 0

    with open(file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=";")

        for row in csv_reader:
            time = int(row["Time"])
            ITCT = float(row["ITCT"])
            IECT_ERROR = float(row["IECT-ERROR"])
            IECT_FINISHED = float(row["IECT-FINISHED"])
            IECT_STARTED = float(row["IECT-STARTED"])
            IECT_TERMINATED = float(row["IECT-TERMINATED"])

            regression_val = calculate_regression(error=IECT_ERROR, finished=IECT_FINISHED, started=IECT_STARTED,
                                                  terminated=IECT_TERMINATED, metric_regression=regression_name)

            if auto_reset:
                if regression_val != previous_regression:
                    if alarm_regression(actual_value=ITCT, calculated_value=regression_val, config_file=config_file):
                        minutes_alarm.append(time)
            elif alarm_regression(actual_value=ITCT, calculated_value=regression_val, config_file=config_file):
                minutes_alarm.append(time)

            previous_regression = regression_val

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
