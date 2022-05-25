from datetime import datetime, timedelta
import calendar
import locale
import os

def dir_exist(path):
    return os.path.isdir(path)

def make_dir(path):
    if not dir_exist(path):
        try:
            os.mkdir(path)
        except OSError:
            print (f"Failed to create directory '{path}'")
        else:
            print(f"Creating folder '{path}'..")

def get_os():
    if os.name == 'nt':
        return 'Windows'
    return 'Linux'

def to_percentage(item, max_value):
    return int(100 * float(item)/float(max_value))

def as_time(string):
    try:
        obj = datetime.strptime(string, '%H:%M').time()
    except ValueError:
        raise ValueError("Time must be in format: HH:MM")
    else:
        return obj

# def get_ts(string):
#     obj = datetime.strptime(string, '%H:%M').time()
#     time_obj = datetime.combine(datetime.now(), obj)
#     return time_obj.timestamp()

def get_ts(string, weekday):
    today = datetime.now().weekday()
    dif = weekday - today
    date = datetime.now() + timedelta(days=dif)
    obj = datetime.strptime(string, '%H:%M').time()
    time_obj = datetime.combine(date, obj)
    return time_obj.timestamp()

def time_as_string(time_obj):
    time_string = time_obj.strftime("%#H:%M")

    return time_string

def add_days(offset):
    weekday = datetime.now() + timedelta(days=offset)

    return weekday.weekday()

def replace_str(text, dic):
    """Replace text based on dict provided."""

    for i, j in dic.items():
        text = text.replace(i, j)
    return text

def get_days(language='es', abbr=False):
    rep = {
        '.': '',
        'é': 'e',
        'á': 'a'
    }
    if language == 'en':
        if get_os() == 'Windows':
            locale.setlocale(locale.LC_ALL, 'en_US')
        else:
            locale.setlocale(locale.LC_ALL, 'en_US.utf-8')
    elif language == 'es':
        if get_os() == 'Windows':
            locale.setlocale(locale.LC_ALL, 'es_MX')
        else:
            locale.setlocale(locale.LC_ALL, 'es_MX.utf-8')
    if abbr is True:
        days = [replace_str(x.lower(), rep) for x in list(calendar.day_abbr)]
        return days
    days = [replace_str(x.lower(), rep) for x in list(calendar.day_name)]
    return days

def to_english(text, abbr=False):
    english = get_days('en', abbr)
    spanish = get_days('es', abbr)
    if '/' in text.lower():
        text = text.lower().split('/')[0]
    for index, day in enumerate(spanish):
        if text.lower() in day:
            return english[index]
    else:
        raise ValueError(f"Could not translate day '{text}' to english")

def get_weekday_text(index, language='es'):
    rep = {
        "é": "e",
        "á": "a"
    }

    if language == 'en':
        if get_os() == 'Windows':
            locale.setlocale(locale.LC_ALL, 'en_US')
        else:
            locale.setlocale(locale.LC_ALL, 'en_US.utf-8')
    elif language == 'es':
        if get_os() == 'Windows':
            locale.setlocale(locale.LC_ALL, 'es_MX')
        else:
            locale.setlocale(locale.LC_ALL, 'es_MX.utf-8')
    try:
        return replace_str(calendar.day_name[index].lower(), rep)
    except IndexError:
        print("Day must be between 0-6")
