import typing 
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultPhoto

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
movie_choice = [["m1","m2","m3","m4","m5","m6","m7","m8","m9"],
                ["m10","m11","m12"],["m13","m14","m15"]]
movie_kind = ["kind1","kind2","kind3"]
#電影院
theater_choice = [["t__1","t__2","t__3","t__4","t__5","2t1","2t2","2t3","2t4","2t5","2t1","2t2","2t3","2t4","2t5"],
                  ["2t1","2t2","2t3","2t4","2t5"],["t__1","t__2","t__3","t__4","t__5"]]
cities = ["city 1","city 2","city 3"]

#時間
time_choice = [["1","2","3","4","5","6","7","8"],
                  ["1","2","3","4","5","6","7","8"],
                  ["1","2","3","4","5","6","7","8"],
                  ["1","2","3","4","5","6","7","8"],
                  ["1","2","3","4","5","6","7","8"]]
day = ["1","2","3","4","5"]

y_index = 0 
x_index = 0
get_vote = {} #{選項 : 票數}
user_vote = {}#{id:[選項,]}

#儲存上下左右
turn_page_button = [InlineKeyboardButton("left", callback_data="button_left"),
                    InlineKeyboardButton("up", callback_data="button_up"),
                    InlineKeyboardButton("right", callback_data="button_right"),
                InlineKeyboardButton("down", callback_data="button_down"),
            ]

def vote_appear(options : typing.List):#選項排版

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
    show_theater_reply_markup = InlineKeyboardMarkup()
    for t in t_appear:
        show_theater_reply_markup.add(t)
    show_theater_reply_markup.add(*turn_page_button)
    show_theater_reply_markup.add(InlineKeyboardButton("show all",callback_data="show_all"))
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
    user_vote = {}
    vote_hightest_num = 0

    text_len = len(message.text)

    
    if (text_len == 3 or str(message.text).find("@") == 3):
        person_vote_num = 1
    else:
        if (str(message.text).find("@") != -1):
            person_vote_num = int(message.text[4:str(message.text).find("@")])
        else:
            person_vote_num = int(message.text[4:len(message.text)])
        
    appear = vote_appear(options)
    show_reply_markup = button_array(appear)
    bot.send_message(message.chat.id, add_string + title + kind[x_index]
                    , reply_markup=show_reply_markup)
def change_button_page(call,options : typing.List,title : str,kind = typing.List):
    """
    視窗刷新
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
/ti + <投票數上限> 產生時段投票表格(需先決定電影與電影院然後使用/next )
/vote + <選項名稱> 使用指令投票(可搭配投票表格上的show all一次看所有選擇)
/sv               顯示有拿到票數的選項
/search           顯示呼叫指令者投的所有選項
/next             進行到下一步驟

圖形化介面:
show all 顯示所有選項(方便複製貼上)
""")
    
@bot.message_handler(commands=['vm'])#投電影
def show_m(message):
    global movie
    global theater
    global day_time
    movie = None   
    theater = None 
    day_time = None
    show_vote(message,movie_choice, "類型:", movie_kind)
@bot.message_handler(commands=['vt'])#投電影院
def show_t(message):
    global theater
    global day_time
    theater = None 
    day_time = None
    if (movie == None):
        bot.reply_to(message,"請先決定電影要看甚麼")
        return
    
    show_vote(message,theater_choice, "城市:", cities)
    

@bot.message_handler(commands=['ti'])#投時間
def show_time(message):
    global day_time
    day_time = None
    show_vote(message,time_choice, "日期:", day)

