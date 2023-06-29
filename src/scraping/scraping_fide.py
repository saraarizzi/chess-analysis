import time
from datetime import datetime

from selenium.webdriver.common.by import By

from src.mongo.connection import MongoConnection
from src.scraping.scraper import Scraper

FIDE_LINK = 'https://www.fide.com/'


class FIDEScraper(Scraper):

    def __init__(self):
        super().__init__()
        self.conn = MongoConnection("mik_dm_project", "Spindox!99")
        self.players = self.conn.db["players"]

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
            time.sleep(1)
            table = self.driver.find_element(By.XPATH, '//*[@id="table_results"]/tbody')
            for tr in table.find_elements(By.XPATH, '//*[@id="table_results"]/tbody/tr'):
                dict_tmp = {}
                lista_tmp = []
                for td in tr.find_elements(By.XPATH, ".//td"):
                    lista_tmp.append(td.text)
                dict_tmp['standard_fide_rating'] = int(lista_tmp[4].strip())
                dict_tmp['rapid_fide_rating'] = int(lista_tmp[5].strip())
                dict_tmp['blitz_fide_rating'] = int(lista_tmp[6].strip())
                dict_tmp['birth_year'] = lista_tmp[7].strip()
                dict_tmp['fide_id'] = id_player
                self.insert(dict_tmp)
                lista_tmp.clear()
            self.driver.find_element(By.XPATH, '//*[@id="dyn1"]').clear()

        print("DONE")

    def insert(self, obj):
        try:
            before = self.players.find_one({'fide_id': obj['fide_id']})

            update_result = self.players.update_one({'fide_id': obj['fide_id']}, {'$set': obj}, upsert=False)

            if bool(update_result.modified_count):
                after = self.players.find_one({'fide_id': obj['fide_id']})

                std_before = before.get("standard_fide_rating")
                std_after = after.get("standard_fide_rating")

                rapid_before = before.get("rapid_fide_rating")
                rapid_after = after.get("rapid_fide_rating")

                blz_before = before.get("blitz_fide_rating")
                blz_after = after.get("blitz_fide_rating")

                rows = []
                updated = False
                now = datetime.now().isoformat()
                if std_before != std_after:
                    updated = True
                    rows.append((str(after.get("_id")), after.get("fide_id"), std_before, std_after, 'std_fide', now))

                if rapid_before != rapid_after:
                    updated = True
                    rows.append((str(after.get("_id")), after.get("fide_id"), rapid_before, rapid_after, 'rapid_fide', now))

                if blz_before != blz_after:
                    updated = True
                    rows.append((str(after.get("_id")), after.get("fide_id"), blz_before, blz_after, 'blz_fide', now))

                if updated:
                    pass

                    # sqlite_hook = SqliteHook()
                    # target_fields = ['id_player', 'fullname', 'value_before', 'value_after', 'field', 'date_update']
                    # sqlite_hook.insert_rows(table='LogUpdatePlayer', rows=rows, target_fields=target_fields)

        except Exception as e:
            print(e)


if __name__ == "__main__":
    FIDEScraper().scrape_fide()
