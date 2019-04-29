import requests
import sys


def save_map(map_ll, map_spn=None, map_type='map', point=None):
    map_request = 'http://static-maps.yandex.ru/1.x/'

    ll = ','.join(str(x) for x in map_ll)
    static_params = {
        'll': ll,
        'l': map_type
    }
    if map_spn is not None:
        spn = ','.join(str(x) for x in map_spn)
        static_params['spn'] = spn
    
    if point is not None:
        pt = ','.join(str(x) for x in point)
        static_params['pt'] = pt

    try:
        response = requests.get(map_request, params=static_params)

        if not response:
            print('Ошибка выполнения запроса:')
            print(map_request)
            print('Http статус:', response.status_code, '(', response.reason, ')')
            sys.exit(1)
    except:
        print('Запрос не удалось выполнить. Проверьте наличие сети Интернет.')
        sys.exit(1)

    # Запишем полученное изображение в файл.
    map_file = '_map.png'
    try:
        with open(map_file, 'wb') as file:
            file.write(response.content)
    except IOError as ex:
        print('Ошибка записи временного файла:', ex)
        sys.exit(2)
