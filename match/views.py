import requests
import json
import math
import pandas as pd

from django.shortcuts import render
from django.views     import View
from django.http      import JsonResponse

from .track           import track_dict
from .kart            import kart_dict

def make_match_id_list(access_id, match_type):

    authorization_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50X2lkIjoiNDY5OTY0MzIyIiwiYXV0aF9pZCI6IjIiLCJ0b2tlbl90eXBlIjoiQWNjZXNzVG9rZW4iLCJzZXJ2aWNlX2lkIjoiNDMwMDExMzkzIiwiWC1BcHAtUmF0ZS1MaW1pdCI6IjIwMDAwOjEwIiwibmJmIjoxNTk0MTg4NjEwLCJleHAiOjE2NTcyNjA2MTAsImlhdCI6MTU5NDE4ODYxMH0.GOldD1jgUrjdExP4Snc59veMh9ilEhLVt0UXQFJKqy8'

    URL = f'https://api.nexon.co.kr/kart/v1.0/users/{access_id}/matches?start_date=&end_date= &offset=0&limit=10&match_types={match_type}'
    r = requests.get(URL , headers={'authorization': authorization_key})

    user_dict  = r.json()

    if not user_dict['matches']:
        return []

    match_list = user_dict['matches'][0]['matches']

    match_id_list   = []

    for i in range(len(match_list)):
        match_id_list.append(match_list[i]['matchId'])

    return match_id_list

def make_detail_list(access_id, match_type):

    offset            = 0
    limit             = 10
    authorization_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50X2lkIjoiNDY5OTY0MzIyIiwiYXV0aF9pZCI6IjIiLCJ0b2tlbl90eXBlIjoiQWNjZXNzVG9rZW4iLCJzZXJ2aWNlX2lkIjoiNDMwMDExMzkzIiwiWC1BcHAtUmF0ZS1MaW1pdCI6IjIwMDAwOjEwIiwibmJmIjoxNTk0MTg4NjEwLCJleHAiOjE2NTcyNjA2MTAsImlhdCI6MTU5NDE4ODYxMH0.GOldD1jgUrjdExP4Snc59veMh9ilEhLVt0UXQFJKqy8'

    URL = f'https://api.nexon.co.kr/kart/v1.0/users/{access_id}/matches?start_date=&end_date= &offset={offset}&limit={limit}&match_types={match_type}'

    r = requests.get(URL , headers={'authorization': authorization_key})

    user_dict  = r.json()

    if not user_dict['matches']:
        return []

    # creating a dataframe
    match_list_1 = pd.DataFrame(user_dict['matches'][0]['matches'])[['playerCount', 'trackId', 'startTime']]
    match_list_1['startTime'] = match_list_1['startTime'].astype(str).str.slice(start=11, stop=13)
    match_list_1['trackId'] = track_dict(match_list_1['trackId'])
    match_list_1.rename(columns={'startTime':'timeDifference'}, inplace=True)

    match_list_2 = pd.DataFrame(user_dict['matches'][0]['matches'])
    player_df = pd.json_normalize(match_list_2['player'])[['kart', 'matchRank', 'matchTime']]

    to_num_cols = ['matchTime', 'matchRank']
    player_df[to_num_cols] = player_df[to_num_cols].apply(pd.to_numeric, errors='coerce', axis=1)

    mask = (player_df['matchRank'] == 99)
    player_df.loc[mask, 'matchTime'] = 0

    player_df['matchTime'] = pd.to_timedelta(player_df['matchTime'], unit='ms').astype(str).str.slice(start=10, stop=18)
    player_df['matchTime'] = player_df['matchTime'].str.replace(':','\'').str.replace('.','\'')

    player_df['kart'] = kart_dict(player_df['kart'])
    test = pd.merge(player_df, match_list_1, how='left',left_index=True, right_index=True)

    return test.to_dict(orient='records')

class IndiMatchView(View):

    def get(self, request, access_id, match_type):

        access_id     = str(access_id)
        match_id_list = make_match_id_list(access_id, match_type)
        detail_list   = make_detail_list(access_id, match_type)
        match_list    = []
