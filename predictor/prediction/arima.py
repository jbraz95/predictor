from statsmodels.tsa.arima_model import ARIMA
from numpy import around
from api_calls.general_api_calls import adapt_time_series


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
