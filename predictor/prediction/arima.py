from statsmodels.tsa.arima_model import ARIMA
from numpy import around
from api_calls.general_api_calls import adapt_time_series


# It generates the forecast for a timeseries
# series: a timeseries where the algorithm will get trained and will generate the forecast
# p: parameter of AR (auto regressive)
# d: parameter to difference the timeseries
# q: parameter of MA (moving average)
# trend: 'nc' = no constant | 'c' = constant
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

    return around(forecast_result)


def get_forecast_array(params, time_series, forecast_time):
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
