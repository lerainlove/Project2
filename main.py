from flask import Flask, render_template, request

from config import Config
from service import is_weather_bad
from weather_api import WeatherApi

app = Flask(__name__)
settings = Config()
weather_service = WeatherApi(settings.api_token)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/check_weather_by_coords', methods=['POST'])
def check_weather_by_coordinates():
    latitude_value = request.form.get('latitude', type=float)
    longitude_value = request.form.get('longitude', type=float)

    if latitude_value is None or longitude_value is None:
        return render_template(
            'error.html',
            error_text='Широта и долгота обязательны для указания',
            back_link='/',
        )

    try:
        weather_data = weather_service.get_weather_by_coords(latitude_value, longitude_value)

        is_weather_unfavorable = is_weather_bad(weather_data)

        return render_template(
            'coords.html',
            temperature=weather_data.temperature,
            humidity=weather_data.humidity,
            wind_speed=weather_data.wind_speed,
            precipitation=weather_data.precipitation,
            is_bad='Да' if is_weather_unfavorable else 'Нет',
        )
    except ValueError:
        return render_template(
            'error.html',
            error_text='Неверные координаты',
            back_link='/',
        )
    except Exception:
        return render_template(
            'error.html',
            error_text='Произошла ошибка | API недоступен',
            back_link='/',
        )


@app.route('/check_weather_by_cities', methods=['POST'])
def check_weather_by_multiple_cities():
    city_start = request.form.get('start_city')
    city_end = request.form.get('end_city')

    try:
        weather_start_city = weather_service.get_weather_by_city(city_start)
        weather_end_city = weather_service.get_weather_by_city(city_end)

        start_city_weather_bad = is_weather_bad(weather_start_city)
        end_city_weather_bad = is_weather_bad(weather_end_city)

        return render_template(
            'cities.html',
            start_city=city_start,
            end_city=city_end,
            start_weather=weather_start_city,
            end_weather=weather_end_city,
            start_is_bad=start_city_weather_bad,
            end_is_bad=end_city_weather_bad,
        )
    except ValueError:
        return render_template(
            'error.html',
            error_text='Неверное название города',
            back_link='/',
        )
    except Exception:
        return render_template(
            'error.html',
            error_text='Произошла ошибка | API недоступен',
            back_link='/',
        )


if __name__ == '__main__':
    app.run(port=8000)
