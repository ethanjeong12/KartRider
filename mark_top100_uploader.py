import sys
import os 
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from rank.models import *

from selenium import webdriver
import datetime
import pymysql
import requests

# Set Variables
crawling_url_indi = 'https://tmi.nexon.com/kart/rank'
crawling_url_team =  'https://tmi.nexon.com/kart/rank?mode=team&speed=speedTeamFastest'
auth_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50X2lkIjoiOTczNjg0NTQ2IiwiYXV0aF9pZCI6IjIiLCJ0b2tlbl90eXBlIjoiQWNjZXNzVG9rZW4iLCJzZXJ2aWNlX2lkIjoiNDMwMDExMzkzIiwiWC1BcHAtUmF0ZS1MaW1pdCI6IjIwMDAwOjEwIiwibmJmIjoxNTk0MDAyMzYzLCJleHAiOjE2NTcwNzQzNjMsImlhdCI6MTU5NDAwMjM2M30.l7JhPS_pDBElPj0CRmwLMhcjK30AfTGIvQ74CB-pROE'
delay = 3
t=datetime.datetime.today()

# Brwosing and Crawling
def browse_n_crawl(crawling_url, delay):
    print("start crwaling...")
    browser = webdriver.Firefox()
    browser.implicitly_wait(delay)
    browser.get(crawling_url)
    print("browser opening...")
    top3 = browser.find_element_by_css_selector('#base > div.toprank')
    top100 = browser.find_element_by_css_selector('#rank > div > ul')
    user_list = [i.split(' ')[0] for i in top3.text.split('\n')[0::7]]
    user_list.extend([i.split(' ')[0] for i in top100.text.split('\n')[6::5]])
    print("succeed to get element...")
    browser.quit()
    print("browser closed...")
    print(str(t) + " TOP " + str(len(user_list)) + " Users are ...")
    print('sample user_list ' + str(user_list[:5]) + '...')
    return user_list


# Get Rider Api
def user_pairid_creator(nickname):
    try:
        rider_URL = f'https://api.nexon.co.kr/kart/v1.0/users/nickname/{nickname}'
        r = requests.get(rider_URL , headers={'authorization': auth_key})
        rider_dict = r.json()
        datum = {
               'access_id' : rider_dict['accessId'],
                'nickname' : rider_dict['name']
                }
        return datum
    except:
        pass


# Execute Crawling and Call Rider Api
while True:
    user_list = browse_n_crawl(crawling_url_indi, delay)
    delay += 1
    print("user delay time is " + str(delay) + " ...")
    if len(user_list) >= 10:
        while True:
            team_list = browse_n_crawl(crawling_url_team, delay)
            delay += 1
            print("team delay time is " + str(delay) + " ...")
            if len(team_list) >= 10:
                break
        break


user_dict_pre = [user_pairid_creator(user) for user in user_list]
user_dict = list(filter(None, user_dict_pre))
team_dict_pre = [user_pairid_creator(user) for user in team_list]
team_dict = list(filter(None, team_dict_pre))

# Excpetion
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
bf_yesterday = today - datetime.timedelta(days=2)
indi_match_type = "7b9f0fd5377c38514dbb78ebe63ac6c3b81009d5a31dd569d1cff8f005aa881a"
team_match_type =  "effd66758144a29868663aa50e85d3d95c5bc0147d7fdb9802691c2087f3416e"
offset = 0
limit = 500

start_date = bf_yesterday
end_date = today
match_types = indi_match_type

not_played_d1 = []
for i in user_dict:
    access_id = i['access_id']
    url = f"https://api.nexon.co.kr/kart/v1.0/users/{access_id}/matches?start_date={start_date}&end_date={ end_date}&offset={offset}&limit={limit}&match_types={match_types}"
    req_data = requests.get(url, headers={'authorization': auth_key}).text
    data = json.loads(req_data)
    if data['matches'] == []:
        not_played_d1.append(access_id)

user_dict = [i for i in user_dict if i['access_id'] not in not_played_d1]

match_types = team_match_type

not_played_d1 = []
for i in team_dict:
    access_id = i['access_id']
    url = f"https://api.nexon.co.kr/kart/v1.0/users/{access_id}/matches?start_date={start_date}&end_date={ end_date}&offset={offset}&limit={limit}&match_types={match_types}"
    req_data = requests.get(url, headers={'authorization': auth_key}).text
    data = json.loads(req_data)
    if data['matches'] == []:
        not_played_d1.append(access_id)

team_dict = [i for i in team_dict if i['access_id'] not in not_played_d1]


[user_dict[k].__setitem__('rank', k+1)  for k, _ in enumerate(user_dict)]
[team_dict[k].__setitem__('rank', k+1) for k, _ in enumerate(team_dict)]

print('Nick and Access_id paired users are ' + str(len(user_dict)))
print('Nick and Access_id paired team_users are ' + str(len(team_dict)))
print('sample user_dict ' + str(user_dict[:5]) + '...' + str(team_dict[:5]) + '...')

#[{'access_id': '1593946477', 'nickname': 'STELLA동댜', 'rank': 1, 'team_id': 1}, ...]

TeamType.objects.create(name='개인전')
TeamType.objects.create(name='팀전')

user_obj = [GameUser(team_id = TeamType.objects.get(name='개인전').id, **vals) for vals in user_dict]
GameUser.objects.bulk_create(user_obj)
team_obj = [GameUser(team_id = TeamType.objects.get(name='팀전').id, **vals) for vals in team_dict]
GameUser.objects.bulk_create(team_obj)

