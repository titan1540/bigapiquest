import requests
import sys

import distance
import geocoder


def get_nearest_organization(toponym):
    search_api_server = 'https://search-maps.yandex.ru/v1/'
    api_key = 'dda3ddba-c9ea-4ead-9010-f43fbc15c6e3'

    address_ll = ','.join(str(x) for x in geocoder.get_ll(toponym))
    address_spn = ','.join(str(x) for x in geocoder.get_spn(toponym))

    search_params = {
        'apikey': api_key,
        'lang': 'ru_RU',
        'll': address_ll,
        'spn': address_spn,
        'type': 'biz',
        'rspn': 1,
    }

    try:
        response = requests.get(search_api_server, params=search_params)

        if not response:
            print('Ошибка выполнения запроса:')
            print(search_params)
            print('Http статус:', response.status_code, '(', response.reason, ')')
            sys.exit(1)
    except:
        print('Запрос не удалось выполнить. Проверьте наличие сети Интернет.')
        sys.exit(1)

    # Преобразуем ответ в json-объект
    json_response = response.json()

    organizations = json_response['features']

    answer = (1e100, None, None)
    my_ll = geocoder.get_ll(toponym)

    for organization in organizations:
        pos = organization['geometry']['coordinates']

        if distance.lonlat_distance(my_ll, pos) <= 50 and \
                distance.lonlat_distance(my_ll, pos) <= answer[0]:
            answer = distance.lonlat_distance(my_ll, pos), \
                     organization['properties']['CompanyMetaData']['name'], pos

    return answer[1], answer[2]
