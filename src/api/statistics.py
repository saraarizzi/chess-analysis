# Data Acquisition: 2° step
# Getting transactional data about actual and best ratings in different ways of playing chess.
# The main categories are: rapid, bullet, blitz

from chessdotcom import get_player_stats
from datetime import datetime
from src.mongo.connection import MongoConnection


class StatisticsUpdater:

    def __init__(self):
        super().__init__()
        self.conn = MongoConnection("delo_dm_project", "Xhemil1960")
        self.players = self.conn.db["players"]
        self.statistics = self.conn.db["statistics"]

    def update_stats(self):

        now_date = datetime.now().date().isoformat()
        all_data = []

        all_players = self.players.find({"username": {"$ne": None}})
        for player in all_players:
            username = player.get("username")
            single_data = get_player_stats(username).json.get("stats")
            all_data.append(single_data)

            single_data["username"] = username
            single_data["date"] = now_date

            self.remove_keys(single_data)

            self.statistics.insert_one(single_data)

        print("DONE")

    def remove_keys(self, player):
        player.pop("chess960_daily", None)
        player.pop("puzzle_rush", None)


if __name__ == "__main__":
    StatisticsUpdater().update_stats()
