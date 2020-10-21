from datetime import datetime as dt


def datetoday(date):
    return 'Сегодня' if date.date() == dt.today().date() else date.strftime('%d %B')


def time(date):
    return date.strftime('%H:%M')


custom_filters = {
    'date': datetoday,
    'time': time
}
