#Data Acquistion: 2° step
#Getting transactional data about actual and best ratings in different ways of playing chess.
#The main categories are: rapid, bullet, blitz, daily.
from chessdotcom import get_player_stats
import pandas as pd
import pprint
from datetime import datetime
from pymongo import MongoClient
printer = pprint.PrettyPrinter()

date = datetime.today().strftime('%Y-%m-%d')
all_data = []
players_list = []

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
 doc = document["username"]
 if doc is not None:
    players_list.append(doc)

for player in players_list:
    single_data = get_player_stats(player).json
    all_data.append(single_data)
df_format = pd.DataFrame.from_dict(pd.json_normalize(all_data), orient='columns')
df_format['username'] = players_list
    #.str.capitalize()
df_format['acquisition_date'] = date

#printer.pprint(all_data) #: To visualize the original data from the API call
#print(df_format.columns)
df_format = df_format.rename(columns={'stats.chess_rapid.last.rating': 'rapid_last_rating',
                                      'stats.chess_rapid.best.rating': 'rapid_best_rating',
                                      'stats.chess_rapid.best.game': 'rapid_best_game',
                                      'stats.chess_rapid.record.win': 'rapid_record_win',
                                      'stats.chess_rapid.record.loss': 'rapid_record_loss',
                                      'stats.chess_rapid.record.draw': 'rapid_record_draw',
                                      'stats.chess_bullet.last.rating': 'bullet_last_rating',
                                      'stats.chess_bullet.best.rating': 'bullet_best_rating',
                                      'stats.chess_bullet.best.game': 'bullet_best_game',
                                      'stats.chess_bullet.record.win': 'bullet_record_win',
                                      'stats.chess_bullet.record.loss': 'bullet_record_loss',
                                      'stats.chess_bullet.record.draw': 'bullet_record_draw',
                                      'stats.chess_blitz.last.rating': 'blitz_last_rating',
                                      'stats.chess_blitz.best.rating': 'blitz_best_rating',
                                      'stats.chess_blitz.best.game': 'blitz_best_game',
                                      'stats.chess_blitz.record.win': 'blitz_record_win',
                                      'stats.chess_blitz.record.loss': 'blitz_record_loss',
                                      'stats.chess_blitz.record.draw': 'blitz_record_draw',
                                      'stats.fide': 'rating_FIDE', 'stats.tactics.highest.rating': 'highest_rating',
                                      'stats.tactics.lowest.rating': 'lowest_rating',
                                      'stats.chess_daily.last.rating': 'daily_last_rating',
                                      'stats.chess_daily.best.rating': 'daily_best_rating',
                                      'stats.chess_daily.best.game': 'daily_best_game',
                                      'stats.chess_daily.record.win': 'daily_record_win',
                                      'stats.chess_daily.record.loss': 'daily_record_loss',
                                      'stats.chess_daily.record.draw': 'daily_record_draw',
                                      'stats.chess_daily.record.time_per_move': 'daily_record_time_move',
                                      'stats.chess_daily.record.timeout_percent': 'daily_record_timeout_percentage',
                                      'stats.puzzle_rush.best.total_attempts': 'puzzle_best_total_attempts',
                                      'stats.puzzle_rush.best.score': 'puzzle_score',
                                      'stats.chess_rapid.last.date': 'rapid_last_date',
                                      'stats.chess_rapid.best.date': 'rapid_best_date',
                                      'stats.chess_rapid.last.rd': 'rapid_last_rd',
                                      'stats.chess_bullet.last.date': 'bullet_last_date',
                                      'stats.chess_bullet.best.date': 'bullet_best_date',
                                      'stats.chess_bullet.last.rd': 'bullet_best_rd',
                                      'stats.chess_blitz.last.date': 'blitz_last_date',
                                      'stats.chess_blitz.best.date': 'blitz_best_date',
                                      'stats.chess_blitz.last.rd': 'blitz_last_rd',
                                      'stats.tactics.lowest.date': 'tactics_lowest_date',
                                      'stats.tactics.highest.date': 'tactics_highest_date',
                                        })

df_format = df_format.drop(columns=['stats.chess960_daily.last.rating', 'stats.chess960_daily.last.date',
                                    'stats.chess960_daily.last.rd', 'stats.chess960_daily.best.rating',
                                    'stats.chess960_daily.best.date', 'stats.chess960_daily.best.game',
                                    'stats.chess960_daily.record.win', 'stats.chess960_daily.record.loss',
                                    'stats.chess960_daily.record.draw', 'stats.chess960_daily.record.time_per_move',
                                    'stats.chess960_daily.record.timeout_percent', 'stats.chess_daily.last.date',
                                    'stats.chess_daily.best.date', 'stats.chess_daily.last.rd',
                                    'stats.puzzle_rush.daily.score', 'stats.puzzle_rush.daily.total_attempts'
                                    ])
print(df_format.columns)
#print(df_format)
#print(type(df_format))
df_format["rapid_last_date"] = df_format["rapid_last_date"].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d') if isinstance(x, int) else "No date")
df_format["bullet_last_date"] = df_format["bullet_last_date"].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d')  if isinstance(x, int) else "No date")
df_format["blitz_last_date"] = df_format["blitz_last_date"].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d')  if isinstance(x, int)  else "No date")
df_format["rapid_best_date"] = df_format["rapid_best_date"].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d')  if isinstance(x, int)  else "No date")
df_format["bullet_best_date"] = df_format["bullet_best_date"].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d')  if isinstance(x, int)  else "No date")
df_format["blitz_best_date"] = df_format["blitz_best_date"].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d')  if isinstance(x, int)  else "No date")
df_format["tactics_lowest_date"] = df_format["tactics_lowest_date"].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d') if  isinstance(x, int) else "No date")
df_format["tactics_highest_date"] = df_format["tactics_highest_date"].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d')  if isinstance(x, int) else "No date")
all_stats = df_format.to_dict('records')
printer.pprint(all_stats)
print(len(all_stats))

try:
   my_client["chess"]["stats"].insert_many(all_stats)
   print("success")
except Exception as e:
   print(e)
