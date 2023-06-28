from selenium import webdriver
from selenium.webdriver.chrome.service import Service


class Scraper:
    def __init__(self):
        self.driver = self.__setup_driver()

    def __setup_driver(self):
        path = "driver/chromedriver"
        service_object = Service(path)
        d = webdriver.Chrome(service=service_object)
        return d
