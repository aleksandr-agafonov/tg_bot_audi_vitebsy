import pyodbc
from datetime import datetime


server = 'prsunvsu17.database.windows.net'
database = 'mybi-mcqiivs'
username = 'owner-mcqiivs'
password = '5riBokzl5RaR'
driver_string = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' \
                + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password


# функция подключения и чтения из AZURE
def get_stat(query):
    start_time = datetime.now()

    # меняем маркированные символы на латиницу
    calltags_string = r"1С: Отдел продаж автомобилей', 'Кредит', 'Покупка конкретного ТС (новые)', 'Покупка модели (новые)', 'Покупка ТС без уточнения (новые)', 'Продажа', 'Модель"
    query = query.replace('{tags}', calltags_string, 3)

    connector = pyodbc.connect(driver_string)
    connector.timeout = 30
    cursor = connector.cursor()

    # получаем стату
    cursor.execute(query)
    row_data = cursor.fetchone()
    print(row_data, type(row_data), len(row_data))

    stat_dict = dict()
    stat_dict['date'] = row_data[0]
    stat_dict['unique_calls'] = row_data[1]
    stat_dict['target_calls'] = row_data[2]
    stat_dict['adcost'] = round(row_data[3])
    stat_dict['max_hour'] = row_data[4]

    if stat_dict['unique_calls'] == 0:
        stat_dict['unique_calls_cpl'] = 0
    else:
        stat_dict['unique_calls_cpl'] = round(stat_dict['adcost'] / stat_dict['unique_calls'])

    if stat_dict['target_calls'] == 0:
        stat_dict['target_calls_cpl'] = 0
    else:
        stat_dict['target_calls_cpl'] = round(stat_dict['adcost'] / stat_dict['target_calls'])


    if len(row_data) == 9:  # контекст
        stat_dict['target_calls_yandex'] = row_data[5]
        stat_dict['target_calls_google'] = row_data[6]
        stat_dict['adcost_yandex'] = round(row_data[7])
        stat_dict['adcost_google'] = round(row_data[8])

        if stat_dict['target_calls_yandex'] == 0:
            stat_dict['target_calls_yandex_cpl'] = 0
        else:
            stat_dict['target_calls_yandex_cpl'] = round(stat_dict['adcost_yandex'] / stat_dict['target_calls_yandex'])

        if stat_dict['target_calls_google'] == 0:
            stat_dict['target_calls_google_cpl'] = 0
        else:
            stat_dict['target_calls_google_cpl'] = round(stat_dict['adcost_google'] / stat_dict['target_calls_google'])

    #print(stat_dict, len(stat_dict))
    elif len(row_data) == 11:  # тотал
        stat_dict['target_calls_yandex'] = row_data[5]
        stat_dict['target_calls_google'] = row_data[6]
        stat_dict['target_calls_facebook'] = row_data[7]
        stat_dict['adcost_yandex'] = round(row_data[8])
        stat_dict['adcost_google'] = round(row_data[9])
        stat_dict['adcost_facebook'] = round(row_data[10])

        if stat_dict['target_calls_yandex'] == 0:
            stat_dict['target_calls_yandex_cpl'] = 0
        else:
            stat_dict['target_calls_yandex_cpl'] = round(stat_dict['adcost_yandex'] / stat_dict['target_calls_yandex'])

        if stat_dict['target_calls_google'] == 0:
            stat_dict['target_calls_google_cpl'] = 0
        else:
            stat_dict['target_calls_google_cpl'] = round(stat_dict['adcost_google'] / stat_dict['target_calls_google'])

        if stat_dict['target_calls_facebook'] == 0:
            stat_dict['target_calls_facebook_cpl'] = 0
        else:
            stat_dict['target_calls_facebook_cpl'] = round(stat_dict['adcost_facebook'] / stat_dict['target_calls_facebook'])

    end_time = datetime.now()
    print('Обработка заняла:', end_time-start_time)
    connector.close()
    return stat_dict

# test_query = open(r'ppc_sql\ppc_current_week_stat.sql').read()
# get_stat(test_query)
