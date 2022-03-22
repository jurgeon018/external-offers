from datetime import datetime as dt, timedelta


def datetoday(date):
    return 'Сегодня' if date.date() == dt.today().date() else date.strftime('%d %B')


def time(date):
    return date.strftime('%H:%M')


def seconds_to_time(seconds):
    return str(timedelta(seconds=int(seconds)))


custom_filters = {
    'date': datetoday,
    'time': time,
    'seconds_to_time': seconds_to_time,
}
