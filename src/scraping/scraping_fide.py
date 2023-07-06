import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from src.mongo.connection import MongoConnection
from src.scraping.scraper import Scraper

FIDE_LINK = 'https://www.fide.com/'


class FIDEScraper(Scraper):

    def __init__(self):
        super().__init__()
        self.conn = MongoConnection()
        self.players = self.conn.db["players"]
        self.ratings = self.conn.db["ratings"]

    def scrape_fide(self):

        cursor = self.players.find({})

        fide_id_list = []

        for document in cursor:
            document_id = document["fide_id"]
            fide_id_list.append(document_id)

        self.driver.get(FIDE_LINK)
        self.driver.maximize_window()  # access to webpage

        # clicking on RATINGS button
        ratings_button = self.driver.find_element(
            By.XPATH, '//*[@id="navbarSupportedContent"]/app-shared-client-menu-header/ul/li[2]/a')

        # access to button through XPATH and click()
        ratings_button.click()

        # Defining a function to search & scrape name
        for id_player in fide_id_list:
            self.driver.find_element(By.XPATH, '//*[@id="dyn1"]').send_keys(id_player)
            search_button = self.driver.find_element(By.XPATH, '//*[@id="search_form_buton"]/i')
            search_button.click()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="table_results"]/tbody'))
            )
            table = self.driver.find_element(By.XPATH, '//*[@id="table_results"]/tbody')
            for tr in table.find_elements(By.XPATH, '//*[@id="table_results"]/tbody/tr'):
                dict_tmp = {}
                lista_tmp = []
                for td in tr.find_elements(By.XPATH, ".//td"):
                    lista_tmp.append(td.text)
                dict_tmp['standard_fide_rating'] = int(lista_tmp[4].strip())
                dict_tmp['rapid_fide_rating'] = int(lista_tmp[5].strip())
                dict_tmp['blitz_fide_rating'] = int(lista_tmp[6].strip())
                dict_tmp['fide_id'] = id_player
                dict_tmp["date"] = datetime.now().date().isoformat()
                self.ratings.insert_one(dict_tmp)
                lista_tmp.clear()
            self.driver.find_element(By.XPATH, '//*[@id="dyn1"]').clear()

        print("DONE")


if __name__ == "__main__":
    FIDEScraper().scrape_fide()
