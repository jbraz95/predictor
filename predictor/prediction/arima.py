from statsmodels.tsa.arima_model import ARIMA
from api_calls.general_api_calls import adapt_time_series


# It generates the forecast for a timeseries
# series: a timeseries where the algorithm will get trained and will generate the forecast
# p: parameter of AR (auto regressive)
# d: parameter to difference the timeseries
# q: parameter of MA (moving average)
# trend: 'nc' = no constant | 'c' = constant
# Output: The forecast of that series
def get_arima_forecast(series, p, d, q, forecast, trend):
    series_adapted = adapt_time_series(series)[1]
    forecast_result = []

    try:
        model = ARIMA(series_adapted, order=(p, d, q))
        model_fit = model.fit(disp=0, trend=trend)
        forecast_result = model_fit.forecast(steps=forecast)[0]
    except Exception as e:
        print(e)
        print(forecast_result)
    finally:
        if len(forecast_result) == 0:
            length = len(series_adapted) - 1
            forecast_result = [series_adapted[length]] * forecast

    forecast_result = clean_arima(forecast_result)

    return forecast_result


# This function will "clean" our arima information. As in this case our metric never decreases we will remove datapoints
# where the forecast is lower than the initial point. Like this we will not see forecast that predict a lower value
# for the metric than the actual value. We will also round the values as the metric should only show integers and not
# float values.
# forecast: the forecast of a metric
# Output: a clean and rounded version of the forecast
def clean_arima(forecast):
    og_value = forecast[0]
    previous_val = forecast[0]
    new_forecast = []
    for value in forecast:
        if value < og_value:
            new_forecast.append(round(previous_val))
        else:
            new_forecast.append(round(value))
            previous_val = value

    return new_forecast


# This function will output the forecast given the parameters, the time series and the time to be forecasted.
# params: the parameters for the arima prediction
# time_series: the time series to study past behaviour and predict future values
# forecast_time: how much time we are going to forecast in the future
# output: and array of arrays. Each array will have the trend of it (constant/no constant) and the values
def get_forecasts_array(params, time_series, forecast_time):
    forecasts = []
    for param in params:
        name = list(param.keys())[0]
        p = param[name]['p']
        d = param[name]['d']
        q = param[name]['q']
        trend = param[name]['trend']

        arima = get_arima_forecast(series=time_series, p=p, d=d, q=q, forecast=forecast_time,
                                   trend=trend)

        set_arima = [trend, arima]
        forecasts.append(set_arima)

    return forecasts
