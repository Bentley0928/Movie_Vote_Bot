import typing 
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultPhoto

import bridge

token = "6618282878:AAHxSA6x_syoEijH83R80f4M-uBlqKN0l4E"

bot = telebot.TeleBot(token)

movie = None   #決定要看的電影
theater = None #決定要去的電影院
day_time = None#決定要去看電影的時間


person_vote_num = 0     #一個人幾票
add_string = ""         #show all
show_all_bool = False   #是否開啟show all
chat_id = -1001984208872

#電影
movie_choice,movie_kind = bridge.get_movie()
#電影院
theater_choice = []
cities = []

#時間
time_choice = []
day = []

y_index = 0 
x_index = 0
get_vote = {} #有被投到票的選項與他們的得票數{選項 : 票數}
user_vote = {}#各個使用者所選擇的選項{id:[選項,]}

#儲存上下左右
turn_page_button = [InlineKeyboardButton("left", callback_data="button_left"),
                    InlineKeyboardButton("up", callback_data="button_up"),
                    InlineKeyboardButton("right", callback_data="button_right"),
                InlineKeyboardButton("down", callback_data="button_down"),
            ]

def vote_appear(options : typing.List) -> typing.List:#選項排版

    global y_index
    choice_appear = []
    this_page = options[x_index]
    for i in range(y_index , y_index + 7):#一次顯示7個選項
        if (i < len(this_page)):
            votes = 0
            if (this_page[i] in get_vote):#判斷是否有被投票(防止RE)
                votes = get_vote[this_page[i]]
            choice_appear.append(InlineKeyboardButton(this_page[i] + " " + str(votes) + "票",
                                     callback_data="vote_"+this_page[i]))
        else:
            choice_appear.append(InlineKeyboardButton(" ",
                                     callback_data="vote_"+"empty"))#如果index超出選項範圍，顯示空白
    return choice_appear


def button_array(t_appear : typing.List):#將按鈕儲存成可以輸出的格式
    """
    t_appear = vote_appear()
    """
    show_theater_reply_markup = InlineKeyboardMarkup()#儲存按鈕的容器
    for t in t_appear:
        show_theater_reply_markup.add(t)#加入選項按鈕
    show_theater_reply_markup.add(*turn_page_button)#加入方向按鈕
    show_theater_reply_markup.add(InlineKeyboardButton("show all",callback_data="show_all"))#加入show all
    return show_theater_reply_markup
def show_vote(message,options : typing.List,title : str,kind = typing.List):
    """
    呼叫投票
    """
    global y_index
    global x_index
    global get_vote
    global user_vote
    global person_vote_num

    y_index = 0
    x_index = 0
    get_vote = {}
    user_vote = {}#初始化

    text_len = len(message.text)

    if(title == "日期:"):
        person_vote_num = 10000
    elif (text_len == 3 or str(message.text).find("@") == 3):#如果沒有額外輸入一人票數上限，就設為1
        person_vote_num = 1
    else:
        if (str(message.text).find("@") != -1):#把@的訊息擋掉
            person_vote_num = int(message.text[4:str(message.text).find("@")])
        else:
            person_vote_num = int(message.text[4:len(message.text)])#一人票數上限設定為輸入參數
    
    #產生投票表單
    appear = vote_appear(options)
    show_reply_markup = button_array(appear)
    bot.send_message(message.chat.id, add_string + title + kind[x_index]
                    , reply_markup=show_reply_markup)
def change_button_page(call,options : typing.List,title : str,kind = typing.List):
    """
    更新投票表單
    """
    appear = vote_appear(options)
    show_reply_markup = button_array(appear)
    bot.edit_message_text(text=add_string + title+ kind[x_index] ,
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=show_reply_markup)
   
    
@bot.message_handler(commands=['start','help'])
def help_fuction(message):
    """
    使用者提示
    """
    bot.reply_to(message, """
流程簡介:
1.決定要看甚麼電影
2.決定要去甚麼電影院
3.決定要哪個時段   
                          
指令介紹:
/vm + <投票數上限> 產生電影投票表格
/vt + <投票數上限> 產生電影院投票表格(需先決定電影然後使用/next )
/ti  產生時段投票表格(需先決定電影與電影院然後使用/next )(無投票上限)
/vote + <選項名稱> 使用指令投票(可搭配投票表格上的show all一次看所有選擇)
/sv\t\t顯示有拿到票數的選項
/search\t\t顯示呼叫指令者投的所有選項
/next\t\t進行到下一步驟

圖形化介面:
show all 顯示所有選項(方便複製貼上)
""")
    
