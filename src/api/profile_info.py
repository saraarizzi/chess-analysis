# Data Acquisition: 1° step
# Getting master data about player's profile from chess.com platform

from chessdotcom import get_player_profile
import pandas as pd
from datetime import datetime
from pymongo import UpdateOne
from src.mongo.connection import MongoConnection


class ProfileUpdater:

    def __init__(self):
        super().__init__()
        self.conn = MongoConnection()
        self.players = self.conn.db["players"]

    def update_profiles(self):

        all_data = []

        all_players = self.players.find({"username": {"$ne": None}})
        for player in all_players:
            username = player.get("username")
            single_data = get_player_profile(username).json.get("player")
            single_data["username"] = username
            all_data.append(single_data)

        df_format = pd.DataFrame.from_dict(all_data, orient='columns')

        df_format["joined"] = df_format["joined"].apply(
            lambda x: datetime.fromtimestamp(x).isoformat())

        df_format = df_format.rename(
            columns={'avatar': 'avatar', 'player_id': 'player_id',
                     '@id': 'link_profile', 'url': 'url', 'name': 'name',
                     'username': 'username', 'title': 'title',
                     'followers': 'followers', 'country': 'country',
                     'location': 'location', 'last_online': 'last_online',
                     'joined': 'joined', 'status': 'status',
                     'is_streamer': 'streamer', 'verified': 'verified',
                     'league': 'league', 'twitch_url': 'twitch_url'}
        )

        df_format = df_format.fillna("replaceWithNone")
        df_format.loc[df_format.avatar == "replaceWithNone", 'avatar'] = None
        df_format.loc[df_format.league == "replaceWithNone", 'league'] = None
        df_format.loc[df_format.twitch_url == "replaceWithNone", 'twitch_url'] = None

        # drop columns
        df_format.drop(["player_id", "link_profile", "name", "country", "location", "last_online", "title"], axis=1, inplace=True)

        all_profiles = df_format.to_dict('records')

        try:
            upsert_data = [
                UpdateOne({'username': x['username']}, {'$set': x}, upsert=False) for x in all_profiles
            ]
            self.players.bulk_write(upsert_data)

        except Exception as e:
            print(e)


if __name__ == "__main__":
    ProfileUpdater().update_profiles()
