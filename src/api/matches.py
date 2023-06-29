from datetime import datetime
from chessdotcom import get_player_game_archives
import requests
from pymongo import InsertOne

from src.mongo.connection import MongoConnection


class MatchArchive:

    def __init__(self):
        super().__init__()
        self.conn = MongoConnection("delo_dm_project", "Xhemil1960")
        self.players = self.conn.db["players"]
        self.chess_profiles = self.conn.db["chess_profiles"]
        self.matches = self.conn.db["matches"]

    def get_matches(self):

        all_players = self.players.find({"username": {"$ne": None}})
        for player in all_players:
            username = player.get("username")
            print(f"{username} ----------------------")
            single_data = get_player_game_archives(username).json
            urls = single_data.get("archives")

            player_matches = []
            print(f"Number of archives --> {len(urls)}")
            for url in urls:
                data = requests.get(url).json()
                games = data.get("games")

                for g in games:

                    game = g.copy()

                    game["username"] = username

                    game.pop("end_time", None)
                    game.pop("tcn", None)
                    game.pop("initial_setup", None)
                    game.pop("fen", None)

                    if game.get("pgn"):
                        info = self.get_info(game.get("pgn"))

                        game["start_time"] = info.get("start_time")
                        game["end_time"] = info.get("end_time")
                        game["duration"] = info.get("duration")

                        game.pop("pgn", None)

                    player_matches.append(game)

            if len(player_matches) > 0:
                insert_data = [InsertOne(match) for match in player_matches]
                self.matches.bulk_write(insert_data)
                print(f"total --> {len(insert_data)} matches ")
            else:
                print("no matches found")

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

        return {
            "start_time": start_datetime.isoformat(),
            "end_time": end_datetime.isoformat(),
            "duration": duration
        }


if __name__ == "__main__":
    MatchArchive().get_matches()
