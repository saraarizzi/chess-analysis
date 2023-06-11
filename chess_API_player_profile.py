#Data Acquistion: 1° step
#Getting master data about player's profile from chess.com platform

from chessdotcom import get_player_profile
import pandas as pd
import pprint
from datetime import datetime
from pymongo import MongoClient, UpdateOne
printer = pprint.PrettyPrinter()

players_list = []
all_data = []

host = "cluster0.kah64fo.mongodb.net/?retryWrites=true&w=majority"
username = "delo_dm_project"  # os.getenv("MONGO_USER")
password = "Xhemil1960"
my_client = MongoClient(f"mongodb+srv://{username}:{password}@{host}")

db = my_client.chess
collection = db.players
db = my_client.chess
collection = db.players
cursor = collection.find({})
for document in cursor:
 document = document["username"]
 players_list.append(document)

for player in players_list:
    single_data = get_player_profile(player).json
    all_data.append(single_data)
df_format = pd.DataFrame.from_dict(pd.json_normalize(all_data), orient='columns')
printer.pprint(all_data)

df_format["last_date_online"] = df_format["player.last_online"].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d'))
df_format["last_time_online"] = df_format["player.last_online"].apply(lambda x: datetime.fromtimestamp(x).strftime('%H:%M:%S'))
df_format = df_format.rename(columns = {'player.avatar': 'avatar', 'player.player_id': 'player_id',
                                        'player.@id': 'link_profile', 'player.url': 'URL', 'player.name': 'name',
                                        'player.username': 'username', 'player.title': 'title',
                                        'player.followers': 'followers', 'player.country': 'country',
                                        'player.location': 'location', 'player.last_online': 'last_online',
                                        'player.joined': 'joined', 'player.status': 'status',
                                        'player.is_streamer': 'streamer', 'player.verified': 'verified',
                                        'player.league': 'league', 'player.twitch_url': 'twitch_url'})

df_format["username"] = df_format["username"].str.capitalize()
all_profiles = df_format.to_dict('records')
printer.pprint(all_profiles)
print(len(all_profiles))

try:
  upsert_data = [UpdateOne({'player_id': x['player_id']}, {'$set': x}, upsert=True) for x in all_profiles]
  my_client["chess"]["profiles"].bulk_write(upsert_data)

except Exception as e:
        print(e)