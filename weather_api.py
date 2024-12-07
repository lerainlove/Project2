import requests
from pydantic import BaseModel, Field, ValidationError


class WeatherDetails(BaseModel):
    temperature: float = Field(..., alias='Temperature')
    humidity: int = Field(..., alias='RelativeHumidity')
    wind_speed: float = Field(..., alias='WindSpeed')
    precipitation: float = Field(..., alias='Precipitation')


class WeatherApi:
    def __init__(self, token: str) -> None:
        self.__token = token
        self.__base_url = 'http://dataservice.accuweather.com'

    def __fetch_data(self, endpoint: str, parameters: dict) -> dict:
        parameters['apikey'] = self.__token
        url = f'{self.__base_url}/{endpoint}'

        try:
            response = requests.get(url, params=parameters)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            raise ValueError(f'Ошибка запроса: {error}')
        except ValueError:
            raise ValueError('Ошибка при обработке ответа JSON.')

    def __get_location_key_by_coordinates(self, latitude_value: float, longitude_value: float) -> str:
        endpoint = 'locations/v1/cities/geoposition/search'
        parameters = {'q': f'{latitude_value},{longitude_value}'}
        location_data = self.__fetch_data(endpoint, parameters)
        return location_data.get('Key')

    def __get_location_key_by_city_name(self, city_name: str) -> str:
        endpoint = f'locations/v1/cities/search'
        parameters = {
            'q': city_name,
        }
        location_data = self.__fetch_data(endpoint, parameters)

        return location_data and location_data[0].get('Key')

    def __fetch_weather_data(self, location_key: str) -> dict:
        endpoint = f'currentconditions/v1/{location_key}'
        parameters = {'details': 'true'}
        return self.__fetch_data(endpoint, parameters)[0]

    def __parse_weather_response(self, location_key: str) -> WeatherDetails:
        weather_data = self.__fetch_weather_data(location_key)

        try:
            parsed_weather_data = {
                'Temperature': weather_data['Temperature']['Metric']['Value'],
                'RelativeHumidity': weather_data['RelativeHumidity'],
                'WindSpeed': weather_data['Wind']['Speed']['Metric']['Value'],
                'Precipitation': weather_data['PrecipitationSummary']['Precipitation']['Metric']['Value']
            }
            return WeatherDetails(**parsed_weather_data)
        except ValidationError as error:
            raise ValueError(f'Ошибка валидации данных о погоде: {error}')

    def get_weather_by_city(self, city_name: str) -> WeatherDetails:
        return self.__parse_weather_response(self.__get_location_key_by_city_name(city_name))

    def get_weather_by_coords(self, latitude_value: float, longitude_value: float) -> WeatherDetails:
        return self.__parse_weather_response(self.__get_location_key_by_coordinates(latitude_value, longitude_value))
