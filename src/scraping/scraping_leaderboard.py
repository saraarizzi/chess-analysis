import datetime
import time

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

from scraper import Scraper
from src.mongo.connection import MongoConnection

# from airflow.providers.sqlite.hooks.sqlite import SqliteHook


class LeaderboardScraper(Scraper):
    def __init__(self):
        super().__init__()
        self.conn = MongoConnection("sara-dm-project", "9zc0Kfy9M644W1YD")
        self.players = self.conn.db["players"]
        self.page_players = None
        self.iter_player = None

    def scrape_leaderboard(self, url):

        self.driver.get(url)
        self.driver.maximize_window()

        if self.exists("ready-to-play-banner-close", By.CLASS_NAME):
            self.driver.find_element(By.CLASS_NAME, "ready-to-play-banner-close").click()

        for i in range(4):
            section = self.driver.find_element(By.ID, "view-master-players")
            list_section = section.find_element(By.CLASS_NAME, "post-preview-list-component")
            self.page_players = list_section.find_elements(By.CLASS_NAME, "post-author-component")
            k = 0
            for player in self.page_players:
                k += 1
                self.iter_player = player
                while True:
                    try:
                        obj = {}

                        text = self.iter_player.text.split("\n")

                        obj["title"] = text[0][:2]
                        obj["fullname"] = text[0][3:].strip()

                        spl = text[1].split("|")
                        obj["rank"] = int(spl[1].replace("#", "").strip())
                        obj["leaderboard_rating"] = int(spl[0].strip())

                        obj["country"] = text[2]

                        obj["username"] = self.iter_player.get_dom_attribute("data-username")
                        # obj["uuid"] = self.iter_player.get_dom_attribute("data-user-uuid")

                        avatar = self.iter_player.find_element(By.CLASS_NAME, "post-author-avatar")
                        link = avatar.get_attribute("href")
                        info_desc_fide = self.get_description(link)
                        obj["bio"] = info_desc_fide[0]
                        obj["fide_id"] = int(info_desc_fide[1])

                        self.insert(obj)

                        print(f"{obj.get('fullname')} --> updated")

                    # except StaleElementReferenceException:
                    except Exception as e:
                        print(e)
                        self.driver.refresh()

                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.ID, "view-master-players"))
                        )

                        section = self.driver.find_element(By.ID, "view-master-players")
                        list_section = section.find_element(By.CLASS_NAME, "post-preview-list-component")
                        self.page_players = list_section.find_elements(By.CLASS_NAME, "post-author-component")
                        print("-------------------------REFRESH---------------------------")
                        print(k)
                        self.page_players = self.page_players[k - 1:]
                        self.iter_player = self.page_players[0]
                        continue

                    break

            self.driver.find_element(By.XPATH, ".//a[@aria-label='Next Page']").click()

        print("DONE")

    def insert(self, obj):
        try:
            before = self.players.find_one({'fide_id': obj['fide_id']})

            update_result = self.players.update_one({'fide_id': obj['fide_id']}, {'$set': obj}, upsert=True)

            if bool(update_result.modified_count):
                after = self.players.find_one({'fide_id': obj['fide_id']})

                rank_before = before.get("rank")
                rank_after = after.get("rank")

                rating_before = before.get("leaderboard_rating")
                rating_after = after.get("leaderboard_rating")

                rows = []
                updated = False
                now = datetime.datetime.now().isoformat()
                if rank_before != rank_after:
                    updated = True
                    rows.append((str(after.get("_id")), after.get("fide_id"), rank_before, rank_after, 'leaderboard_rank', now))

                if rating_before != rating_after:
                    updated = True
                    rows.append((str(after.get("_id")), after.get("fide_id"), rating_before, rating_after, 'leaderboard_rating', now))

                if updated:
                    pass

                    # sqlite_hook = SqliteHook()
                    # target_fields = ['id_player', 'fullname', 'value_before', 'value_after', 'field', 'date_update']
                    # sqlite_hook.insert_rows(table='LogUpdatePlayer', rows=rows, target_fields=target_fields)

        except Exception as e:
            print(e)

    def exists(self, el, by):
        try:
            self.driver.find_element(by, el)
        except NoSuchElementException:
            return False
        return True

    def get_description(self, link):
        description = ""

        self.driver.get(link)

        section_id = self.driver.find_element(By.CLASS_NAME, "master-players-description")
        socials = section_id.find_element(By.CLASS_NAME, "master-players-social").find_element(By.CLASS_NAME, "master-players-social-links")
        id_data = socials.find_element(By.XPATH, ".//a[@class='master-players-social-fide master-players-social-link']").get_attribute("href")
        id_data_split = id_data.split("/")
        fide_id = id_data_split[len(id_data_split)-1]

        section_bio = self.driver.find_element(By.CLASS_NAME, "post-view-component")
        list_p = section_bio.find_element(By.CLASS_NAME, "post-view-content").find_elements(By.TAG_NAME, "p")[:5]

        for p in list_p:
            description += " " + p.text

        time.sleep(2)

        self.driver.back()

        return description, fide_id


if __name__ == "__main__":
    LeaderboardScraper().scrape_leaderboard("https://www.chess.com/players")