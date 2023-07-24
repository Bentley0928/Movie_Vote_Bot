from os.path import exists
from time import time,sleep
from threading import Thread
path_tm = "schedule_msg.txt"
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
            elif next_time - now <= 10: delay = 1  ; break
            elif next_time - now <= 20: delay = 10 ; break

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
    update_schedule_message()

# 新增新時間{"chat": chat_id, "time": time}
def add_schedule_message(data):
    global schedule_time
    # 加進串列
    schedule_time.append(data)
    # 排序
    schedule_time.sort(key = lambda x: x["time"])
    # 寫檔 (並update列表)
    write_schedule_message(schedule_time)