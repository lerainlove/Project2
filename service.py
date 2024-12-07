from weather_api import WeatherDetails


def is_weather_bad(weather: WeatherDetails) -> bool:

    score = 0

    if weather.temperature < -5 or weather.temperature > 35:
        score += 2
    elif -5 <= weather.temperature < 0 or 30 <= weather.temperature <= 35:
        score += 1

    if weather.wind_speed > 70:
        score += 2
    elif 50 <= weather.wind_speed <= 70:
        score += 1

    if weather.precipitation > 90:
        score += 2
    elif 70 <= weather.precipitation <= 90:
        score += 1

    if weather.humidity > 85 and weather.temperature > 30:
        score += 1
    elif weather.humidity < 20 and weather.temperature < 0:
        score += 1

    return score > 3
