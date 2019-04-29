import sys
import requests


def get_toponym(address):
    geocoder_api_server = 'http://geocode-maps.yandex.ru/1.x/'

    geocoder_params = {
        'geocode': address,
        'format': 'json',
    }

    try:
        response = requests.get(geocoder_api_server, params=geocoder_params)

        if not response:
            print('Ошибка выполнения запроса:')
            print(geocoder_params)
            print('Http статус:', response.status_code, '(', response.reason, ')')
            sys.exit(1)
    except:
        print('Запрос не удалось выполнить. Проверьте наличие сети Интернет.')
        sys.exit(1)

    # Преобразуем ответ в json-объект
    json_response = response.json()

    # Получаем первый топоним из ответа геокодера.
    toponym = json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']

    return toponym


def get_ll(toponym):
    toponym_coodrinates = toponym['Point']['pos']

    toponym_longitude, toponym_lattitude = map(float, toponym_coodrinates.split(' '))

    return toponym_longitude, toponym_lattitude


def get_spn(toponym):
    down, left = map(float, toponym['boundedBy']['Envelope']['lowerCorner'].split())
    up, right = map(float, toponym['boundedBy']['Envelope']['upperCorner'].split())

    return abs(up - down), abs(right - left)


def get_address(toponym):
    text = toponym['metaDataProperty']['GeocoderMetaData']['text']
    try:
        postcode = toponym['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
    except Exception:
        postcode = ''
    return text, postcode
