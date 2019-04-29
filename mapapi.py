import requests
import sys


def save_map(map_ll, map_spn=None, map_type='map'):
    ll = ','.join(str(x) for x in map_ll)
    if map_spn is None:
        map_request = 'http://static-maps.yandex.ru/1.x/?ll={ll}&l={map_type}'.format(ll=ll, map_type=map_type)
    else:
        spn = ','.join(str(x) for x in map_spn)
        map_request = 'http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn}&l={map_type}'.format(ll=ll, spn=spn,
                                                                                                map_type=map_type)
    try:
        response = requests.get(map_request)

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
