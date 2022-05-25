from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.utils import ChromeType

import os

class Driver:
    def __init__(self):
        if os.name == 'nt':
            self.os = 'Windows'
        else:
            self.os = 'Linux'
        self.config()
    
    def config(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument('--no-sandbox')  #bypass OS security model
        self.chrome_options.add_argument('--disable-dev-shm-usage') #overcome limited resource problems
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)	

    def open_browser(self):
        if self.os == 'Windows':
            self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=self.chrome_options)
        elif self.os == 'Linux':
            service = Service(ChromeDriverManager().install())                                # Chrome
            # service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()) # Chromium
            self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
    
    def close_browser(self):
        self.driver.quit()
    
