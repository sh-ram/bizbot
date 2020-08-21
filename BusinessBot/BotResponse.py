"""
    Describe all sent message.
"""

from typing import List

from jobs import Job



# rate_ = 'Показать курс по валюте: /rate'
# notifications_ = 'Действующие подписки: /notifications'
# notify = 'Настроить оповещения: /notify'
time_format = 'Формат: <b>чч[:мм[:сс]]</b>'
currency_format = 'Формат: <b>[валюта|индекс]</b>'
cancel = 'Отменить: /cancel'
help = 'Список команд: /help'

time_invalid = 'Время некорректно.\n'\
              f'{help}'

conv_time = 'Укажите время оповещения.\n' \
            f'{time_format}\n\n'          \
            f'{cancel}'

conv_currency = 'Укажите валюту.\n'\
                f'{currency_format}'

conv_time_invalid = 'Время некорректно.\n'  \
                    'Введите заново.\n'     \
                    f'{time_format}\n\n'    \
                    f'{cancel}'

conv_cancel = 'Отмена успешна.\n\n'\
              f'{help}'

request_accept = 'Принято.\n'\
                'Обрабатываю...'

jobs_disabled = 'Оповещения по валютам отключены!\n\n'\
                f'{help}'


def currency_invalid(message: str) -> str:
    return  f'Значение "{message}" некорректно.\n'\
            f'{help}'

def conv_currency_invalid(message: str) -> str:
    return  f'Значение "{message}" некорректно.\n\n'\
            f'{currency_format}\n'  \
            f'{cancel}'

def job_stated(currency_index: str, time: str) -> str:
    return  f'Оповещение по валюте <b>{currency_index}</b> ' \
            f'на <b>{time}</b> успешно установлено!\n'     \
            f'{help}'

def job_disabled(currency: str) -> str:
    return  f'Оповещение по валюте <b>{currency}</b> '\
            f'успешно отключено!\n\n'\
            f'{help}'

def job_empty(currency_index: str) -> str:
    return f'Оповещение по валюте <b>{currency_index}</b> '\
            'не активно.\n\n'   \
           f'Настроить: /notify{currency_index}\n\n'\
           f'{help}'

def notifications(job_queue: List[Job]) -> str:
    if job_queue:
        jobs = tuple()
        for job in job_queue:
            jobs += (f'<b>Валюта</b>: {job.currency_index}\n'       \
                     f'<b>Время</b>: {job.time}\n'                  \
                     # f'<b>Дни</b>: {job.days}\n'                  \
                     f'<i>Изм.</i>: /notify{job.currency_index}\n'  \
                     f'<i>Откл.</i>: /notify{job.currency_index}_',)
        text = 'Для чата назначены следующие оповещения:\n\n'
        text += '\n——————————\n'.join(jobs)
        text += f'\n\nОткл. все: /notify_\n\n{help}'
        return text
    return f'Для чата <i>нет</i> оповещений!\n\n{help}'

def rate(currency: List) -> str:
    index, name, unit, rate = range(4)
    return f'<b>{currency[name]}</b>\n'\
           f'Курс по ЦБ: <b>{currency[rate]}&#x20bd;</b> '\
           f'за {currency[unit]} <b>{currency[index]}</b>\n\n'\
           f'Настроить оповещение: /notify{currency[index]}\n' \
           f'{help}'


