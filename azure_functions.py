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
    start_date = datetime.now()

    # меняем маркированные символы на латиницу
    calltags_string = r"1С: Отдел продаж автомобилей', 'Кредит', 'Покупка конкретного ТС (новые)', 'Покупка модели (новые)', 'Покупка ТС без уточнения (новые)', 'Продажа', 'Модель"
    query = query.replace('{tags}', calltags_string, 1)

    connector = pyodbc.connect(driver_string)
    connector.timeout = 30
    cursor = connector.cursor()

    try:
        # получаем расходы
        cursor.execute(query)
        row_data = cursor.fetchone()
        print(row_data)

        try:
            unique_calls_cpl = round(row_data[3] / row_data[1])
        except:
            unique_calls_cpl = 0


        try:
            target_calls_cpl = round(row_data[3] / row_data[2])
        except:
            target_calls_cpl = 0

        # кладем все что получили в словарь
        stat_dict = dict()
        stat_dict['date'] = row_data[0]
        stat_dict['unique_calls'] = row_data[1]
        stat_dict['target_calls'] = row_data[2]
        stat_dict['adcost'] = row_data[3]
        stat_dict['max_hour'] = row_data[4]
        stat_dict['unique_calls_cpl'] = unique_calls_cpl
        stat_dict['target_calls_cpl'] = target_calls_cpl

        end_date = datetime.now()
        print('Время обработки запроса: ', end_date - start_date)

        return stat_dict
    except Exception as e:
        print(e)
        return 'error'
    finally:
        connector.close()

# test_query = open(r'ppc_sql\ppc_yesterday_stat.sql').read()
# print(get_stat(test_query))
