
import math
import requests
from bs4 import BeautifulSoup
from json import loads
import json
from datetime import date
from threading import Thread

import CIP_module
def get_movie():
    """輸出格式:

    (
     [
        [A類電影],
        [B類電影],
        [C類電影]......
     ],
     [
        電影分類標籤
     ]
    
    )

    
    """
    all_movies = CIP_module.get_movie_data()[1]
    movies = [all_movies]
    movies_page = ["page" + str(1)]
    
    
    

    


    return (movies , movies_page)

theater_movie_time = {}
def get_theater(movie : str):
    """輸出格式:

    (
     [
        [A縣電影院],
        [B市電影院],
        [C縣電影院]......
     ],
     [
        縣市
     ]
    
    )

    依據輸入的movie
    得出會上映這部電影的電影院

    """
    cities = []
    theaters = []
    data = CIP_module.scrape_movies_info(n = -1, request_date = str(date.today()),movie = movie)
    for area in data[0]["area"]:
        cities.append(area["city"])
        theaters.append([])
        theaters_data = area["theaters"]
        for t in theaters_data:
            theaters[len(theaters) - 1].append(t['theater_name'])
            print(t['theater_name'])
            theater_movie_time[t['theater_name']] = t["showing"]
        # print(cities[len(cities) - 1])
        # print(theaters[len(theaters) - 1])
    
    return (theaters, cities)
def get_time(movie : str,theater : str):
    """輸出格式:

    (
     [
        [第一天時間列表],
        [第二天時間列表],
        [第三天時間列表]
     ],
     [
        
     ]
    
    )
    
    依據輸入的theater和movie
    這部電影在這個電影院三天的時間表

    時間我希望日期加上時間，如:
    "7/25 19:00 - 21:00"
    
    """
    showing_time = theater_movie_time[theater]

    day = []
    for d in showing_time.keys():
        day.append(str(d))
    time = []
    for d in day:
        
        time.append([])
        for t in showing_time[d]:
            time[len(time) - 1].append(str(d) + " " + str(t))
    print(day)
    print(time)
    return ([time,list(day)])


#print(CIP_module.scrape_movies_info(n = -1, request_date = str(date.today()),movie = "鬼郵輪：瑪麗皇后號"))

get_theater("鬼郵輪：瑪麗皇后號")
get_time("鬼郵輪：瑪麗皇后號","台北樂聲影城")