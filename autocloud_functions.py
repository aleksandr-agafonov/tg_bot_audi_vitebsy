import requests
import pandas as pd
from datetime import datetime
import asyncio


url = 'https://api.aaa24.ru/api/'
login = 'Ruslan'
password = '1994Ru'
salon = '1994'
target_call_string = 'Целевой'
client_name = 'Ауди Центр Витебский'


# параметры для авторизации
auth_params = {
    'login': login,
    'password': password,
    'salon': salon
}


# считает звонки
async def get_autocloud_calls(date_from, date_to):
    result_dict = dict()
    page = 1
    df_list = []
    # получаем токен
    try:
        req = requests.get(url + 'token/', params=auth_params)
        token = req.json()['result']['token']
    except:
        print('не удалось поулчить токен')
        return 'не удалось поулчить токен'

    while True:
        params = {
            'from': date_from,
            'to': date_to,
            'page': page
        }

        headers = {
            'Authorization': 'Bearer ' + token
        }
        # получаем звонки
        try:
            req = requests.get(url + 'calls/', params=params, headers=headers)
            df = pd.DataFrame(req.json()['result'])
            df_list.append(df)
            page += 1
        except:
            break

    try:
        final_calls_df = pd.concat(df_list)
        # целевые звонки: тотал и по площадкам
        target_calls_total = \
            final_calls_df[final_calls_df['tags'].str.contains(target_call_string)]['from'].nunique()

        target_calls_autoru = \
            final_calls_df[final_calls_df['tags'].str.contains(target_call_string) & (final_calls_df['site'] == 'autoru')]['from'].nunique()

        target_calls_avito = \
            final_calls_df[final_calls_df['tags'].str.contains(target_call_string) & (final_calls_df['site'] == 'avito')]['from'].nunique()

        target_calls_drom = \
            final_calls_df[final_calls_df['tags'].str.contains(target_call_string) & (final_calls_df['site'] == 'drom')]['from'].nunique()

        result_dict['target_calls_total'] = target_calls_total
        result_dict['target_calls_autoru'] = target_calls_autoru
        result_dict['target_calls_avito'] = target_calls_avito
        result_dict['target_calls_drom'] = target_calls_drom

    except ValueError:
        print('Нет звонков')
        result_dict['target_calls_total'] = 0
        result_dict['target_calls_autoru'] = 0
        result_dict['target_calls_avito'] = 0
        result_dict['target_calls_drom'] = 0

    return result_dict


# асинхронная функция для сбора звонков из Автоклауда
async def async_get_autocloud_calls(date_from, date_to):
    return await get_autocloud_calls(date_from, date_to)

#a = asyncio.run(async_get_autocloud_calls('2021-10-01', '2021-10-11'))


# отчет по минимальной цене
def get_competitors():
    start_time = datetime.now()
    try:
        req = requests.get(url + 'token/', params=auth_params)
        token = req.json()['result']['token']
    except:
        print('не удалось поулчить токен')
        return 'не удалось поулчить токен'

    if token:

        headers = {
            'Authorization': 'Bearer ' + token
        }

        params = {
            'page': 1,
            'blocking': 0,
            'page_size': 120  # максимальный размер выборки в ответе
        }

        ad_ids = []  # сюда кладем id объвлений
        result_list = []  # сюда кладем финальный словарь
        # поулчаем список объявлений
        try:
            req = requests.get(url + 'cars/', params=params, headers=headers)
        except Exception as e:
            print('Ошибка:', e)
            return 'error'

        for id in req.json()['result']:
            ad_ids.append(id['id'])

        for ad_id in ad_ids:
            prices_params = {
            'id': ad_id
            }

            req = requests.get(url + 'prices/', params=prices_params, headers=headers)
            clients_ad = req.json()['result']
            competitors = clients_ad['analyze']

            # убираем объявления клиентов из списка
            competitors = [client for client in competitors if client['salon_name'] != client_name]
            # сортируем конкурентов по цене
            competitors = sorted(competitors, key=lambda price: price['price'])

            if len(competitors) == 0:
                continue
            else:
                # инициируем словарь и набиваем его результатами
                result_dict = dict()
                result_dict['Марка'] = clients_ad['mark']
                result_dict['Модель'] = clients_ad['model']
                result_dict['Модификация'] = clients_ad['modif']
                result_dict['Комплектация'] = clients_ad['comp']
                result_dict['Цена в салоне Ауди Центр Витебский с учетом скидок'] = clients_ad['price']

                if clients_ad['price'] > competitors[0]['price']:
                    result_dict['Минимальная цена на авто.ру'] = competitors[0]['price']
                    result_dict['Разница'] = clients_ad['price'] - competitors[0]['price']
                    result_dict['Салон, размещающий а/м с самой низкой ценой'] = competitors[0]['salon_name']
                else:
                    result_dict['Минимальная цена на авто.ру'] = clients_ad['price']
                    result_dict['Разница'] = 0
                    result_dict['Салон, размещающий а/м с самой низкой ценой'] = client_name

                result_list.append(result_dict)

    df = pd.DataFrame(result_list)
    df.to_excel('конкуренты.xlsx')
    finish_time = datetime.now()
    print('обработка заняла: ', finish_time - start_time)
    return 'ok'

#get_competitors()
# a = get_autocloud_calls('2021-10-01', '2021-10-05')
# print(a)
