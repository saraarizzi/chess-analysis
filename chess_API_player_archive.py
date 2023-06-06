from chessdotcom import get_player_game_archives
import pprint
import requests
from pymongo import MongoClient
from datetime import datetime

printer = pprint.PrettyPrinter()

host = "cluster0.kah64fo.mongodb.net/?retryWrites=true&w=majority"
username = "delo_dm_project"  # os.getenv("MONGO_USER")
password = "Xhemil1960"
my_client = MongoClient(f"mongodb+srv://{username}:{password}@{host}")

players_list = []
all_data = []

db = my_client.chess
collection = db.players
db = my_client.chess
collection = db.players
cursor = collection.find({})
for document in cursor:
    document = document["username"]
    players_list.append(document)

for player in players_list:
    single_data = get_player_game_archives(player).json
    url = single_data['archives'][-2]
    data = requests.get(url).json()
    games = data['games']

    # printer.pprint(type(games[0]['pgn']))
    for g in games:
        # printer.pprint(i)
        pgn = g.get('pgn')
        if pgn is not None:
            start_index = pgn.find('Date')
        else:
            continue
        date = pgn[start_index + 6:start_index + 16]
        el = g.pop('pgn')
        g['date'] = date
        all_data.append(g)
        # printer.pprint(date)
        #printer.pprint("FINE DEL CICLO")


printer.pprint(all_data)
print(len(all_data))

