# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 22:53:22 2023

這是一個電影投票bot。                                                                                            的雛型                                                                                            的部分完全體

"""

# 匯入所需的函式庫
import telebot
from CIP_module import scrape_movies_info
from os.path import exists
from time import time, sleep
from threading import Thread
# from datetime import date

# /start /help 歡迎訊息
welcome_msg = """👋 歡迎使用電影選片小幫手 Bot！
我是你的影院導賞員，專門為你提供最新的電影資訊和群組投票功能，讓你和你的群組朋友們輕鬆選擇今晚的觀影片！

🎥 電影資訊功能：
輸入 /movie (日期 yyyy-mm-dd):
    我將會爬取 Yahoo奇摩電影的最新資訊，包括評分、片長、導演、演員等，讓你快速掌握每部電影的相關情報。
輸入 /info [電影編號]:
    你可以瞭解指定電影的放映場次和時間。只要告訴我電影名稱，我將爬取最近的放映場次資訊，讓你不用再到不同網站查找，輕鬆掌握所有播放時刻！
* 輸入 /info all 可以一次查看所有電影的場次和時間

🗺️ 依地區篩選電影：
輸入 /area [地區名稱]:
    你可以查詢目前所有可搜尋的地區名稱。隨後，我會幫你搜尋符合該地區的電影場次，讓你更方便找到離你最近的放映場所。

🗳️ 群組投票功能：
輸入 /vote:
    你可以輕鬆在群組中發起投票，讓大家一起票選今晚要看的電影！只需幾個簡單指令，就能決定今晚的觀影片，讓群組氣氛更加熱鬧有趣。

📢 提醒功能：
別擔心錯過重要投票或電影新片上映時間！我會在適時提醒你關於投票結果和電影播放時刻，確保你不會錯過任何精彩電影資訊。

😊 使用方法很簡單，隨時輸入指令，我會幫你處理一切！
現在就讓我們一起開啟精彩的電影之旅吧！輸入 /start 或 /help 來存取此幫助訊息。

