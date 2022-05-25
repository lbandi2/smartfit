from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
from selenium.webdriver.chrome.options import Options

# https://trainingymapp.com/webtouch/horario ---> classes grid

grab_date = datetime.now().strftime("%d/%m/%Y (%H:%M:%S.%f)")
grab_time = datetime.now().strftime("%#I:%M %p")
grab_timestamp = int(time.time())
url = "https://smartfit.com.co/sedes/exito-country"
file = 'web_page.html'

def main():
    grab_homepage()
    grab_schedule()
    assistance_list, now_assistance, min_assistance, max_assistance, updated_at = get_data(get_today_schedule())
    today_schedule = get_today_schedule()
    classes_today, classes_tomorrow, classes_list = get_today_classes()

    print(today_schedule)
    # print(schedule)

    for x in assistance_list:
        print(x)

    print(now_assistance)
    print(min_assistance)
    print(max_assistance)
    print(updated_at)

    for x in classes_today:
        print(x)

    for x in classes_tomorrow:
        print(x)

    for x in classes_list:
        print(x)


def grab_page(url, file, sleep):
    path = "C:\\Program Files (x86)\\chromedriver.exe"
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(path, options=chrome_options)
    driver.get(url)

    time.sleep(sleep)

    with open(file, 'w', encoding="utf-8") as file:
        file.write(driver.page_source)

    driver.quit()

def grab_homepage():
    print('Downloading webpage..')
    grab_page(url, file, 0)

def time_object(hour):
    hour_obj = datetime.strptime(f'{str(hour)}', '%H').time()  # create time object
    time_obj = datetime.combine(datetime.now(), hour_obj)      # combine today's date with time object

    return time_obj

def military_time(string):
    obj = datetime.strptime(string, '%H:%M').time()
    return obj

def get_ts(string):
    obj = datetime.strptime(string, '%H:%M').time()
    time_obj = datetime.combine(datetime.now(), obj)
    return time_obj.timestamp()

def time_as_string(time_obj):
    time_string = time_obj.strftime("%#H:%M")

    return time_string

def replace_str(text, dic):
    """Replace text based on dict provided."""

    for i, j in dic.items():
        text = text.replace(i, j)
    return text

def add_days(offset):
    days = [
        'Lunes',
        'Martes',
        'Miércoles',
        'Jueves',
        'Viernes',
        'Sábado',
        'Domingo'
    ]

    weekday = datetime.now() + timedelta(days=offset)

    # return days[weekday.weekday()]
    return weekday.weekday()

def get_today_classes():
    with open('classes.html', 'r', encoding="utf-8") as content:
        classes_html = BeautifulSoup(content, 'html.parser')

    # all_days = classes_html.find('div', class_="caja-horario reservaCalendario2 hidden-xs ng-scope")
    all_days = classes_html.find_all('div', class_="columnaHorasDiferentes")

    day = classes_html.find_all('div', class_="contenedor-item-dia maximoEntre5")
    
    # if len(day) == 0:
    #     day = classes_html.find_all('div', class_="contenedor-item-dia maximoEntre7")

    day_class = classes_html.find_all('div', class_="div item-dias altoNormal alturaActividadesReservas ng-scope grisClaro")

    days = [
        'Lunes',
        'Martes',
        'Miércoles',
        'Jueves',
        'Viernes',
        'Sábado',
        'Domingo'
    ]

    classes = []
    prev_time = military_time('05:00')

    weekday = datetime.now().weekday()
    offset = 0
    # dow = weekday + offset

    for x in day_class:

        hora = x.find('span', class_="label etiquetaHora ng-binding")
        hora = hora.text.strip().split(' / ')
        inicio, fin = hora[0], hora[1]

        clase_salon = x.find_all('span', class_="label padding-0 controlarPalabra ng-binding")
        for index, y in enumerate(clase_salon):
            if index == 0:
                clase = y.text
            elif index == 1:
                salon = y.text.replace('sala: ', '').title()

        monitor = x.find('span', class_="label2 padding-0 controlarPalabra ng-binding").text.strip().replace('Monitor: ', '').capitalize()

        # print(prev_time.hour - military_time(inicio).hour <= 0, clase)

        if prev_time.hour - military_time(inicio).hour <= 0:
            prev_time = military_time(fin)
        else:
            offset += 1
            prev_time = military_time(fin)


        # print(f"GRAB: {inicio}-{fin} - {clase} - {salon} - {monitor}")
        if clase != 'SMART FIT GO':
            if offset == weekday:
                dow = f'Hoy'
            else:
                dow = days[add_days(offset)]

            if 'trx' in clase.lower():
                clase = f"{clase.split(' ')[0].capitalize()} {clase.split(' ')[1].upper()}"
            else:
                clase = clase.title()

            classes.append(
                [
                    add_days(offset), 
                    inicio, 
                    fin, 
                    clase, 
                    salon, 
                    monitor,
                    get_ts(inicio),
                    get_ts(fin)
                ]
            )
            # prev_time = military_time(fin)
            prev_offset = offset

    classes_today = []
    classes_tomorrow = []

    # counter = 0

    prev_weekday = 0
    for x in classes:

        if x[0] == weekday and prev_weekday <= 0:
            classes_today.append(x)
        elif x[0] == weekday + 1 and prev_weekday <= 1:
            classes_tomorrow.append(x)
        else:
            prev_weekday += 1

    # print(classes_today)
    # print(classes_tomorrow)
    # print(classes)
    return classes_today, classes_tomorrow, classes
    # for x in classes:
    #     print(x)

