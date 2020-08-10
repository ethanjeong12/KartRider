#import sys
#import json
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from rank.models import *
from metadata.models import *

import requests
import json
import pandas as pd
import numpy as np
import math
import scipy.stats as stats
import datetime
from abc import *

## Variables
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
bf_yesterday = today - datetime.timedelta(days=2)
first_day_of_month = datetime.date.today().replace(day=1)

auth_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50X2lkIjoiOTczNjg0NTQ2IiwiYXV0aF9pZCI6IjIiLCJ0b2tlbl90eXBlIjoiQWNjZXNzVG9rZW4iLCJzZXJ2aWNlX2lkIjoiNDMwMDExMzkzIiwiWC1BcHAtUmF0ZS1MaW1pdCI6IjIwMDAwOjEwIiwibmJmIjoxNTk0MDAyMzYzLCJleHAiOjE2NTcwNzQzNjMsImlhdCI6MTU5NDAwMjM2M30.l7JhPS_pDBElPj0CRmwLMhcjK30AfTGIvQ74CB-pROE'
offset = 0
limit = 500 # max 500
indi_match_type = "7b9f0fd5377c38514dbb78ebe63ac6c3b81009d5a31dd569d1cff8f005aa881a"
team_match_type = "effd66758144a29868663aa50e85d3d95c5bc0147d7fdb9802691c2087f3416e"

## Helper Function
def record_histogram(histories):
    bin_edges = np.arange(histories.min(), histories.max(), 2000)
    x, y = np.histogram(histories, bins=bin_edges)
    hist_dict = {}
    for A, B in zip(x, y):
        if A != 0 and B != 0:
            hist_dict[B] = A
    return hist_dict

def recent_record(df, track_Id):
    return df.loc[df[df['trackId']==track_Id]['startTime'].idxmax()]['matchTime']