@bot.message_handler(commands=['vm'])#投電影
def show_m(message):
    global movie#初始化
    global theater
    global day_time
    movie = None   
    theater = None 
    day_time = None
    show_vote(message,movie_choice, "類型:", movie_kind)#產生表單
@bot.message_handler(commands=['vt'])#投電影院
def show_t(message):
    global theater#初始化
    global day_time
    global theater_choice
    global cities
    theater_choice,cities = bridge.get_theater(movie)
    theater = None 
    day_time = None
    if (movie == None):
        bot.reply_to(message,"請先決定電影要看甚麼")#強制使用者依照流程
        return
    
    show_vote(message,theater_choice, "城市:", cities)#產生表單
    

@bot.message_handler(commands=['ti'])#投時間
def show_time(message):
    global day_time#初始化
    global time_choice
    global day
    time_choice,day = bridge.get_time(movie,theater)
    day_time = None
    if (theater == None):
        bot.reply_to(message,"請先決定要去哪個電影院")#強制使用者依照流程
        return
    show_vote(message,time_choice, "日期:", day)#產生表單

@bot.callback_query_handler(func=lambda cb: cb.data.startswith('button_'))
def button_turn_page(call):
    """
    實現上下左右的fuction
    """
    choice = []
    kind = []


    if (movie == None):#判斷現在進行到甚麼階段
        choice = movie_choice
        kind = movie_kind
        up_down_right_left(call, choice, kind)#處理按鈕得到的資訊
        change_button_page(call,movie_choice,"類型:",movie_kind)#更新投票表單頁面
    elif (theater == None):
        choice = theater_choice
        kind = cities
        up_down_right_left(call, choice, kind)
        change_button_page(call,theater_choice,"城市:",cities)
    elif (day_time == None):
        choice = time_choice
        kind = day
        up_down_right_left(call, choice, kind)
        change_button_page(call,time_choice, "日期:", day)
    else:
        return

def up_down_right_left(call, choice, kind):
    global y_index
    global x_index
    if (call.data == "button_down" and y_index < len(choice[x_index])):#上下翻頁
        y_index += 7
    elif (call.data == "button_up" and y_index - 7 >= 0):
        y_index -= 7
    elif (call.data == "button_right" and x_index < len(kind) - 1):#左右翻頁
        x_index += 1
        y_index = 0
    elif (call.data == "button_left" and x_index > 0):
        x_index -= 1
        y_index = 0
    
@bot.callback_query_handler(func=lambda cb: cb.data.startswith('vote_'))#實現投票按鈕
def vote_fuction(call):
    user_id = call.from_user.id                #得知誰按了按鈕(用來防止一人投多次同個選項、限制每人票數上限)
    option_choice = call.data[5:len(call.data)]#得知按鈕上對應的名稱(用來update票數)
    if (option_choice == "empty"):   #處理空白選項          
        return
    else:
        vote_board_change(user_id, option_choice)#投票統計
        if (movie == None):
            change_button_page(call,movie_choice,"類型:",movie_kind)#投票顯示
        elif (theater == None):
            change_button_page(call,theater_choice,"城市:",cities)
        elif (day_time == None):
            change_button_page(call,time_choice, "日期:", day)
        else:
            return
@bot.callback_query_handler(func=lambda cb: cb.data.startswith('show_all'))
def show_all(call):#實現選項一覽
    global show_all_bool
    global add_string
    add_string = "選項一覽:\n"
    choice = []
    kind = []
    title = ""
    if (movie == None):#判斷現在正在進行甚麼階段
        choice = movie_choice
        kind = movie_kind
        title = "類型:"
    elif(theater == None):
        choice = theater_choice
        kind = cities
        title = "城市:"
    elif(day_time == None):
        choice = time_choice
        kind = day
        title = "日期:"
    else:
        return
    if (show_all_bool == False):#如果show all沒有被打開，打開它
        show_all_bool = True
        for x in choice:
            for y in x:
                add_string += ' ' + y + '\n'#將所有選項輸進一個字串中
        add_string += '\n'
    else:                      #如果show all已被打開，關上它
        show_all_bool = False

    change_button_page(call,choice, title,kind)#更新投票表單
    
