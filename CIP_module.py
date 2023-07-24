# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 22:53:22 2023

這是一個爬取 Yahoo 電影網站上指定地區影城的電影放映資訊的程式模組。

"""

# 匯入所需的函式庫
import requests
from bs4 import BeautifulSoup
from json import loads
from datetime import date
from threading import Thread

def get_movie_data():
    """
    取得 Yahoo 電影網站上的電影資料，包含電影 ID 和電影名稱。

    Returns:
        ids (list): 電影 ID 列表
        names (list): 電影名稱列表
    """
    # Yahoo電影的API網址
    url = "https://movies.yahoo.com.tw/ajax/in_theater_movies"

    # 使用 requests 套件向網址發送GET請求，獲取HTML響應
    html = requests.get(url)
    html.encoding = "utf-8"

    # 將HTML響應解析為JSON格式
    j = loads(html.text)

    # 從JSON中提取電影ID和電影名稱並分別放入列表中
    ids = list(j.keys())
    names = list(j.values())
    return ids, names

def get_movie_schedule(movie_id, request_date):
    """
    取得指定電影的放映資訊 HTML。

    Args:
        movie_id (str): 電影 ID

    Returns:
        str: 放映資訊的 HTML 內容
    """
    # Yahoo電影放映資訊的API網址
    url = "https://movies.yahoo.com.tw/ajax/pc/get_schedule_by_movie"
    
    # 設定要傳遞給API的參數，包括電影ID、日期（當天日期）和地區ID（未指定）
    payload = {
        "movie_id": movie_id,
        "date": request_date,
        "area_id": ""
    }
    
    # 使用 requests 套件向API網址發送GET請求，傳遞參數，獲取HTML響應
    html = requests.get(url, params=payload)

    # 將HTML響應解析為JSON格式
    j = loads(html.text)
    
    # 從JSON中提取並返回放映資訊的HTML內容
    return j["view"]

def parse_schedule_html(schedule_html):
    """
    解析放映資訊的 HTML 內容，提取電影名稱、地區和影城資訊。

    Args:
        schedule_html (str): 放映資訊的 HTML 內容

    Returns:
        dict: 包含電影名稱、地區和影城資訊的字典
    """
    # 使用 BeautifulSoup 套件解析放映資訊的HTML內容
    soup = BeautifulSoup(schedule_html, features="html.parser")

    # 從HTML中提取電影名稱
    movie_info = soup.find_all("input", attrs={"type": "radio", "name": "schedule_list"})
    tt = movie_info[0]["data-movie_title"]

    # 初始化包含電影名稱、地區和影城資訊的字典
    movie_data = {"title": tt, "area": []}
    c = 0
    
    # 提取地區和影城資訊
    cities = soup.find_all("div", attrs={"class": "area_title"})
    theater = soup.find_all("ul", attrs={"class": "area_time _c jq_area_time"})
    last = 0

    # 以下是神奇的資料處理 不要叫我解釋 我也不想再寫一次
    for t in theater:
        if t.parent != last:
            city = cities[c].text
            movie_data["area"].append({"city" : city, "theaters" : []})
            c += 1

        tn = t["data-theater_name"]
        movie_data["area"][-1]["theaters"].append({"theater_name": tn, "showing": {}})

        for mvif in movie_info:
            tp, dt, tm = mvif["data-movie_type"], mvif["data-movie_date"], mvif["data-movie_time"]
            if tp not in movie_data["area"][-1]["theaters"][-1]:
                movie_data["area"][-1]["theaters"][-1]["showing"] = {}
            if dt not in movie_data["area"][-1]["theaters"][-1]["showing"]:
                movie_data["area"][-1]["theaters"][-1]["showing"][dt] = []
            movie_data["area"][-1]["theaters"][-1]["showing"][dt].append(tm)
        last = t.parent

    return movie_data

def scrape_movie_info(idx, i, request_date):
    try:
        # 獲取指定電影的放映資訊HTML
        schedule_html = get_movie_schedule(i, request_date)
        
        # 解析放映資訊的HTML內容，提取電影名稱、地區和影城資訊
        movie_data = parse_schedule_html(schedule_html)
        
        # 將處理後的電影資訊添加到列表中
        movies_info.append(movie_data)
    except:
        # 若處理過程中出現錯誤，則跳過該電影的處理，繼續處理下一部電影
        pass

def scrape_movies_info(n = -1, request_date = str(date.today())):
    """
    爬取 Yahoo 電影網站的電影資訊，包含放映資訊。

    Returns:
        list: 包含各部電影資訊的列表
    """
    global movies_info

    # 獲取 Yahoo 電影網站上的電影資料，包含電影 ID 和電影名稱
    ids, names = get_movie_data()
    
    # 初始化存儲各部電影資訊的列表
    movies_info = []
    
    # 逐個電影進行處理 使用threading
    threads = []
    for idx, i in enumerate(ids):
        if idx == n: break
        threads.append(Thread(target = scrape_movie_info, args = (idx, i, request_date)))
        threads[-1].start()
    # 等全都爬完
    for i in threads:
        i.join()

    # 返回包含各部電影資訊的列表
    return movies_info
