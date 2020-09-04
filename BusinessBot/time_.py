import datetime


MOSCOW = datetime.timezone(datetime.timedelta(hours=3))

def get_msk(time: tuple) -> datetime:
    '''Return UTC+03 datetime.'''
    hours, minutes, seconds = range(3)
    if isinstance(time, str):
        time = tuple( time.split(':') )
    hours = int(time[hours]) if time[hours] else 0
    minutes = int(time[minutes]) if time[minutes] else 0
    seconds = int(time[seconds]) if time[seconds] else 0
    try:
        time = datetime.time(hours, 
                             minutes, 
                             seconds, 
                             tzinfo=MOSCOW)
    except ValueError as error:
        print('ValueError:', error)
    else:
        return time