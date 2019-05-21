from statsmodels.tsa.arima_model import ARIMA
from api_calls.general_api_calls import get_time_series


def get_arima_forecast():
    series = get_time_series()

    return 1