def milisec_converter(mili_sec):
    minute     = float(int(mili_sec)/60000)
    second     = str(round((float(format(minute, '.4f')) - (int(mili_sec)//60000)) * 60, 2)).replace('.','\'')
    lap_time   = str(int(mili_sec)//60000) + '\'' + second
    return lap_time

## Abstract Factory
class NXApiStat(metaclass = ABCMeta):
    def __init__(self, access_id, match_types, start_date, end_date):
        self.access_id = access_id
        self.match_types = match_types
        self.start_date = start_date
        self.end_date = end_date
        self.authorization_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50X2lkIjoiNDY5OTY0MzIyIiwiYXV0aF9pZCI6IjIiLCJ0b2tlbl90eXBlIjoiQWNjZXNzVG9rZW4iLCJzZXJ2aWNlX2lkIjoiNDMwMDExMzkzIiwiWC1BcHAtUmF0ZS1MaW1pdCI6IjIwMDAwOjEwIiwibmJmIjoxNTk0MTg4NjEwLCJleHAiOjE2NTcyNjA2MTAsImlhdCI6MTU5NDE4ODYxMH0.GOldD1jgUrjdExP4Snc59veMh9ilEhLVt0UXQFJKqy8'
        self.current_URL = f"https://api.nexon.co.kr/kart/v1.0/users/{self.access_id}/matches?start_date={self.start_date}&end_date={self.end_date}&offset={offset}&limit={limit}&match_types={self.match_types}"
        self.limit500_URL = f"https://api.nexon.co.kr/kart/v1.0/users/{self.access_id}/matches?start_date={self.start_date}&end_date={self.end_date}&offset={offset}&limit={limit}&match_types={self.match_types}"

    def _api_to_df(self, url):
        # API Call
        req_data = requests.get(url, headers={'authorization': self.authorization_key}).text
        data = json.loads(req_data)

        # Get dfs
        matches_df = pd.DataFrame(data['matches'][0]['matches'])
        player_df = pd.json_normalize(matches_df['player'])

        # preprocess 1) join, replace empty value, convert (numeric/date)type
        df = pd.merge(matches_df, player_df, how='left', left_index=True, right_index=True)
        df = df.replace('', np.nan, regex=True)
        df['startTime'] = pd.to_datetime(df['startTime']) # format='%Y-%m-%d'
        to_num_cols = ['matchTime', 'matchWin', 'matchRetired', 'matchRank']
        df[to_num_cols] = df[to_num_cols].apply(pd.to_numeric, errors='coerce', axis=1)

        # preprocess 2) convert retired log: if matchRank == 99 then matchTime set to 0
        mask = (df['matchRank'] == 99)
        df.loc[mask, 'matchTime'] = 0

        # preprocess 3) drop na columns
        df = df.dropna(subset=['kart', 'matchTime', 'matchWin', 'matchRetired', 'matchRank'])

        return df

    @abstractmethod
    def summary_stat(self):
        pass

## RankMain(first_day_of_month to limit 500)
class RankMainRecord_Cumul(NXApiStat):
    def __init__(self, access_id, match_types, start_date = first_day_of_month, end_date = today):
        super().__init__(access_id, match_types, start_date, end_date)
        print(self.access_id, self.limit500_URL)

    def summary_stat(self):
        df = self._api_to_df(url = self.limit500_URL) # Get Cumul Records

        # [메인순위] (승률 / 리타이어율)
        # [종합전적] (전 / 승 / 패 / 승률 / 완주율 / 리타이어율)
        play_cnt = df['matchRank'].count()

        rank_df = df['matchRank'].value_counts().reset_index()
        win_mask = (rank_df['index'] == 1)
        retire_mask = (rank_df['index'] == 99)

        win_cnt = rank_df[win_mask].matchRank.item()

        win_ratio = round(win_cnt/play_cnt, 4)

        if len(rank_df[retire_mask].matchRank) != 0:
            retire_cnt = rank_df[retire_mask].matchRank.item()
        else:
            retire_cnt = 0
        retire_ratio = round(retire_cnt/play_cnt, 4)


        # [종합전적] 캐릭터이름
        character = df['character_x'].head(1).item()

        # [메인순위] (누적포인트)
        score_df = pd.DataFrame(
            {
                'score' : [10,7,5,4,3,1,0,-1,-5]
            }, index = [1, 2, 3, 4, 5, 6, 7, 8, 99]
        )
        user_rankcount = df['matchRank'].value_counts()
        result = pd.merge(user_rankcount, score_df, how='inner', left_index=True, right_index=True)
        result['Rank_Mul_score'] = result['matchRank'] * result['score']
        point_cumul = result['Rank_Mul_score'].sum()

        return play_cnt, win_cnt, win_ratio, retire_ratio, point_cumul, character

## RankMain(yeseterday)
class RankMainRecord_Recent(NXApiStat):
    def __init__(self, access_id, match_types, start_date = bf_yesterday, end_date = today):
        super().__init__(access_id, match_types, start_date, end_date)
        print(self.access_id, self.limit500_URL)

    def summary_stat(self):
        df = self._api_to_df(url = self.current_URL) # Get Recent Records

        # [메인순위] (주행 횟수) / 승률 / 리타이어율 / 누적포인트 / 포인트 변화 / {랭크 변화 / 평균 순위}
        play_count_day1 = df['matchRank'].count()

        # [메인순위] 주행 횟수 / 승률 / 리타이어율 / 누적포인트 / (포인트변화) / {랭크 변화 / 평균 순위}
        score_df = pd.DataFrame(
            {
                'score' : [10,7,5,4,3,1,0,-1,-5]
            }, index = [1, 2, 3, 4, 5, 6, 7, 8, 99]
        )
        user_rankcount = df['matchRank'].value_counts()
        result = pd.merge(user_rankcount, score_df, how='inner', left_index=True, right_index=True)
        result['Rank_Mul_score'] = result['matchRank'] * result['score']
        point_new_day1 = result['Rank_Mul_score'].sum()

        return play_count_day1, point_new_day1

class UserDetailRecord_Cumul(NXApiStat):
    def __init__(self, access_id, match_types, start_date = first_day_of_month, end_date = today):
        super().__init__(access_id, match_types, start_date, end_date)
        print(self.access_id, self.limit500_URL)

    def summary_stat(self):
        df = self._api_to_df(url = self.limit500_URL)

        # [순위변동추이] - 500경기평균/50경기평균/50순위리스트 (avg_500rank, rank_50list, avg_50rank)
        avg_500rank = df['matchRank'].mean()
        rank_50list = list(df['matchRank'][:50])
        avg_50rank = np.mean(rank_50list)

        # [트랙전적] 기록분포 - 10개 데이터 포인트 이상만
        hist_result_list = []
        grouped_df = df.groupby(['accountNo_x','trackId'])['matchTime']
        for key, item in grouped_df:
                if sum(record_histogram(item).values()) > 10:
                    hist_result_list.append({
                        'track_key': key[1],
                        'recent_record': recent_record(df, key[1]),
                        'user_history': record_histogram(item)
                    })

        # [트랙전적] 주행횟수/승률/기록
        track_group_value = df.groupby(['trackId']).agg(
            {'matchWin':['count', 'sum'], 'matchTime':['min']}
        ).reset_index()
        track_group_value.columns = ['trackId', 'count', 'sum', 'min']
        track_group_value['winRatio'] = round(track_group_value['sum'] / track_group_value['count'], 4)
        track_result = track_group_value[['trackId', 'count', 'winRatio', 'min']]
        track_result['min'] = pd.to_timedelta(track_result['min'], unit='ms').astype(str).str.slice(start=10, stop=18)
        track_result['min'] = track_result['min'].str.replace(':','\'').str.replace('.','\'')

        # [카트전적] 카트별 트랙 4개기록
        kart_track_4history = df.groupby(['kart']).head(4)[['kart','trackId','matchTime']]

        # [카트전적] 주행횟수/승률/기록
        kart_group_value = df.groupby(['kart']).agg(
            {'matchWin':['count', 'sum']}).reset_index()
        kart_group_value.columns = ['kart', 'count', 'sum']

        retire_mask = (df['matchRank'] == 99)
        kart_group_retire = df[retire_mask].groupby(['kart']).agg(
            {'matchWin':['count']}).reset_index()
        kart_group_retire.columns = ['kart', 'retire']
        kart_meged = pd.merge(kart_group_value, kart_group_retire, how='left', on='kart')
        kart_meged['retire'] = kart_meged['retire'].replace(np.nan, 0)
        kart_meged['retireRatio'] = round(kart_meged['retire'] / kart_meged['count'], 4)
        kart_meged['winRatio'] = round(kart_meged['sum'] / kart_meged['count'], 4)
        kart_meged = kart_meged[['kart', 'count', 'winRatio', 'retireRatio']]
        kart_meged['history4'] = kart_meged['kart'].apply(
            lambda x: [
                {
                    'trackId':k['trackId'],
                    'matchTime':milisec_converter(k['matchTime'])
                    } for k in kart_track_4history.to_dict(orient='r') if k['kart'] == x
            ]
        )

        return avg_500rank, avg_50rank, rank_50list, hist_result_list,\
                track_result.to_dict(orient='r'), kart_meged.to_dict(orient='r')

if __name__ == '__main__':

    target_user = [i for i in GameUser.objects.filter(team_id=1).all()]
    team_type =  TeamType.objects.get(name='개인전')
    for i in target_user:

        play_cnt_global, win_cnt_global, win_ratio, retire_ratio_global, point_cumul, character = RankMainRecord_Cumul(
                i, indi_match_type
                ).summary_stat()
        play_count_day1, point_new_day1 = RankMainRecord_Recent(
                i.access_id, indi_match_type).summary_stat()
        avg_500rank, avg_50rank, rank_50list,\
                hist_result_list, track_result_list, kart_merged_list  = UserDetailRecord_Cumul(
                i.access_id, indi_match_type).summary_stat()

        for j in hist_result_list:
            track = Track.objects.get(key = j['track_key'])
            cumul_dist = [j['recent_record'], j['user_history']]
            UserTrackRecord(cumul_dist = cumul_dist, game_user=i, track=track, team_type=team_type).save()

        for j in track_result_list:
            track = Track.objects.get(key=j['trackId'])
            play_cnt = j['count']
            win_ratio = j['winRatio']
            best_lap = j['min']
            UserTrackInfo(play_cnt = play_cnt, win_ratio = win_ratio, best_lap = best_lap, game_user=i, track=track, team_type=team_type).save()

        for j in kart_merged_list:

            try:
                kart = Kart.objects.get(key=j['kart'])
                play_cnt = j['count']
                win_ratio = j['winRatio']
                retire_ratio = j['retireRatio']
                track_history = j['history4']
                UserKart(play_cnt = play_cnt, win_ratio = win_ratio, retire_ratio = retire_ratio, track_history = track_history, game_user=i, kart=kart, team_type=team_type).save()
            except:
                pass

        Detail(play_cnt = play_cnt_global, win_cnt = win_cnt_global, retire_pct = retire_ratio_global, rank_avg_50 = avg_50rank, rank_avg_500 = avg_500rank, rank_list_50 = rank_50list, game_user = i, character = Character.objects.get(key=character), team_type=team_type).save()

        Ranking(rank = i.rank, cumul_point = point_cumul, point_get = point_new_day1, win_pct = win_ratio, retire_pct = retire_ratio, play_cnt = play_count_day1, game_user=i, team_type=team_type).save()


    target_user = [i for i in GameUser.objects.filter(team_id=2).all()]
    team_type =  TeamType.objects.get(name='팀전')
    for i in target_user:

        play_cnt_global, win_cnt_global, win_ratio, retire_ratio_global, point_cumul, character = RankMainRecord_Cumul(
                i, team_match_type
                ).summary_stat()
        play_count_day1, point_new_day1 = RankMainRecord_Recent(
                i.access_id, team_match_type).summary_stat()
        avg_500rank, avg_50rank, rank_50list,\
                hist_result_list, track_result_list, kart_merged_list  = UserDetailRecord_Cumul(
                        i.access_id, team_match_type).summary_stat()

        for j in hist_result_list:
            track = Track.objects.get(key = j['track_key'])
            cumul_dist = [j['recent_record'], j['user_history']]
            UserTrackRecord(cumul_dist = cumul_dist, game_user=i, track=track, team_type=team_type).save()

        for j in track_result_list:
            track = Track.objects.get(key=j['trackId'])
            play_cnt = j['count']
            win_ratio = j['winRatio']
            best_lap = j['min']
            UserTrackInfo(play_cnt = play_cnt, win_ratio = win_ratio, best_lap = best_lap, game_user=i, track=track, team_type=team_type).save()

        for j in kart_merged_list:

            try:
                kart = Kart.objects.get(key=j['kart'])
                play_cnt = j['count']
                win_ratio = j['winRatio']
                retire_ratio = j['retireRatio']
                track_history = j['history4']
                UserKart(play_cnt = play_cnt, win_ratio = win_ratio, retire_ratio = retire_ratio, track_history = track_history, game_user=i, kart=kart, team_type=team_type).save()
            except:
                pass

        Detail(play_cnt = play_cnt_global, win_cnt = win_cnt_global, retire_pct = retire_ratio_global, rank_avg_50 = avg_50rank, rank_avg_500 = avg_500rank, rank_list_50 = rank_50list, game_user = i, character = Character.objects.get(key=character), team_type=team_type).save()

        Ranking(rank = i.rank, cumul_point = point_cumul, point_get = point_new_day1, win_pct = win_ratio, retire_pct = retire_ratio, play_cnt = play_count_day1, game_user=i, team_type=team_type).save()