@bot.callback_query_handler(func=lambda cb: cb.data.startswith('button_'))
def theater_view(call):
    global y_index
    global x_index
    global call_mcid 
    global call_mmid

    if (call.data == "button_down" and y_index < len(theater_choice[x_index])):
        y_index += 7
    elif (call.data == "button_up" and y_index - 7 >= 0):
        y_index -= 7
    elif (call.data == "button_right" and x_index < len(cities) - 1):
        x_index += 1
        y_index = 0
    elif (call.data == "button_left" and x_index > 0):
        x_index -= 1
        y_index = 0
    else:
        return
    
    if (movie == None):
        change_button_page(call,movie_choice,"類型:",movie_kind)
    elif (theater == None):
        change_button_page(call,theater_choice,"城市:",cities)
    elif (day_time == None):
        change_button_page(call,time_choice, "日期:", day)
    else:
        return
    
@bot.callback_query_handler(func=lambda cb: cb.data.startswith('vote_'))
def vote_fuction(call):
    user_id = call.from_user.id
    option_choice = call.data[5:len(call.data)]
    if (option_choice == "empty"):
        return
    else:
        vote_board_change(user_id, option_choice)
        if (movie == None):
            change_button_page(call,movie_choice,"類型:",movie_kind)
        elif (theater == None):
            change_button_page(call,theater_choice,"城市:",cities)
        elif (day_time == None):
            change_button_page(call,time_choice, "日期:", day)
        else:
            return
@bot.callback_query_handler(func=lambda cb: cb.data.startswith('show_all'))
def show_all(call):
    global show_all_bool
    global add_string
    add_string = ""
    choice = []
    kind = []
    title = ""
    if (movie == None):
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
    if (show_all_bool == False):
        show_all_bool = True
        for x in choice:
            for y in x:
                add_string += ' ' + y + '\n'
        add_string += '\n'
    else:
        show_all_bool = False

    change_button_page(call,choice, add_string + title,kind)
    
@bot.message_handler(commands=['vote'])#直接投票
def show_vote_result(message):
    user_id = message.from_user.id
    option_choice = ""
    if (str(message.text).find("@") != -1):
        option_choice = message.text[6:message.text.find("@")]
    else:
        option_choice = message.text[6:len(message.text)]
    print(option_choice)
    vote_board_change(user_id, option_choice)


def vote_board_change(user_id, option_choice):



    access_to_vote = True

    if (user_id in user_vote.keys() and len(user_vote[user_id]) >= person_vote_num):
        access_to_vote = False
    
    if ((option_choice in get_vote.keys()) == False and access_to_vote):
        get_vote[option_choice] = 1

    elif((option_choice in user_vote[user_id]) == False and access_to_vote):
        get_vote[option_choice] += 1*access_to_vote

    elif(option_choice in user_vote[user_id]):
        get_vote[option_choice] -= 1
        if (get_vote[option_choice] == 0):
            del get_vote[option_choice]

    if ((user_id in user_vote.keys()) == False):
        user_vote[user_id] = [option_choice]

    elif((option_choice in user_vote[user_id]) == False and access_to_vote):
        user_vote[user_id].append(option_choice)
    elif(option_choice in user_vote[user_id]):
        user_vote[user_id].remove(option_choice)


def highest_option() -> typing.List :#找到最高票
    keys = get_vote.keys()
    max_num = 0
    max_names = []

    for k in keys:
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
    
    if (len(vote_highest_name) == 0):
        bot.reply_to(message, "尚未投票")
        return
    elif(len(vote_highest_name) == 1):
        vote_highest_name = vote_highest_name[0]
    else:
        show = ""
        for s in vote_highest_name:
            show += s + '\n'
        bot.reply_to(message, "有複數最高票:\n" + show + "請再投票以選出最高票者")
        return
    

    if (movie == None):
        movie = vote_highest_name
        bot.reply_to(message, "那麼，就決定看:" + movie + "\n/vt 開始決定要去哪間電影院")
    elif (theater == None):
        theater = vote_highest_name
        bot.reply_to(message, "那麼，就決定去:" + theater + "看電影\n/ti 開始決定要甚麼時段")
    else:
        day_time = vote_highest_name
        bot.reply_to(message, "結果如下:" + "電影:" + movie + '\n' +
"電影院:" + theater + '\n' + 
"時間:" + day_time + '\n')
    
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