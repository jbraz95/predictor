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
    span = 1
    negatives1 = [0,60,120,180,240,300,360,420,480,540,600,660,720,780,840,900,960,1020,1080,1140,1200,1260,1320,1380,1440,1500,1560,1620,1680,1740,1800,1860,1920,1980,2040,2100,2160,2220,2280,2340,2400,2460,2520,2580,2640,2700,2760,2820,2880,2940,3000,3060,3120,3180,3240,3300,3360,3420,3480,3540]
    positives = [3600,3660,3720,3780,3840,3900,3960,4020,4080,4140,4200,4260,4320,4380,4440,4500,4560,4620,4680,4740,4800,4860,4920,4980,5040,5100,5160,5220,5280,5340,5400,5460,5520,5580,5640,5700,5760,5820,5880,5940,6000,6060,6120,6180,6240,6300,6360,6420,6480,6540,6600,6660,6720,6780,6840,6900,6960,7020,7080,7140,7200,7260,7320,7380,7440,7500,7560,7620,7680,7740,7800,7860,7920,7980,8040,8100,8160,8220,8280,8340,8400,8460,8520,8580,8640,8700,8760,8820,8880,8940,9000,9060,9120,9180,9240,9300,9360,9420,9480,9540,9600,9660,9720,9780,9840,9900,9960,10020,10080,10140,10200,10260,10320,10380,10440,10500,10560,10620,10680,10740]
    negatives2 = [10800,10860,10920,10980,11040,11100,11160,11220,11280,11340,11400,11460,11520,11580,11640,11700,11760,11820,11880,11940,12000,12060,12120,12180,12240,12300,12360,12420,12480,12540,12600,12660,12720,12780,12840,12900,12960,13020,13080,13140,13200,13260,13320,13380,13440,13500,13560,13620,13680,13740,13800,13860,13920,13980,14040,14100,14160,14220,14280,14340,14400]

    minutes_alarm_regression = test_regression(regression_name, file, config_file, auto_reset=False, auto_constant=True)
    print("----------------------TESTING REGRESSION WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_alarm_regression)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_alarm_regression))
    print("------------------------------------------------------------------")
    print("True Positives: " + str(len(set(minutes_alarm_regression) & set(positives))))
    print("------------------------------------------------------------------")
    print("True Negatives: " + str(120 - len(set(minutes_alarm_regression) & set(negatives1 + negatives2))))
    print("------------------------------------------------------------------")
    print("False Positives: " + str(len(set(minutes_alarm_regression) & set(negatives1 + negatives2))))
    print("------------------------------------------------------------------")
    print("False Negatives: " + str(120 - len(set(minutes_alarm_regression) & set(positives))))
    if minutes_alarm_regression:
        print("------------------------------------------------------------------")
        print("Time until first detection: " + str((minutes_alarm_regression[0] - 3600) / 60))
    print("------------------------------------------------------------------")
    print("False positives after fixing it: " + str(len(set(minutes_alarm_regression) & set(negatives2))))
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

    print("----------------------TESTING " + case + " FINISHED----------------------")
    print("----------------------TESTING REGRESSION WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_alarm_regression)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_alarm_regression))
    print("------------------------------------------------------------------")
    print("True Positives: " + str(len(set(minutes_alarm_regression) & set(positives))))
    print("------------------------------------------------------------------")
    print("True Negatives: " + str(120 - len(set(minutes_alarm_regression) & set(negatives1+negatives2))))
    print("------------------------------------------------------------------")
    print("False Positives: " + str(len(set(minutes_alarm_regression) & set(negatives1+negatives2))))
    print("------------------------------------------------------------------")
    print("False Negatives: " + str(120 - len(set(minutes_alarm_regression) & set(positives))))
    if minutes_alarm_regression:
        print("------------------------------------------------------------------")
        print("Time until first detection: " + str((minutes_alarm_regression[0] - 3600)/60))
    print("------------------------------------------------------------------")
    print("False positives after fixing it: " + str(len(set(minutes_alarm_regression) & set(negatives2))))
    print("------------------------------------------------------------------")

    print("----------------------TESTING FORECAST-C WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_alarm_forecast_c)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_alarm_forecast_c)*span)
    print("------------------------------------------------------------------")
    print("True Positives: " + str(len(set(minutes_alarm_forecast_c) & set(positives))))
    print("------------------------------------------------------------------")
    print("True Negatives: " + str(120 - len(set(minutes_alarm_forecast_c) & set(negatives1+negatives2))))
    print("------------------------------------------------------------------")
    print("False Positives: " + str(len(set(minutes_alarm_forecast_c) & set(negatives1+negatives2))))
    print("------------------------------------------------------------------")
    print("False Negatives: " + str(120 - len(set(minutes_alarm_forecast_c) & set(positives))))
    print("------------------------------------------------------------------")
    if minutes_alarm_forecast_c:
        print("Time until first detection: " + str((minutes_alarm_forecast_c[0] - 3600) / 60))
        print("------------------------------------------------------------------")
    print("False positives after fixing it: " + str(len(set(minutes_alarm_forecast_c) & set(negatives2))))
    print("------------------------------------------------------------------")

    print("----------------------TESTING FORECAST-NC WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_alarm_forecast_nc)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_alarm_forecast_nc)*span)
    print("------------------------------------------------------------------")
    print("True Positives: " + str(len(set(minutes_alarm_forecast_nc) & set(positives))))
    print("------------------------------------------------------------------")
    print("True Negatives: " + str(120 - len(set(minutes_alarm_forecast_nc) & set(negatives1+negatives2))))
    print("------------------------------------------------------------------")
    print("False Positives: " + str(len(set(minutes_alarm_forecast_nc) & set(negatives1+negatives2))))
    print("------------------------------------------------------------------")
    print("False Negatives: " + str(120 - len(set(minutes_alarm_forecast_nc) & set(positives))))
    print("------------------------------------------------------------------")
    if minutes_alarm_forecast_nc:
        print("Time until first detection: " + str((minutes_alarm_forecast_nc[0] - 3600) / 60))
        print("------------------------------------------------------------------")
    print("False positives after fixing it: " + str(len(set(minutes_alarm_forecast_nc) & set(negatives2))))
    print("------------------------------------------------------------------")

    print("----------------------TESTING FORECAST-ANY WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_alarm_forecast_any)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_alarm_forecast_any)*span)
    print("------------------------------------------------------------------")
    print("True Positives: " + str(len(set(minutes_alarm_forecast_any) & set(positives))))
    print("------------------------------------------------------------------")
    print("True Negatives: " + str(120 - len(set(minutes_alarm_forecast_any) & set(negatives1 + negatives2))))
    print("------------------------------------------------------------------")
    print("False Positives: " + str(len(set(minutes_alarm_forecast_any) & set(negatives1 + negatives2))))
    print("------------------------------------------------------------------")
    print("False Negatives: " + str(120 - len(set(minutes_alarm_forecast_any) & set(positives))))
    print("------------------------------------------------------------------")
    if minutes_alarm_forecast_any:
        print("Time until first detection: " + str((minutes_alarm_forecast_any[0] - 3600) / 60))
        print("------------------------------------------------------------------")
    print("False positives after fixing it: " + str(len(set(minutes_alarm_forecast_any) & set(negatives2))))
    print("------------------------------------------------------------------")

    print("----------------------TESTING FORECAST-BOTH WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_alarm_forecast_both)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_alarm_forecast_both)*span)
    print("------------------------------------------------------------------")
    print("True Positives: " + str(len(set(minutes_alarm_forecast_both) & set(positives))))
    print("------------------------------------------------------------------")
    print("True Negatives: " + str(120 - len(set(minutes_alarm_forecast_both) & set(negatives1 + negatives2))))
    print("------------------------------------------------------------------")
    print("False Positives: " + str(len(set(minutes_alarm_forecast_both) & set(negatives1 + negatives2))))
    print("------------------------------------------------------------------")
    print("False Negatives: " + str(120 - len(set(minutes_alarm_forecast_both) & set(positives))))
    print("------------------------------------------------------------------")
    if minutes_alarm_forecast_both:
        print("Time until first detection: " + str((minutes_alarm_forecast_both[0] - 3600) / 60))
        print("------------------------------------------------------------------")
    print("False positives after fixing it: " + str(len(set(minutes_alarm_forecast_both) & set(negatives2))))
    print("------------------------------------------------------------------")

    print("----------------------TESTING DOUBLE_CHECK-C WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_double_check_c)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_double_check_c)*span)
    print("------------------------------------------------------------------")
    print("True Positives: " + str(len(set(minutes_double_check_c) & set(positives))))
    print("------------------------------------------------------------------")
    print("True Negatives: " + str(120 - len(set(minutes_double_check_c) & set(negatives1 + negatives2))))
    print("------------------------------------------------------------------")
    print("False Positives: " + str(len(set(minutes_double_check_c) & set(negatives1 + negatives2))))
    print("------------------------------------------------------------------")
    print("False Negatives: " + str(120 - len(set(minutes_double_check_c) & set(positives))))
    print("------------------------------------------------------------------")
    if minutes_double_check_c:
        print("Time until first detection: " + str((minutes_double_check_c[0] - 3600) / 60))
        print("------------------------------------------------------------------")
    print("False positives after fixing it: " + str(len(set(minutes_double_check_c) & set(negatives2))))
    print("------------------------------------------------------------------")

    print("----------------------TESTING DOUBLE_CHECK-NC WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_double_check_nc)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_double_check_nc)*span)
    print("------------------------------------------------------------------")
    print("True Positives: " + str(len(set(minutes_double_check_nc) & set(positives))))
    print("------------------------------------------------------------------")
    print("True Negatives: " + str(120 - len(set(minutes_double_check_nc) & set(negatives1 + negatives2))))
    print("------------------------------------------------------------------")
    print("False Positives: " + str(len(set(minutes_double_check_nc) & set(negatives1 + negatives2))))
    print("------------------------------------------------------------------")
    print("False Negatives: " + str(120 - len(set(minutes_double_check_nc) & set(positives))))
    print("------------------------------------------------------------------")
    if minutes_double_check_nc:
        print("Time until first detection: " + str((minutes_double_check_nc[0] - 3600) / 60))
        print("------------------------------------------------------------------")
    print("False positives after fixing it: " + str(len(set(minutes_double_check_nc) & set(negatives2))))
    print("------------------------------------------------------------------")

    print("----------------------TESTING DOUBLE_CHECK-ANY WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_double_check_any)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_double_check_any) * span)
    print("------------------------------------------------------------------")
    print("True Positives: " + str(len(set(minutes_double_check_any) & set(positives))))
    print("------------------------------------------------------------------")
    print("True Negatives: " + str(120 - len(set(minutes_double_check_any) & set(negatives1 + negatives2))))
    print("------------------------------------------------------------------")
    print("False Positives: " + str(len(set(minutes_double_check_any) & set(negatives1 + negatives2))))
    print("------------------------------------------------------------------")
    print("False Negatives: " + str(120 - len(set(minutes_double_check_any) & set(positives))))
    print("------------------------------------------------------------------")
    if minutes_double_check_any:
        print("Time until first detection: " + str((minutes_double_check_any[0] - 3600) / 60))
        print("------------------------------------------------------------------")
    print("False positives after fixing it: " + str(len(set(minutes_double_check_any) & set(negatives2))))
    print("------------------------------------------------------------------")

    print("----------------------TESTING DOUBLE_CHECK-BOTH WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_double_check_both)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_double_check_both)*span)
    print("------------------------------------------------------------------")
    print("True Positives: " + str(len(set(minutes_double_check_both) & set(positives))))
    print("------------------------------------------------------------------")
    print("True Negatives: " + str(120 - len(set(minutes_double_check_both) & set(negatives1 + negatives2))))
    print("------------------------------------------------------------------")
    print("False Positives: " + str(len(set(minutes_double_check_both) & set(negatives1 + negatives2))))
    print("------------------------------------------------------------------")
    print("False Negatives: " + str(120 - len(set(minutes_double_check_both) & set(positives))))
    print("------------------------------------------------------------------")
    if minutes_double_check_both:
        print("Time until first detection: " + str((minutes_double_check_both[0] - 3600) / 60))
        print("------------------------------------------------------------------")
    print("False positives after fixing it: " + str(len(set(minutes_double_check_both) & set(negatives2))))
    print("------------------------------------------------------------------")

    print("----------------------TESTING DOUBLE_FORECAST-C WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_double_forecast_check_c)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_double_forecast_check_c)*span)
    print("------------------------------------------------------------------")
    print("True Positives: " + str(len(set(minutes_double_forecast_check_c) & set(positives))))
    print("------------------------------------------------------------------")
    print("True Negatives: " + str(120 - len(set(minutes_double_forecast_check_c) & set(negatives1 + negatives2))))
    print("------------------------------------------------------------------")
    print("False Positives: " + str(len(set(minutes_double_forecast_check_c) & set(negatives1 + negatives2))))
    print("------------------------------------------------------------------")
    print("False Negatives: " + str(120 - len(set(minutes_double_forecast_check_c) & set(positives))))
    print("------------------------------------------------------------------")
    if minutes_double_forecast_check_c:
        print("Time until first detection: " + str((minutes_double_forecast_check_c[0] - 3600) / 60))
        print("------------------------------------------------------------------")
    print("False positives after fixing it: " + str(len(set(minutes_double_forecast_check_c) & set(negatives2))))
    print("------------------------------------------------------------------")

    print("----------------------TESTING DOUBLE_FORECAST-NC WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_double_forecast_check_nc)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_double_forecast_check_nc)*span)
    print("------------------------------------------------------------------")
    print("True Positives: " + str(len(set(minutes_double_forecast_check_nc) & set(positives))))
    print("------------------------------------------------------------------")
    print("True Negatives: " + str(120 - len(set(minutes_double_forecast_check_nc) & set(negatives1 + negatives2))))
    print("------------------------------------------------------------------")
    print("False Positives: " + str(len(set(minutes_double_forecast_check_nc) & set(negatives1 + negatives2))))
    print("------------------------------------------------------------------")
    print("False Negatives: " + str(120 - len(set(minutes_double_forecast_check_nc) & set(positives))))
    print("------------------------------------------------------------------")
    if minutes_double_forecast_check_nc:
        print("Time until first detection: " + str((minutes_double_forecast_check_nc[0] - 3600) / 60))
        print("------------------------------------------------------------------")
    print("False positives after fixing it: " + str(len(set(minutes_double_forecast_check_nc) & set(negatives2))))
    print("------------------------------------------------------------------")

    print("----------------------TESTING DOUBLE_FORECAST-ANY WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_double_forecast_check_any)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_double_forecast_check_any)*span)
    print("------------------------------------------------------------------")
    print("True Positives: " + str(len(set(minutes_double_forecast_check_any) & set(positives))))
    print("------------------------------------------------------------------")
    print("True Negatives: " + str(120 - len(set(minutes_double_forecast_check_any) & set(negatives1 + negatives2))))
    print("------------------------------------------------------------------")
    print("False Positives: " + str(len(set(minutes_double_forecast_check_any) & set(negatives1 + negatives2))))
    print("------------------------------------------------------------------")
    print("False Negatives: " + str(120 - len(set(minutes_double_forecast_check_any) & set(positives))))
    print("------------------------------------------------------------------")
    if minutes_double_forecast_check_any:
        print("Time until first detection: " + str((minutes_double_forecast_check_any[0] - 3600) / 60))
        print("------------------------------------------------------------------")
    print("False positives after fixing it: " + str(len(set(minutes_double_forecast_check_any) & set(negatives2))))
    print("------------------------------------------------------------------")

    print("----------------------TESTING DOUBLE_FORECAST-BOTH WITH " + case + " ----------------------")
    print("----------------------Minutes with anomalies: ----------------------")
    print(minutes_double_forecast_check_both)
    print("----------------------Number of minutes with anomalies: ----------------------")
    print(len(minutes_double_forecast_check_both)*span)
    print("------------------------------------------------------------------")
    print("True Positives: " + str(len(set(minutes_double_forecast_check_both) & set(positives))))
    print("------------------------------------------------------------------")
    print("True Negatives: " + str(120 - len(set(minutes_double_forecast_check_both) & set(negatives1 + negatives2))))
    print("------------------------------------------------------------------")
    print("False Positives: " + str(len(set(minutes_double_forecast_check_both) & set(negatives1 + negatives2))))
    print("------------------------------------------------------------------")
    print("False Negatives: " + str(120 - len(set(minutes_double_forecast_check_both) & set(positives))))
    print("------------------------------------------------------------------")
    if minutes_double_forecast_check_both:
        print("Time until first detection: " + str((minutes_double_forecast_check_both[0] - 3600) / 60))
        print("------------------------------------------------------------------")
    print("False positives after fixing it: " + str(len(set(minutes_double_forecast_check_both) & set(negatives2))))
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


def test_regression(regression_name, file, config_file, auto_reset=False, auto_constant=False):
    minutes_alarm = []
    previous_regression = 0
    constant = 0;

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

            if auto_constant:
                auto_constant = False
                constant = ITCT - regression_val

            regression_val += constant

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
