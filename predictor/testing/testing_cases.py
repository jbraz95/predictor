import csv

from alarms.alarm_system import calculate_percentage, alarm_regression, alarm_forecast
from api.general_api_calls import adapt_time_series
from file_loader.config_loader import get_regression_info, get_regression_info_metric, get_params_arima_metric, \
    get_forecast_time, get_monitoring_forecast_percentage
from prediction.arima import get_forecasts_array


def test_cases():
    cases = [['case1', 'incoming_task_count_total-BASIC_PREPARATION'],
             ['case2', 'incoming_task_count_total-BASIC_PREPARATION'],
             ['case3', 'incoming_task_count_total-BASIC_PREPARATION'],
             ['case4', 'incoming_task_count_total-BASIC_PREPARATION'],
             ['case5', 'incoming_task_count_total-BASIC_PREPARATION'],
             ['case6', 'incoming_task_count_total-BASIC_PREPARATION'],
             ['case7', 'incoming_task_count_total-BASIC_PREPARATION']
             ]
    cases = [['case7', 'incoming_task_count_total-BASIC_PREPARATION']]

    for case, regression in cases:
        print("----------------Testing " + case + "----------------")
        test_case(case, regression)


def test_case(case, regression_name):
    file = "predictor/testing_data/" + case + "/" + case + ".csv"
    config_file = "predictor/configuration.yaml"
    span = 5

    minutes_alarm_regression = test_regression(regression_name, file, config_file, auto_reset=False)
    print("----------------------TESTING REGRESSION WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_alarm_regression)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_alarm_regression))
    print("------------------------------------------------------------------")

    print("----------------------TESTING FORECAST-C WITH " + case + " ----------------------")
    minutes_alarm_forecast_c = test_forecast(regression_name, file, config_file, span, 'c')
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_alarm_forecast_c)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_alarm_forecast_c)*span)
    print("------------------------------------------------------------------")

    print("----------------------TESTING FORECAST-NC WITH " + case + " ----------------------")
    minutes_alarm_forecast_nc = test_forecast(regression_name, file, config_file, span, 'nc')
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_alarm_forecast_nc)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_alarm_forecast_nc)*span)

    print("----------------------TESTING FORECAST-ANY WITH " + case + " ----------------------")
    minutes_alarm_forecast_any = sorted(set(minutes_alarm_forecast_c).union(minutes_alarm_forecast_nc))
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_alarm_forecast_any)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_alarm_forecast_any)*span)
    print("------------------------------------------------------------------")

    print("----------------------TESTING FORECAST-BOTH WITH " + case + " ----------------------")
    minutes_alarm_forecast_both = sorted(set(minutes_alarm_forecast_c).intersection(minutes_alarm_forecast_nc))
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_alarm_forecast_both)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_alarm_forecast_both)*span)
    print("------------------------------------------------------------------")

    print("----------------------TESTING DOUBLE_CHECK-C WITH " + case + " ----------------------")
    minutes_double_check_c = test_double_check(minutes_alarm_regression, minutes_alarm_forecast_c)
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_double_check_c)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_double_check_c)*span)
    print("------------------------------------------------------------------")

    print("----------------------TESTING DOUBLE_CHECK-NC WITH " + case + " ----------------------")
    minutes_double_check_nc = test_double_check(minutes_alarm_regression, minutes_alarm_forecast_nc)
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_double_check_nc)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_double_check_nc)*span)
    print("------------------------------------------------------------------")

    print("----------------------TESTING DOUBLE_CHECK-ANY WITH " + case + " ----------------------")
    minutes_double_check_any = sorted(set(minutes_double_check_c).union(minutes_double_check_nc))
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_double_check_any)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_double_check_any) * span)
    print("------------------------------------------------------------------")

    print("----------------------TESTING DOUBLE_CHECK-BOTH WITH " + case + " ----------------------")
    minutes_double_check_both = sorted(set(minutes_double_check_c).intersection(minutes_double_check_nc))
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_double_check_both)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_double_check_both)*span)
    print("------------------------------------------------------------------")

    print("----------------------TESTING DOUBLE_FORECAST-C WITH " + case + " ----------------------")
    minutes_double_forecast_check_c = test_double_forecast(file, minutes_alarm_forecast_c, config_file)
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_double_forecast_check_c)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_double_forecast_check_c)*span)
    print("------------------------------------------------------------------")

    print("----------------------TESTING DOUBLE_FORECAST-NC WITH " + case + " ----------------------")
    minutes_double_forecast_check_nc = test_double_forecast(file, minutes_alarm_forecast_nc, config_file)
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_double_forecast_check_nc)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_double_forecast_check_nc)*span)
    print("------------------------------------------------------------------")

    print("----------------------TESTING DOUBLE_FORECAST-ANY WITH " + case + " ----------------------")
    minutes_double_forecast_check_any = sorted(set(minutes_double_forecast_check_c).union(minutes_double_forecast_check_nc))
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_double_forecast_check_any)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_double_forecast_check_any)*span)
    print("------------------------------------------------------------------")

    print("----------------------TESTING DOUBLE_FORECAST-BOTH WITH " + case + " ----------------------")
    minutes_double_forecast_check_both = sorted(set(minutes_double_forecast_check_c).intersection(minutes_double_forecast_check_nc))
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_double_forecast_check_both)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_double_forecast_check_both)*span)
    print("------------------------------------------------------------------")


def test_double_forecast(file, minutes_alarm_forecast, config_file):
    time_series = prepare_timeseries(file, "ITCT")
    forecast_percentage = get_monitoring_forecast_percentage(config_file)
    anomaly_minutes = []

    for minutes in minutes_alarm_forecast:
        start = int((minutes/60) - 60 + 1)
        finish = int(minutes/60 + 1)

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
        adapted_finish = finish * 60
        if alarm_forecast(forecasts=forecasts, config_file=config_file, mode=mode):
            print("ALAAARRRRMMMMM!!!!!!!")
            minutes_alarm.append(adapted_finish)
            print(minutes_alarm)

        start += span
        finish += span
        print("For time:" + str(adapted_finish))
        print(time_series_reduced)
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

            print(time)
            regression_val = calculate_regression(error=IECT_ERROR, finished=IECT_FINISHED, started=IECT_STARTED,
                                                  terminated=IECT_TERMINATED, metric_regression=regression_name)

            if auto_reset:
                if regression_val != previous_regression:
                    if alarm_regression(actual_value=ITCT, calculated_value=regression_val, config_file=config_file):
                        print("alarm!")
                        minutes_alarm.append(time)
            elif alarm_regression(actual_value=ITCT, calculated_value=regression_val, config_file=config_file):
                minutes_alarm.append(time)
                print("alarm!")

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
