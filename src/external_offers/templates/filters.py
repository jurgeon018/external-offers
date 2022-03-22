from datetime import datetime as dt, timedelta


def datetoday(date):
    return 'Сегодня' if date.date() == dt.today().date() else date.strftime('%d %B')


def time(date):
    return date.strftime('%H:%M')


def seconds_to_time(seconds: str) -> str:
    if seconds is None:
        return '0:00:00'
    if isinstance(seconds, bool):
        return 'NaN'
    try:
        seconds = float(seconds)
    except ValueError:
        return 'NaN'
    if isinstance(seconds, str):
        return 'NaN'
    return str(timedelta(seconds=int(seconds)))


custom_filters = {
    'date': datetoday,
    'time': time,
    'seconds_to_time': seconds_to_time,
}