@bot.message_handler(commands=['vote'])#直接投票
def show_vote_result(message):
    user_id = message.from_user.id    #得知誰按了按鈕(用來防止一人投多次同個選項、限制每人票數上限)
    option_choice = ""
    if (str(message.text).find("@") != -1):
        option_choice = message.text[6:message.text.find("@")]
    else:
        option_choice = message.text[6:len(message.text)]
    if (option_choice in get_vote.keys()):
        vote_board_change(user_id, option_choice)#投票統計
    else:
        bot.reply_to(message,"名稱不正確")


def vote_board_change(user_id, option_choice):



    access_to_vote = True

    if (user_id in user_vote.keys() and len(user_vote[user_id]) >= person_vote_num):#超過票數上限不能再投票，只能取消
        access_to_vote = False
    
    if ((option_choice in get_vote.keys()) == False and access_to_vote):#選了之前沒人投的選項
        get_vote[option_choice] = 1

    elif((option_choice in user_vote[user_id]) == False and access_to_vote):#之前有人投過
        get_vote[option_choice] += 1*access_to_vote

    elif(option_choice in user_vote[user_id]):#之前自己投過，按一下取消投票
        get_vote[option_choice] -= 1
        if (get_vote[option_choice] == 0):
            del get_vote[option_choice]

    if ((user_id in user_vote.keys()) == False):#紀錄某user投過某選項
        user_vote[user_id] = [option_choice]

    elif((option_choice in user_vote[user_id]) == False and access_to_vote):
        user_vote[user_id].append(option_choice)
    elif(option_choice in user_vote[user_id]):#紀錄某user取消某選項
        user_vote[user_id].remove(option_choice)


def highest_option() -> typing.List :#找到最高票
    keys = get_vote.keys()
    max_num = 0
    max_names = []

    for k in keys:#疊帶暴力尋找
        if (get_vote[k] > max_num):
            max_num = get_vote[k]
            max_names = [k]
        elif(get_vote[k] == max_num):
            max_names.append(k)
    return max_names
    
@bot.message_handler(commands=['sv'])#顯示投票狀態
def show_vote_result(message):
    if (len(get_vote.keys()) == 0):
        bot.reply_to(message,"尚未投票")
    result = ""
    for k in get_vote.keys():
        result += k + " 獲得:" + str(get_vote[k]) + "票\n"
    bot.reply_to(message,result)

@bot.message_handler(commands=['next'])#進行到下一階段
def next(message):
    global movie
    global theater
    global day_time


    vote_highest_name = highest_option()
    
    if (len(vote_highest_name) == 0):#強制使用者依照流程
        bot.reply_to(message, "尚未投票")
        return
    elif(len(vote_highest_name) == 1):#有唯一最高票
        vote_highest_name = vote_highest_name[0]
    elif(movie == None or theater == None):         #有多個最高票->繼續投到唯一最高票產生
        show = ""
        for s in vote_highest_name:
            show += s + '\n'
        bot.reply_to(message, "有複數最高票:\n" + show + "請再投票以選出最高票者")
        return
    else:
        day_time = ""

        for vhn in vote_highest_name:
            day_time += vhn + '\n'

        bot.reply_to(message, "結果如下:\n" + "電影:" + movie + '\n' +
"電影院:" + theater + '\n' + 
"最多人可以的時間:" + '\n' + day_time )#結束，產生投票資訊
    if (movie == None):
        movie = vote_highest_name
        bot.reply_to(message, "那麼，就決定看:" + movie + "\n/vt 開始決定要去哪間電影院")
    elif (theater == None):
        theater = vote_highest_name
        bot.reply_to(message, "那麼，就決定去:" + theater + "看電影\n/ti 開始決定要甚麼時段")
    
        
        
    
@bot.message_handler(commands=['search'])#查詢自己投了甚麼
def search(message):
    user = message.from_user.id
    if ((user in user_vote.keys()) and len(user_vote[user]) != 0):
        reply = ""
        for s in user_vote[user]:
            reply += s + '\n'
        bot.reply_to(message, "你投了:\n" + reply)
    else:
        bot.reply_to(message, "你尚未投票")


bot.infinity_polling()