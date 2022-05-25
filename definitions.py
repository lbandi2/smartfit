from datetime import datetime
from selenium_driver import Driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import json
import time
from utils import to_percentage
from db import DB
from working_hours import WorkingHours
from classes_schedule import Classes

class Sede:
    def __init__(self, url, filename, filename_classes, language='es'):
        self.page = Page(url, filename, filename_classes, language)
        self.classes_filename = filename_classes
        self.language = language
        self.name = self.page.name
        self.address = self.page.address
        self.working_hours = self.page.working_hours
        self.features = self.page.features
        self.assistance = self.page.assistance
        self.classes_today = self.page.classes_today
        self.classes_tomorrow = self.page.classes_tomorrow
        self.all_classes = self.page.all_days
        self.save_json_data()
        self.db = DB()
        self.db.insert(self.data_as_dict())
        self.db.disconnect()

    def data_as_dict(self):
        data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M"),
            "name": self.name,
            "address": self.address,
            "working_hours": self.working_hours,
            "features": self.features,
            "assistance": self.assistance,
            "classes": self.page.all_days_json
        }
        return data

    def save_json_data(self):
        with open("./data/json_data.json", "w") as f:
            json.dump(self.data_as_dict(), f, indent=4)

class Page:
    def __init__(self, url, filename, filename_classes, language, sleep=0):
        self.url = url
        self.filename = filename
        self.filename_classes = filename_classes
        self.language = language
        self.sleep = sleep
        self.driver = Driver()
        self.main()

    def main(self):
        self.open_webpage(self.url, self.sleep)
        self.save_webpage(self.filename)
        soup = self.open_saved_webpage()
        self.name = self.find_name()
        self.features = self.find_features()
        self.working_hours = self.find_opening_hours()
        self.address = self.find_address()
        self.assistance = self.find_live_assistance()
        self.classes_webpage_url = self.find_classes_webpage_url()
        self.parse_classes_webpage()
        self.close_browser()

    def open_webpage(self, url, sleep):
        self.driver.open_browser()
        self.driver.driver.get(url)
        time.sleep(sleep)

    def save_webpage(self, filename):
        with open(f'./data/{filename}', 'w', encoding="utf-8") as f:
            f.write(self.driver.driver.page_source)

    def close_browser(self):
        self.driver.close_browser()

    def open_saved_webpage(self):
        with open(f"./data/{self.filename}", "rb") as f:
            return BeautifulSoup(f, features="lxml")

    def click_element(self, tag, html_element, wait_time=0):
        if self.find_element(tag, html_element):
            element = self.driver.driver.find_element(tag, html_element)
            element.click()
            time.sleep(wait_time)

    def click_element_multiple(self, tag, html_element, wait_time):
        while True:
            if not self.find_element(tag, html_element):
                break
            self.click_element(html_element, wait_time)

    def is_element(self, tag, html_element):
        try:
            self.driver.driver.find_element(tag, html_element)
        except NoSuchElementException:
            return False
        return True

    def find_element(self, tag, html_element):
        try:
            return self.driver.driver.find_element(tag, html_element)
        except NoSuchElementException:
            return None

    def find_name(self):
        soup = self.open_saved_webpage()
        table = soup.find('div', ('class', ("show-locations-page__header__body__content")))
        name = table.find('h1')
        return name.text

    def find_address(self):
        soup = self.open_saved_webpage()
        table = soup.find('div', ('class', ("show-locations-page__address")))
        return table.text.replace('VER MAPA', '')

    def find_opening_hours(self):  ## convert list to detailed list by day
        soup = self.open_saved_webpage()
        table = soup.find('div', ('class', ("show-locations-page__opening-hours")))
        items = table.find_all('p')
        working_hours = []
        day = '-'
        hours = '-'
        for index, item in enumerate(items):
            if index % 2 == 0:
                day = item.text.replace("  ", " ").replace("á", "a").replace("é", "e").lower()
            else:
                hours = item.text
                working_hours.append([day, hours])
        schedule = WorkingHours(working_hours, self.language).working_hours
        return schedule

    def find_features(self):
        soup = self.open_saved_webpage()
        table = soup.find('div', ('class', ("show-locations-page__benefits__slider")))
        items = table.find_all('div', ('class', ("show-locations-page__benefits__slider__item__name")))
        items_text = [x.text for x in items]
        return items_text

    def find_live_assistance(self):
        zone = self.find_element(By.CLASS_NAME, "show-locations-page__class-details")
        asistencia = zone.find_element(By.TAG_NAME, 'button')
        if asistencia.text == 'VER GRÁFICO DE ASISTENCIA':
            print("Click on Grafico de Asistencia")
            asistencia.click()
            time.sleep(2)
        graph = self.driver.driver.find_element(By.CLASS_NAME, "modal-wrapper__modal").find_element(By.TAG_NAME, "svg").find_element(By.TAG_NAME, "g")
        all_gs = graph.find_elements(By.TAG_NAME, 'g')
        assistance = []
        for index, item in enumerate(all_gs):
            if index < 20:
                continue
            else:
                rect = item.find_element(By.TAG_NAME, 'rect')
                assistance.append(int(rect.get_attribute('height')))

        assistance.append(0) # completes the last hour (22:00)
        maximum = max(assistance)
        assistance = [to_percentage(item, maximum) for item in assistance] # converts graph values to percentage

        hours = [x for x in graph.text.split('\n')]
        assistance_hours = list(zip(hours, assistance))
        zone = self.find_element(By.CLASS_NAME, "modal-wrapper")
        button = zone.find_element(By.TAG_NAME, "button")
        button.click()
        return assistance_hours

    def find_classes_webpage_url(self):
        webpage = "https://trainingymapp.com/webtouch/horario/3174/1"  # comment these 2 lines to use method
        return webpage
        zone = self.find_element(By.CLASS_NAME, "show-locations-page__class-details")
        button = zone.find_elements(By.TAG_NAME, 'button')[1]
        if button.text == 'HORARIO DE CLASES':
            print("Click on Horario de Clases")
            button.click()
            time.sleep(3)
        # classes_webpage = self.driver.driver.find_element(By.TAG_NAME, "iframe").get_attribute("src")

        delay = 30 # seconds
        try:
            # WebDriverWait(self.driver.driver, delay).until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
            WebDriverWait(self.driver.driver, delay).until(EC.visibility_of_element_located((By.TAG_NAME, 'iframe')))
            print("Page loaded!")
        except TimeoutException:
            print("Loading took too much time!")
        else:
            classes_webpage = self.driver.driver.find_element(By.TAG_NAME, "iframe").get_attribute("src")
            if 'trainingymapp' in classes_webpage:
                print(f"Found classes_webpage: {classes_webpage}")
                return classes_webpage
            else:
                raise ValueError(f"Could not find webpage for classes, webpage returned was: {classes_webpage}")

    def parse_classes_webpage(self):
        self.open_webpage(self.classes_webpage_url, 5)
        self.save_webpage(self.filename_classes)
        classes = Classes(self.filename_classes, self.language)
        self.all_days = classes.all_days
        self.classes_today = classes.classes_today
        self.classes_tomorrow = classes.classes_tomorrow
        self.all_days_json = classes.all_days_dict
        self.close_browser()


# locations = 'https://smartfit.com.co/gimnasios'

# base_url = "https://smartfit.com.co/sedes/exito-country"
# filename = 'web_page.html'

# a = Sede(base_url, filename, "classes.html")
# name = a.name
# hours = a.working_hours
# address = a.address
# features = a.features
# assistance = a.assistance
# classes_today = a.classes_today
# classes_tomorrow = a.classes_tomorrow

# print(name)
# print(hours)
# print(address)
# print(features)
# print(assistance)
# print(classes_today)
# print(classes_tomorrow)
