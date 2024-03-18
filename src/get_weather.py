import openmeteo_requests
import json
import requests_cache
import pandas as pd
from retry_requests import retry


class WeatherFetcher:
    """Class to fetch weather data from OpenMeteo API. 
    It uses the openmeteo_requests library to make the requests and the requests_cache library to cache the responses. 
    It also uses the retry_requests library to retry the requests in case of failure. 
    The parameters are read from a config file. 
    The class has a method to get the current weather and the hourly weather forecast. 
    The data is returned as pandas dataframes. The class also has a method to convert the time from UTC to the local timezone."""
    def __init__(self, latitude, longitude, current, hourly, timezone, forecast_days, forecast_hours, expire_after, n_retries, backoff_factor):
        self.latitude = latitude
        self.longitude = longitude
        self.current = current
        self.hourly = hourly
        self.timezone = timezone
        self.forecast_days = forecast_days
        self.forecast_hours = forecast_hours
        cache_session = requests_cache.CachedSession('.cache', expire_after = expire_after)
        retry_session = retry(cache_session, retries = n_retries, backoff_factor = backoff_factor)
        self.openmeteo = openmeteo_requests.Client(session = retry_session)

    def get_weather(self):
        """Method to get the current weather and the hourly weather forecast."""
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "current": self.current,
            "hourly": self.hourly,
            "timezone": self.timezone,
            "forecast_days": self.forecast_days,
            "forecast_hours": self.forecast_hours
        }
        responses = self.openmeteo.weather_api(url, params=params)
        response = responses[0]
        current = response.Current()
        current_temperature_2m = current.Variables(0).Value()
        current_apparent_temperature = current.Variables(1).Value()
        current_is_day = current.Variables(2).Value()
        current_is_day = True if int(current_is_day) == 1 else False
        current_precipitation = current.Variables(3).Value()
        current_data = {
            "date": self.convert_time(current.Time()),
            "temperature_2m": current_temperature_2m,
            "apparent_temperature": current_apparent_temperature,
            "is_day": current_is_day,
            "precipitation": current_precipitation
        }
        current_dataframe = pd.DataFrame(data = current_data, index=[0])
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_apparent_temperature = hourly.Variables(1).ValuesAsNumpy()
        hourly_precipitation = hourly.Variables(3).ValuesAsNumpy()
        hourly_uv_index = hourly.Variables(4).ValuesAsNumpy()
        hourly_data = {"date": pd.date_range(
            start = self.convert_time(hourly.Time()),
            end = self.convert_time(hourly.TimeEnd()),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )}
        hourly_data["temperature_2m"] = hourly_temperature_2m
        hourly_data["apparent_temperature"] = hourly_apparent_temperature
        hourly_data["precipitation_probability"] = hourly_precipitation
        hourly_data["uv_index"] = hourly_uv_index
        hourly_dataframe = pd.DataFrame(data = hourly_data)
        return current_dataframe, hourly_dataframe

    def convert_time(self, time):
        """Method to convert the time from UTC to the local timezone."""
        return pd.to_datetime(time, unit = "s").tz_localize("UTC").tz_convert(self.timezone).strftime('%Y-%m-%d %H:%M')



if __name__ == "__main__":
    #open config file and read the parameters
    with open("config/baires_config.json", "r") as file:
        config = json.load(file)
    
    weather_params = config.get("params", {})
    cache_params = config.get("cache", {})

    #create a WeatherFetcher object
    weather_fetcher = WeatherFetcher(
        latitude = weather_params.get("latitude", 0),
        longitude = weather_params.get("longitude", 0),
        current = weather_params.get("current", ["temperature_2m"]),
        hourly = weather_params.get("hourly", ["temperature_2m"]),
        timezone = weather_params.get("timezone", "GMT"),
        forecast_days = weather_params.get("forecast_days", 1),
        forecast_hours = weather_params.get("forecast_hours", 6),
        expire_after = cache_params.get("expire_after", 3600),
        n_retries = cache_params.get("n_retries", 1),
        backoff_factor = cache_params.get("backoff_factor", 0.2)
    )

    #get the weather data
    current, hourly = weather_fetcher.get_weather()
    print(current)
    print(hourly)