"""
Sales Forecasting Module
Time-series forecasting using ARIMA and Prophet models
"""

import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

class SalesForecaster:
    """Time series forecasting for sales data"""
    
    def __init__(self, data, date_col='Date', value_col='Revenue'):
        self.data = data.copy()
        self.date_col = date_col
        self.value_col = value_col
        self.data[date_col] = pd.to_datetime(data[date_col])
        self.data = self.data.sort_values(date_col)
    
    def prepare_time_series(self):
        """Aggregate daily sales"""
        ts = self.data.groupby(self.date_col)[self.value_col].sum().reset_index()
        ts.columns = ['ds', 'y']
        ts['ds'] = pd.to_datetime(ts['ds'])
        return ts
    
    def forecast_arima(self, periods=30, order=(5, 1, 2)):
        """ARIMA forecasting"""
        ts = self.prepare_time_series().set_index('ds')['y']
        try:
            model = ARIMA(ts, order=order)
            results = model.fit()
            forecast = results.get_forecast(steps=periods)
            forecast_df = forecast.conf_int(alpha=0.05).reset_index()
            forecast_df.columns = ['Date', 'Lower', 'Upper']
            forecast_df['Forecast'] = results.fittedvalues.values[-1]
            return forecast_df, results
        except Exception as e:
            print(f"ARIMA Error: {e}")
            return None, None
    
    def forecast_prophet(self, periods=30):
        """Facebook's Prophet forecasting"""
        ts = self.prepare_time_series()
        try:
            model = Prophet(yearly_seasonality=True, weekly_seasonality=True)
            model.fit(ts)
            future = model.make_future_dataframe(periods=periods)
            forecast = model.predict(future)
            forecast_df = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods).reset_index(drop=True)
            forecast_df.columns = ['Date', 'Forecast', 'Lower', 'Upper']
            return forecast_df, model
        except Exception as e:
            print(f"Prophet Error: {e}")
            return None, None
    
    def evaluate_forecast(self, actual, predicted):
        """Model accuracy metrics"""
        mae = mean_absolute_error(actual, predicted)
        rmse = np.sqrt(mean_squared_error(actual, predicted))
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
        return {'MAE': mae, 'RMSE': rmse, 'MAPE': mape}
    
    def generate_forecast(self, periods=30, method='prophet'):
        """Generate complete forecast"""
        if method == 'prophet':
            forecast_df, model = self.forecast_prophet(periods)
        else:
            forecast_df, model = self.forecast_arima(periods)
        
        if forecast_df is not None:
            forecast_df['Method'] = method.upper()
            forecast_df['GeneratedAt'] = pd.Timestamp.now()
            return forecast_df
        return None
