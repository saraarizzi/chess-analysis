
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import  By
from time import sleep
import pandas as pd
import pymongo
from pymongo import MongoClient
#from findNameInRatings import find_name_in_ratings

host = "cluster0.kah64fo.mongodb.net/?retryWrites=true&w=majority"
username = "mik_dm_project"
password = "Spindox!99"

my_client = MongoClient(f"mongodb+srv://{username}:{password}@{host}")


db = my_client.chess
collection = db.players
cursor = collection.find({})



fide_id_list = []

for document in cursor:
    document_id = document["fide_id"]
    fide_id_list.append(document_id)


'''
rev_players_list = []
for name in players_list:
    if str(name) is not None:
        rev_players_list.append(', '.join(reversed(str(name).split(' '))))
'''
# print(rev_players_list)



# print(players_list)
# options = webdriver.ChromeOptions()
#options.add_experimental_option("detach", True)
#PATH = "C:/Users/mirko.dibiase/chess-analysis/driver/chromedriver.exe"
FIDE_LINK = 'https://www.fide.com/'
chrome_driver = ChromeDriverManager().install()
driver=Chrome(service=Service(chrome_driver))
driver.maximize_window()
driver.get(FIDE_LINK) # access to webpage


# clicking on RATINGS button
ratings_button = driver.find_element(By.XPATH,'//*[@id="navbarSupportedContent"]/app-shared-client-menu-header/ul/li[2]/a')

# access to button through XPATH and click()
ratings_button.click()
#sleep(10)

list_final = []
# Defining a function to search & scrape name
for id in fide_id_list:
# def find_name_in_ratings(name):
    driver.find_element(By.XPATH,'//*[@id="dyn1"]').send_keys(id)
    sleep(1)
# Set search_button for entering the name we are looking for
    search_button = driver.find_element(By.XPATH,'//*[@id="search_form_buton"]/i')
# Click on it
    search_button.click()
    sleep(2)
    table = driver.find_element(By.XPATH, '//*[@id="table_results"]/tbody')
    for tr in table.find_elements(By.XPATH,'//*[@id="table_results"]/tbody/tr'):
        dict_tmp = {}
        lista_tmp = []
        for td in tr.find_elements(By.XPATH, ".//td"):
            lista_tmp.append(td.text)
        #if lista_tmp[1] == "GM":
            lista_tmp.pop(2)
            #print(lista_tmp)
        dict_tmp['standard_rating'] = lista_tmp[3]
        dict_tmp['rapid_rating'] = lista_tmp[4]
        dict_tmp['blitz_rating'] = lista_tmp[5]
        dict_tmp['birth_year'] = lista_tmp[6]
        dict_tmp['player_id'] = id
        list_final.append(dict_tmp)
        lista_tmp.clear()
    sleep(2)
    driver.find_element(By.XPATH, '//*[@id="dyn1"]').clear()
    sleep(2)

print(list_final)

#for nome in players_list:
# find_name_in_ratings("Carlsen Magnus")






# print(len(players_list))



'''

sleep(1)

# detecting and saving the table
ratings = driver.find_elements(By.TAG_NAME,'tr')
# print(ratings)


# setting the list of interest in order to getting a dataframe
classifica = []
name = []
federation = []
rating = []
b_year = []

# for rating in ratings:
 #  position = rating.find_element(By.XPATH, '//*[@id="top_rating_div"]/table/tbody/tr/td[2]').text
 #  classifica.append(position)

#for row in ratings:
#   print([td.text for td in row.find_elements(By.XPATH, '//*[@id="top_rating_div"]/table/tbody/tr/td[2]')])


# setting the TABLE with tag name
table =  driver.find_element(By.TAG_NAME, 'table')

# populating classifica[]
for row in table.find_elements(By.XPATH,".//tr"):
    for td in row.find_elements(By.XPATH,".//td[1]"):
        classifica.append(td.text)

# populating name[]
for row in table.find_elements(By.XPATH,".//tr"):
    for td in row.find_elements(By.XPATH,".//td[2]"):
        name.append(td.text)

# populating federation[]
for row in table.find_elements(By.XPATH,".//tr"):
    for td in row.find_elements(By.XPATH,".//td[3]"):
        federation.append(td.text)

# populating rating[]
for row in table.find_elements(By.XPATH,".//tr"):
    for td in row.find_elements(By.XPATH,".//td[4]"):
        rating.append(td.text)

# populating b_year[]
for row in table.find_elements(By.XPATH,".//tr"):
    for td in row.find_elements(By.XPATH,".//td[6]"):
        b_year.append(td.text)

print(classifica)
print(name)
print(federation)
print(rating)
print(b_year)

# saving lists into df
fide_df = pd.DataFrame({'classifica': classifica,
                        'name': name,
                        'federation': federation,
                        'rating': rating,
                        'b_year': b_year})

# converting df into json
fide_df = fide_df.to_json(orient='index')
print(fide_df)


for row in table.find_elements(By.XPATH,".//tr"):
    print([td.text for td in row.find_elements(By.XPATH,".//td[2]")])

for row in table.find_elements(By.XPATH,".//tr"):
    print([td.text for td in row.find_elements(By.XPATH,".//td[3]")])

for row in table.find_elements(By.XPATH,".//tr"):
    print([td.text for td in row.find_elements(By.XPATH,".//td[4]")])

for row in table.find_elements(By.XPATH,".//tr"):
    print([td.text for td in row.find_elements(By.XPATH,".//td[6]")])
'''










