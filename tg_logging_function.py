import requests


bot_name = '@audi_vitebsky_log_bot'
token = '2033942671:AAHEy2LSYZ_RJXHhMuO0ekyM4LAd66qYPqI'
method = 'sendMessage'
url = f'https://api.telegram.org/bot{token}/{method}'
chat_id_list = [1673451611]  # сюда добавляем список id пользователей на которых будет рассылка


def logger_bot(message):
    params = {
        'chat_id': chat_id_list[0],
        'text': message
    }

    requests.get(url, params=params)

#get_data('message')
# бот для логгирования ошибок