def grab_schedule():
    with open('web_page.html', 'r', encoding="utf-8") as content:
        smartfit_html = BeautifulSoup(content, 'html.parser')
    webpage_classes = smartfit_html.find_all('div', class_="full-modal__container")

    for x in webpage_classes:
        if x.find('iframe') != None:
            classes = x.find('iframe')
            print('Downloading sessions grid..')
            grab_page(classes['src'], 'classes.html', 10)

def get_today_schedule():
    # gets fields corresponding to gym bussiness hours
    with open('web_page.html', 'r', encoding="utf-8") as content:
        smartfit_html = BeautifulSoup(content, 'html.parser')
    webpage_schedule = smartfit_html.find_all('div', class_="ScheduleList__item")

    schedule = []
    day_today = datetime.now().isoweekday()
    today = []

    for x in webpage_schedule:
        days = [
            'Lunes',
            'Martes',
            'Miércoles',
            'Jueves',
            'Viernes',
            'Sábado',
            'Domingo'
        ]
        days_abrev = [
            'Lun',
            'Mar',
            'Mie',
            'Jue',
            'Vie',
            'Sáb',
            'Dom'
        ]

        day = x.find('div', class_='ScheduleList__item_weebday').text
        for index, y in enumerate(days_abrev):
            if y == day:
                day = index  # replace day as string for weekday as number
        times = x.find('div', class_='ScheduleList__item_schedule').text.replace("h", "").split(" - ")
        # schedule.append(
        #     [
        #         day,
        #         time_object(times[0]),
        #         time_object(times[1])
        #     ]
        # )

        if day_today == day:
            day = time_object(times[0]).weekday()
            today.append(
                [
                    # day,
                    days[time_object(times[0]).weekday()],
                    # time_object(times[0]),
                    time_as_string(time_object(times[0])),
                    # time_object(times[1]),
                    time_as_string(time_object(times[1]))
                ]
            )

    # for x in schedule:
    #     print(x)
    # print(today)
    return today


def get_data(lst):
    start = lst[0][1].split(':')[0]
    end = lst[0][2].split(':')[0]

    day_today = datetime.now().isoweekday()
    day_gym = ''

    start_time = time_object(start)
    end_time = time_object(end)

    with open('web_page.html', 'r', encoding="utf-8") as content:
        smartfit_html = BeautifulSoup(content, 'html.parser')

    # gets fields corresponding to assistance
    webpage_assistance = smartfit_html.find('div', class_="js--graphic")
    updated_at = webpage_assistance.find('p', class_='text Text--tiny').text.split(":\n")[1].strip()
    print(updated_at)
    graphs_list = webpage_assistance.find_all('div', class_="Graph__item")

    assistance_list = []
    now_assistance = ''
    min_assistance = []
    minimum_assistance = ''
    lowest = 0
    max_assistance = []
    maximum_assistance = ''
    highest = 0

    now_hour = time_object(datetime.now().hour)
    prev_hour = 4

    for index, x in enumerate(graphs_list):

        # get hour and assistance %
        item_hour = x.find('div', class_="Graph__label").text.replace("h", "").replace("Aora", "Now")
        item_assistance = 100 - int(
            x.find('div', class_="Graph__bar__inner")["style"].replace("height: ", "").replace("%;", ""))

        # find hour 'Now" and replace it with actual hour
        if item_hour == 'Now':
            item_hour = int(prev_hour) + 1

        if item_hour != 'Now':
            prev_hour = item_hour
            item_hour = time_object(item_hour)

        if now_hour == item_hour:
            now_assistance = f"\nAhora ({grab_time}): {item_assistance}%"

        # get lowest and highest assistance for the day
        if start_time <= item_hour <= end_time:
            if lowest == 0:
                min_assistance.append(
                    [
                        time_as_string(item_hour),
                        item_assistance
                    ]
                )
                lowest = item_assistance
            else:
                if lowest > item_assistance:
                    min_assistance[0] = [
                        time_as_string(item_hour),
                        item_assistance
                    ]
                    lowest = item_assistance

            if highest == 0:
                max_assistance.append(
                    [
                        time_as_string(item_hour),
                        item_assistance
                    ]
                )
                highest = item_assistance
            else:
                if highest < item_assistance:
                    max_assistance[0] = [
                        time_as_string(item_hour),
                        item_assistance
                    ]
                    highest = item_assistance

            assistance_list.append(
                [
                    time_as_string(item_hour),
                    item_assistance
                ]
            )

            minimum_assistance = f"Horario ideal ({min_assistance[0][0]}): {min_assistance[0][1]}%"
            maximum_assistance = f"Horario a evitar ({max_assistance[0][0]}): {max_assistance[0][1]}%"

    return assistance_list, now_assistance, minimum_assistance, maximum_assistance, updated_at


if __name__ == '__main__':
    main()


