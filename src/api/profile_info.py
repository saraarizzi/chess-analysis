# Data Acquistion: 1° step
# Getting master data about player's profile from chess.com platform

from chessdotcom import get_player_profile
import pandas as pd
from datetime import datetime
from pymongo import UpdateOne
from src.mongo.connection import MongoConnection


class ProfileUpdater:

    def __init__(self):
        super().__init__()
        self.conn = MongoConnection("delo_dm_project", "Xhemil1960")
        self.players = self.conn.db["players"]
        self.chess_profiles = self.conn.db["chess_profiles"]

    def update_profiles(self):

        all_data = []

        all_players = self.players.find({"username": {"$ne": None}})
        for player in all_players:
            username = player.get("username")
            single_data = get_player_profile(username).json.get("player")
            all_data.append(single_data)

        df_format = pd.DataFrame.from_dict(all_data, orient='columns')

        df_format["last_online"] = df_format["last_online"].apply(
            lambda x: datetime.fromtimestamp(x).isoformat())
        df_format["joined"] = df_format["joined"].apply(
            lambda x: datetime.fromtimestamp(x).isoformat())

        df_format = df_format.rename(
            columns={'avatar': 'avatar', 'player_id': 'chess_player_id',
                     '@id': 'link_profile', 'url': 'URL', 'name': 'name',
                     'username': 'username', 'title': 'title',
                     'followers': 'followers', 'country': 'country',
                     'location': 'location', 'last_online': 'last_online',
                     'joined': 'joined', 'status': 'status',
                     'is_streamer': 'streamer', 'verified': 'verified',
                     'league': 'league', 'twitch_url': 'twitch_url'}
        )

        df_format["username"] = df_format["username"].str.capitalize()

        df_format = df_format.fillna("replaceWithNone")
        df_format.loc[df_format.avatar == "replaceWithNone", 'avatar'] = None
        df_format.loc[df_format.name == "replaceWithNone", 'name'] = None
        df_format.loc[df_format.location == "replaceWithNone", 'location'] = None
        df_format.loc[df_format.league == "replaceWithNone", 'league'] = None
        df_format.loc[df_format.twitch_url == "replaceWithNone", 'twitch_url'] = None
        all_profiles = df_format.to_dict('records')

        try:
            upsert_data = [
                UpdateOne({'chess_player_id': x['chess_player_id']}, {'$set': x}, upsert=True) for x in all_profiles
            ]
            self.chess_profiles.bulk_write(upsert_data)

        except Exception as e:
            print(e)


if __name__ == "__main__":
    ProfileUpdater().update_profiles()