🎬 Enjoy the show! 🍿"""

# 電影資訊儲存檔案路徑, 通知時間表檔案路徑, 電影標題列表, 地區名稱列表 的初始化
path_mv = "movies_info.txt"
path_tm = "schedule_msg.txt"
titles = []
areas  = []

# 跑電影時間通知的主程式 (子執行緒)
def run_schedule_message():
    """
    林北懶得寫函式介紹啦吼~~
    """
    global schedule_time
    
    # 剛開始執行要先update_
    schedule_time = 0

    # 不存在，建檔
    if not exists(path_tm):
        write_schedule_message([])

    # 主迴圈
    while True:
        # 判斷要不要update
        if schedule_time == 0: update_schedule_message()
        
        # 現在 = 時間() (誤
        now = time()

        # 可能剛好有好幾個時間都到了(?
        while True:
            # 根本沒東西...騙我!
            if schedule_time == []: delay = 20 ; break

            # 存取第一個時間的資料
            next_time = schedule_time[0]["time"]

            # 時辰到啦~
            if now >= next_time:
                # 發訊息
                msg = "看電影囉~"
                bot.send_message(schedule_time[0]["chat"], msg)

                # 把第一項pop掉
                schedule_time.pop(0)
                # 寫檔 + 更新列表
                write_schedule_message(schedule_time)
                update_schedule_message()

            # 下個通知 <= 20秒，將重置速度加快
            elif next_time - now <= 10: delay = 1
            elif next_time - now <= 20: delay = 10

            # 下個通知還很久，不用猴急
            else: delay = 20 ; break

        # 我睡一下，不要吵我
        sleep(delay)

# 讀檔，更新schedule_time列表
def update_schedule_message():
    global schedule_time
    with open(path_tm, "r", encoding = "utf-8") as f:
        schedule_time = eval(f.readline()) # 用萬能eval變成json

# 寫檔，清空schedule_time列表
def write_schedule_message(schedule_list):
    global schedule_time
    with open(path_tm, "w", encoding = "utf-8") as f:
        f.write(str(schedule_list))
    schedule_time = 0 # 清空列表，這樣run_的迴圈就知道要呼叫update_

# 新增新時間{"chat": chat_id, "time": time}
def add_schedule_message(data):
    global schedule_time
    # 加進串列
    schedule_time.append(data)
    # 排序
    schedule_time.sort()
    # 寫檔 (並update列表)
    write_schedule_message(schedule_time)

# 取得電影資訊，並儲存在全域變數 movies_info 中
def get_movies_info(message):
    """
    獲取電影資訊，並儲存在全域變數 movies_info 中。

    Args:
        message: Telegram Bot 接收到的訊息

    Returns:
        None
    """
    global movies_info

    # 暴力多Thread爬蟲
    bot.reply_to(message, "爬取中...")
    if message.text.strip() == "/movie" or message.text.strip() == "/movie@CineInfoPollBot":
        movies_info = scrape_movies_info()
    elif message.text[6] == "@":
        movies_info = scrape_movies_info(request_date = message.text[22:].strip())
    else:
        try:
            movies_info = scrape_movies_info(request_date = message.text[6:].strip())
        except:
            movies_info = scrape_movies_info()



    # 因多Thread爬蟲效率太高而直接被遺棄的資料庫儲存code 永遠成為歷史......


    # # 現在 = 時間() (誤
    # now = time()
    # file_time = 0.0
    # j = 0

    # # 檢查是否已存在存儲電影資訊的檔案，若存在，則讀取時間和 JSON 內容
    # if exists(path_mv):
    #     with open(path_mv, "r", encoding = "utf-8") as f:
    #         try:
    #             file_time = float(f.readline().strip())
    #         except:
    #             pass
    #         s = f.readline()
    #         if s != "":
    #             j = eval(s)

    # # 若檔案內容時間與現在相差1hour以上，或者檔案內容是空的，則重新爬取電影資訊
    # if now - file_time >= 3600.0 or j == 0:
    #     bot.reply_to(message, "爬取中...")
    #     if message.text.strip() == "/movie" or message.text[6] == "@":
    #         movies_info = scrape_movies_info()
    #     else:
    #         try:
    #             movies_info = scrape_movies_info(request_date = message.text[6:].strip())
    #         except:
    #             movies_info = scrape_movies_info()
    #     with open(path_mv, "w", encoding = "utf-8") as f:
    #         f.write(str(now) + "\n" + str(movies_info))
    # else:
    #     movies_info = j


# 初始化 Telegram Bot
API_TOKEN = "5879372093:AAGsEa8zzzXu0tXo-kfwK1E2smo6XEs4zv8"
bot = telebot.TeleBot(API_TOKEN)

# 子執行緒 - Forever迴圈看通知時間到了沒
T = Thread(target = run_schedule_message)
T.start()

# 處理 '/start' 和 '/help' 指令
@bot.message_handler(commands=['help'])#, 'start'])
def send_welcome(message):
    """
    回應 /help 和 /start 指令，並發送歡迎訊息給使用者。

    Args:
        message: Telegram Bot 接收到的訊息

    Returns:
        None
    """
    bot.reply_to(message, welcome_msg)


# 取得電影資訊
@bot.message_handler(commands=["movie"])
def send_movies_info(message):
    """
    回應 /movie 指令，並將電影名稱列表發送給使用者。

    Args:
        message: Telegram Bot 接收到的訊息

    Returns:
        None
    """
    global movies_info, titles, areas

    # 獲取電影資訊
    get_movies_info(message)
    if movies_info == []:
        bot.reply_to(message, f"❌ {message.text[6:].strip()} 時間格式錯誤: 正確格式 yyyy-mm-dd")
        return

    # 初始化電影名稱列表
    titles = []
    areas  = []
    
    # 從json檔找電影標題和所有地點名稱
    for i in movies_info:
        titles.append(i["title"])
        for j in i["area"]:
            if j["city"] not in areas: areas.append(j["city"])

    # 組成回覆訊息並發送給使用者
    re_msg = ""
    for i, item in enumerate(titles):
        re_msg += str(i).ljust(2, "_") + "  " + item + "\n"
    bot.reply_to(message, re_msg)


# 取得指定電影的放映資訊
@bot.message_handler(commands=["info"])
def info(message):
    """
    回應 /info 指令，並發送指定電影的放映資訊給使用者。

    Args:
        message: Telegram Bot 接收到的訊息

    Returns:
        None
    """
    
    start_idx = 5
    if titles == []:
        bot.reply_to(message, "❌請先使用 /movie 指令查詢電影名稱")
        return
    if message.text.strip() == "/info" or message.text.strip() == "/info@CineInfoPollBot":
        bot.reply_to(message, "❌指令不完整: 請在 /info 後加上電影編號(以空格隔開)")
        return
    elif message.text[5] == "@":
        start_idx = 21

    try:
        # 獲取使用者指定的電影編號
        if message.text[start_idx:].strip().lower() == "all":
            idx = [i for i in range(len(titles))]
        else:
            idx = list(map(int, message.text[5:].strip().split()))
    except:
        # 處理使用者輸入錯誤的情況
        re_msg = "❌編號無法搜尋: 請輸出正確的電影編號\n"
        return

    # 組成指定電影的放映資訊訊息
    re_msg = info_msg(idx)

    # 避免訊息字數限制錯誤 (Telegram 限制bot的單則訊息最多512字)，拆分成多條訊息 (一次發送35行)
    c = 0
    temp = ""
    for msg in re_msg.split("\n"):
        if c == 35:
            # 傳送拆分後的訊息
            if temp[0] == " ": # 第一個字元是空白 的話會被吃掉 所以換成一點.
                temp = "." + temp[1:]
            bot.send_message(message.chat.id, temp)
            temp = ""
            c = 0
        temp += msg + "\n"
        c += 1
    # 別忘了最後一條訊息 :)
    if temp[0] == " ": # 第一個字元是空白 的話會被吃掉 所以換成一點.
        temp = "." + temp[1:]
    bot.send_message(message.chat.id, temp)

    # 超貼心的傳送門~<3
    bot.reply_to(message, "⬆️點擊訊息返回最上方")

# 根據指定的電影編號，組成顯示訊息
def info_msg(idx):
    """
    根據指定的電影編號，組成顯示訊息。

    Args:
        idx (list): 電影編號的列表

    Returns:
        re_msg (str): 包含指定電影放映資訊的訊息
    """
    re_msg = ""
    for i in idx:
        # 用迴圈包起來 195行就可以直接跳出
        for _ in range(1):
            try:
                temp = ""
                temp += titles[i] + "\n"

                # 尋找指定電影的放映資訊
                for j in movies_info:
                    if j["title"] == titles[i]:
                        break
                else: re_msg += f"❌編號 {i} 無法搜尋: 請輸出正確的電影編號\n" ; break # Index Out Of Range

                # 組成放映資訊的訊息 p用於縮排(4n個空白)
                for a in j["area"]:
                    p = " " * 4
                    temp += p + a["city"] + "\n"
                    for ts in a["theaters"]:
                        p = " " * 8
                        temp += p + ts["theater_name"] + "\n"
                        for item in ts["showing"].items():
                            p = " " * 12
                            temp += p + item[0] + "| " + " ".join(item[1]) + "\n"
                if i != idx[-1]:
                    temp += "\n"
                re_msg += temp
            except:
                re_msg += f"❌編號 {i} 無法搜尋: 請輸出正確的電影編號\n"
    return re_msg


# 依地區篩選電影
@bot.message_handler(commands=["area"])
def area(message):
    start_idx = 5
    # 如同字面上的意思
    if titles == []:
        bot.reply_to(message, "❌請先使用 /movie 指令查詢電影名稱")
        return
    if message.text.strip() == "/area" or message.text.strip() == "/area@CineInfoPollBot":
        re_msg = "❌指令不完整: 請在 /area 後加上地區名稱(一個)\n所有地區: " + ", ".join(areas)
        bot.reply_to(message, re_msg)
        return
    elif message.text[5] == "@":
        start_idx = 21


    a = message.text[start_idx:].strip()
    if a not in areas:
        re_msg = f"❌地區 {a} 無法搜尋: 請輸出正確的地區名稱\n所有地區: " + ", ".join(areas)
        bot.reply_to(message, re_msg)
        return

    # 跑到這裡代表使用者沒有故意耍笨輸入錯誤格式 great job!
    temp = []
    for i in movies_info:
        # 先一個一個比較電影播出的地區
        for j in i["area"]:
            # 符合要找的地區
            if j["city"] == a:
                temp.append(i["title"])

    # 組成回覆訊息並發送給使用者
    re_msg = a + "\n"
    for i in temp:
        re_msg += " " * 4 + str(titles.index(i)).ljust(2, "_") + "  " + i + "\n"
    bot.reply_to(message, re_msg)


# 林北還沒寫啦 猴急什麼 草!
@bot.message_handler(commands=["vote"])
def vote(message):
    bot.reply_to(message, "林北還沒寫啦 猴急什麼 草!\n看你這麼閒 幫你設定好電影定時通知了~<3")
    add_schedule_message({"chat": message.chat.id, 
                          "time": time()+30})

# 啟動bot
print("OnLine!")
bot.infinity_polling()