#        indi_list     = []
#        indi_final    = []

        # when access_id doesn't exist
        if not match_id_list:
            combined_list = pd.DataFrame()

            return JsonResponse( {'message': 'INVALID_ACCESS_ID'}, status = 400)

        else:
            for match_id in match_id_list:

                #API call
                authorization_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50X2lkIjoiNDY5OTY0MzIyIiwiYXV0aF9pZCI6IjIiLCJ0b2tlbl90eXBlIjoiQWNjZXNzVG9rZW4iLCJzZXJ2aWNlX2lkIjoiNDMwMDExMzkzIiwiWC1BcHAtUmF0ZS1MaW1pdCI6IjIwMDAwOjEwIiwibmJmIjoxNTk0MTg4NjEwLCJleHAiOjE2NTcyNjA2MTAsImlhdCI6MTU5NDE4ODYxMH0.GOldD1jgUrjdExP4Snc59veMh9ilEhLVt0UXQFJKqy8'

                re = requests.get(f'https://api.nexon.co.kr/kart/v1.0/matches/{match_id}', headers={'authorization': authorization_key})

                match_info = re.json()

                # players df
                players = pd.DataFrame(match_info['players'])[['characterName', 'kart', 'matchRank', 'matchTime']]

                to_num_cols = ['matchTime', 'matchRank']
                players[to_num_cols] = players[to_num_cols].apply(pd.to_numeric, errors='coerce', axis=1)

                mask = (players['matchRank'] == 99)
                players.loc[mask, 'matchTime'] = 0

                players['kart'] = 'https://wekart.s3.ap-northeast-2.amazonaws.com/kart/' + players['kart'] + '.png'
                players['matchTime'] = pd.to_timedelta(players['matchTime'], unit='ms').astype(str).str.slice(start=10, stop=18)
                players['matchTime'] = players['matchTime'].str.replace(':','\'').str.replace('.','\'')

                match_list.append(players.to_dict(orient='records'))

            match_df = pd.DataFrame(match_list)
            detail_df = pd.DataFrame(detail_list)

            combined = pd.concat([detail_df, match_df], axis = 1)
            combined = combined.dropna(subset=['matchRank'])

        return JsonResponse( {'indi_match_detail':combined.to_dict(orient='records')}, status = 200)

class TeamMatchView(View):

    def get(self, request, access_id, match_type):

        detail_list = make_detail_list(access_id, match_type)
        match_id_list = make_match_id_list(access_id, match_type)
        team_list = []

        if not match_id_list:
            combined_list = pd.DataFrame()

            return JsonResponse( {'message': 'INVALID_ACCESS_ID'}, status = 400)

        else:
            for match_id in match_id_list:

                # API call
                authorization_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50X2lkIjoiNDY5OTY0MzIyIiwiYXV0aF9pZCI6IjIiLCJ0b2tlbl90eXBlIjoiQWNjZXNzVG9rZW4iLCJzZXJ2aWNlX2lkIjoiNDMwMDExMzkzIiwiWC1BcHAtUmF0ZS1MaW1pdCI6IjIwMDAwOjEwIiwibmJmIjoxNTk0MTg4NjEwLCJleHAiOjE2NTcyNjA2MTAsImlhdCI6MTU5NDE4ODYxMH0.GOldD1jgUrjdExP4Snc59veMh9ilEhLVt0UXQFJKqy8'

                re = requests.get(f'https://api.nexon.co.kr/kart/v1.0/matches/{match_id}', headers={'authorization': authorization_key})
                match_info = re.json()

                # first team
                first_team = pd.DataFrame(match_info['teams'][0]['players'])[['characterName', 'kart', 'matchRank', 'matchTime']]
                to_num_cols = ['matchTime', 'matchRank']
                first_team[to_num_cols] = first_team[to_num_cols].apply(pd.to_numeric, errors='coerce', axis=1)

                mask = (first_team['matchRank'] == 99)
                first_team.loc[mask, 'matchTime'] = 0

                # second team
                second_team = pd.DataFrame(match_info['teams'][1]['players'])[['characterName', 'kart', 'matchRank', 'matchTime']]
                to_num_cols = ['matchTime', 'matchRank']
                second_team[to_num_cols] = second_team[to_num_cols].apply(pd.to_numeric, errors='coerce', axis=1)

                mask = (second_team['matchRank']) == 99
                second_team.loc[mask, 'matchTime'] = 0

                # combining 2 teams into one
                teams = [first_team, second_team]
                teams_key = pd.concat(teams, keys=['team 1', 'team 2']).reset_index().drop(
                    columns='level_1').rename(
                    columns={'level_0':'teamId'}
                )
                teams_key['kart'] = 'https://wekart.s3.ap-northeast-2.amazonaws.com/kart/' + teams_key['kart'] + '.png'

                team_list.append(teams_key.to_dict(orient='records'))

            team_df = pd.DataFrame(team_list)

            detail_df = pd.DataFrame(detail_list)
            combined = pd.concat([detail_df, team_df], axis=1)

            combined = combined.dropna(subset=['matchRank'])

            return JsonResponse( {'team_match_detail':combined.to_dict(orient='records')}, status = 200)
