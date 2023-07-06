from datetime import datetime, timedelta

import numpy as np
from chessdotcom import get_player_game_archives
import requests
from pymongo import InsertOne
import re

from src.mongo.connection import MongoConnection


class MatchArchive:

    def __init__(self):
        super().__init__()
        self.conn = MongoConnection()
        self.players = self.conn.db["players"]
        self.matches = self.conn.db["matches"]

    def check(self):

        cursor = self.matches.find({"duration": {"$lt": 0}})
        for match in cursor:
            print(match.get("start_time"))
            print(match.get("end_time"))

            start_time = datetime.strptime(match.get("start_time"), "%Y-%m-%dT%H:%M:%S")
            end_time = datetime.strptime(match.get("end_time"), "%Y-%m-%dT%H:%M:%S")

            end_time = end_time + timedelta(days=1)
            duration = int((end_time - start_time).total_seconds())

            match["end_time"] = end_time.isoformat()
            match["duration"] = duration

            self.matches.update_one({"_id": match.get("_id")}, {'$set': match}, upsert=False)

        print("DONE")


    def get_matches(self):

        all_players = self.players.find({"username": {"$ne": None}})
        for player in all_players:
            username = player.get("username")
            print(f"{username} ----------------------")
            single_data = get_player_game_archives(username).json
            urls = single_data.get("archives")

            print(f"Number of archives --> {len(urls)}")
            count = 0
            if len(urls) > 30:
                urls = urls[-30:]
                print(f"Rectified number of archives --> {len(urls)}")

            for url in urls:
                count += 1
                data = requests.get(url).json()
                games = data.get("games")

                player_matches = []
                for g in games:

                    game = g.copy()

                    game.pop("end_time", None)
                    game.pop("tcn", None)
                    game.pop("initial_setup", None)
                    game.pop("fen", None)

                    if game.get("pgn"):
                        info = self.get_info(game.get("pgn"))

                        game["start_time"] = info.get("start_time")
                        game["end_time"] = info.get("end_time")
                        game["duration"] = info.get("duration")
                        game["moves"] = info.get("moves")

                        game.pop("pgn", None)

                    player_matches.append(game)

                # insert
                insert_data = [InsertOne(match) for match in player_matches]
                self.matches.bulk_write(insert_data)

                print(f"progressing... {np.round(count/len(urls)*100, 2)} matches inserted")

        print("DONE")

    @staticmethod
    def get_info(game):
        idx = game.find("StartTime")
        start_time = game[idx+11:idx+19]

        idx = game.find("EndTime")
        end_time = game[idx+9:idx+17]

        idx = game.find("Date")
        day = game[idx+8:idx+16]

        start = day + " " + start_time
        end = day + " " + end_time

        start_datetime = datetime.strptime(start, "%y.%m.%d %H:%M:%S")
        end_datetime = datetime.strptime(end, "%y.%m.%d %H:%M:%S")

        duration = int((end_datetime - start_datetime).total_seconds())

        if duration < 0:
            end_datetime = end_datetime + timedelta(days=1)
            duration = int((end_datetime - start_datetime).total_seconds())

        # pgn regex to get match moves
        spl = game.split("\n")
        pgn = spl[len(spl)-2]

        spl = re.sub(r"[{].*?[}]", "split", pgn)

        rs = spl.split("split")
        moves = "".join([el[6:] if ix % 2 == 1 else el for ix, el in enumerate(rs)])

        return {
            "start_time": start_datetime.isoformat(),
            "end_time": end_datetime.isoformat(),
            "duration": duration,
            "moves": moves
        }


if __name__ == "__main__":
    MatchArchive().get_matches()
