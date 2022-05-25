from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from utils import get_ts, add_days, get_weekday_text

class Classes:
    def __init__(self, filename, language='es'):
        self.html_source = self.open_file(filename)
        self.language = language
        self.exceptions = ['Smart Fit Go']
        self.offset = 0
        self.weekday = self.get_weekday()
        self.all_days = self.get_all_days()
        self.classes_today = self.get_today()
        self.classes_tomorrow = self.get_tomorrow()
        self.all_days_dict = self.get_all_days_dict()

    def open_file(self, filename):
        try:
            with open(f'./data/{filename}', 'rb') as f:
                soup = BeautifulSoup(f, features="lxml")
                day_class = soup.find_all('div', class_="contenedor-item-dia maximoEntre7")
        except FileNotFoundError as e:
            raise FileNotFoundError("File not found", e)
        else:
            if day_class != [] and day_class is not None:
                return day_class
            raise Exception("File is not valid or HTML structure changed")

    def get_weekday(self, offset=0):
        current_weekday = datetime.now().date()
        return (current_weekday + timedelta(days=offset)).weekday()

    def get_all_days(self):
        lst = []
        for item in self.html_source:
            lst.append(Day(self.get_weekday(self.offset), item, self.exceptions).classes)
            self.offset += 1
        return lst

    def get_today(self):
        lst = []
        for day in self.all_days:
            for item in day:
                if self.get_weekday() == item.weekday:
                    lst.append(item)
        return lst

    def get_tomorrow(self):
        lst = []
        for day in self.all_days:
            for item in day:
                if self.get_weekday(1) == item.weekday:
                    lst.append(item)
        return lst

    def get_all_days_dict(self):
        dict = {}
        for item in self.html_source:
            day = Day(self.get_weekday(self.offset), item, self.exceptions)
            weekday = get_weekday_text(day.weekday, self.language).lower()
            dict[weekday] = day.classes_lst
            self.offset += 1
        return dict


class Day:
    def __init__(self, weekday, bs4_obj, exceptions):
        self.weekday = weekday
        self.bs4_obj = bs4_obj.find_all('div', class_="div item-dias altoNormal alturaActividadesReservas ng-scope grisClaro")
        self.exceptions = exceptions
        self.classes = []
        self.classes_lst = []
        self.get_classes()
        self.get_classes_lst()


    def get_classes(self):
        for item in self.bs4_obj:
            clase = Class(self.weekday, item)
            if clase.clase not in self.exceptions:
                self.classes.append(Class(self.weekday, item))

    def get_classes_lst(self):
        prev_weekday = None
        classes = []
        for item in self.bs4_obj:
            clase = Class(self.weekday, item)
            if clase.clase not in self.exceptions:
                classes.append([
                        clase.weekday, 
                        clase.inicio, 
                        clase.fin,
                        clase.inicio_ts,
                        clase.fin_ts,
                        clase.clase,
                        clase.profesor,
                        clase.salon
                        ])
        self.classes_lst = classes

class Class:
    def __init__(self, weekday, bs4_obj):
        self.weekday = weekday
        self.bs4_obj = bs4_obj
        self.inicio = self.get_times()[0]
        self.fin = self.get_times()[1]
        self.profesor = self.get_teacher()
        self.clase = self.get_class()[0]
        self.salon = self.get_class()[1]
        self.inicio_ts = get_ts(self.inicio, self.weekday)
        self.fin_ts = get_ts(self.fin, self.weekday)

    def get_times(self):
        time = self.bs4_obj.find('span', class_="label etiquetaHora ng-binding")
        time_cleanup = time.text.strip().split(' / ')
        start, end = time_cleanup[0], time_cleanup[1]
        return start, end

    def get_teacher(self):
        teacher = self.bs4_obj.find('span', class_="label2 padding-0 controlarPalabra ng-binding").text.strip().replace('Monitor: ', '').capitalize()
        return teacher.title()

    def get_class(self):
        clase_salon = self.bs4_obj.find_all('span', class_="label padding-0 controlarPalabra ng-binding")
        for index, y in enumerate(clase_salon):
            if index == 0:
                clase = y.text
                if clase.lower().split(' ')[1] in ['trx', 'hiit']:
                    clase = f"{clase.split(' ')[0].capitalize()} {clase.split(' ')[1].upper()}"
                else:
                    clase = clase.title().strip()
            elif index == 1:
                salon = y.text.replace('sala: ', '').title()
        return clase, salon
        
    def get_dow(self):
        return add_days(self.weekday)


# a = Classes("classes.html")
# print(a.all_days_dict)
