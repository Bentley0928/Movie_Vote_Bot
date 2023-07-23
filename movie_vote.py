import typing 
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultPhoto

token = "6618282878:AAHxSA6x_syoEijH83R80f4M-uBlqKN0l4E"

bot = telebot.TeleBot(token)

theater = None
movie = None
vote_hightest_name = ""
vote_hightest_num = 0

person_vote_num = 0

#電影
movie_choice = [["m1","m2","m3","m4","m5","m6","m7","m8","m9"],
                ["m10","m11","m12"],["m13","m14","m15"]]
movie_kind = ["kind1","kind2","kind3"]
#選電影院需要的東西
theater_choice = [["t__1","t__2","t__3","t__4","t__5","2t1","2t2","2t3","2t4","2t5","2t1","2t2","2t3","2t4","2t5"],
                  ["2t1","2t2","2t3","2t4","2t5"],["t__1","t__2","t__3","t__4","t__5"]]
cities = ["city 1","city 2","city 3"]
y_index = 0
x_index = 0
get_vote = {}
user_vote = {}#id:[options]

turn_page_button = [InlineKeyboardButton("left", callback_data="button_left"),
                    InlineKeyboardButton("up", callback_data="button_up"),
                    InlineKeyboardButton("right", callback_data="button_right"),
                InlineKeyboardButton("down", callback_data="button_down"),
                 
            ]

def vote_appear(options : typing.List):#選項排版

    global y_index
    choice_appear = []
    this_page = options[x_index]
    for i in range(y_index , y_index + 7):
        if (i < len(this_page)):
            votes = 0
            if (this_page[i] in get_vote):
                votes = get_vote[this_page[i]]
            choice_appear.append(InlineKeyboardButton(this_page[i] + " " + str(votes) + "票",
                                     callback_data="vote_"+this_page[i]))
        else:
            choice_appear.append(InlineKeyboardButton(" ",
                                     callback_data="vote_"+"empty"))
    return choice_appear



def button_array(t_appear : typing.List):#按鈕整合
    """
    t_appear = vote_appear
    """
    show_theater_reply_markup = InlineKeyboardMarkup()
    for t in t_appear:
        show_theater_reply_markup.add(t)
    show_theater_reply_markup.add(*turn_page_button)
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
    global vote_hightest_name 
    global vote_hightest_num
    y_index = 0
    x_index = 0
    get_vote = {}
    user_vote = {}
    vote_hightest_num = 0

    if (len(message.text) == 3):
        person_vote_num = 1
    else:
        person_vote_num = int(message.text[4:len(message.text)])

    appear = vote_appear(options)
    show_reply_markup = button_array(appear)
    bot.send_message(message.chat.id, title + kind[x_index]
                    , reply_markup=show_reply_markup)
def change_button_page(call,options : typing.List,title : str,kind = typing.List):
    """
    投票視窗換頁
    """
    appear = vote_appear(options)
    show_reply_markup = button_array(appear)
    bot.edit_message_text(text=title+ kind[x_index] ,
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=show_reply_markup)

    
@bot.message_handler(commands=['start','help'])
def help_fuction(message):
    """
    使用者提示
    """
    bot.reply_to(message, """/vt + <一人投票上限> 顯示電影院
/vm + <一人投票上限> 投電影
/sv 查看投票狀態
/next 進入下個投票階段
""")

@bot.message_handler(commands=['vt'])#投電影院
def show_t(message):
    
    if (movie == None):
        bot.reply_to(message,"請先決定電影要看甚麼")
        return
    
    show_vote(message,theater_choice, "城市:", cities)
    


@bot.message_handler(commands=['vm'])#投電影
def show_m(message):
    
    show_vote(message,movie_choice, "類型:", movie_kind)

@bot.callback_query_handler(func=lambda cb: cb.data.startswith('button_'))
def theater_view(call):
    global y_index
    global x_index

    
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
        else:
            return

def vote_board_change(user_id, option_choice):

    global vote_hightest_num
    global vote_hightest_name

    access_to_vote = True

    if (user_id in user_vote.keys() and len(user_vote[user_id]) >= person_vote_num):
        access_to_vote = False
    
    if ((option_choice in get_vote.keys()) == False and access_to_vote):
        get_vote[option_choice] = 1

    elif((option_choice in user_vote[user_id]) == False and access_to_vote):
        get_vote[option_choice] += 1*access_to_vote

    elif(option_choice in user_vote[user_id]):
        get_vote[option_choice] -= 1

    if ((user_id in user_vote.keys()) == False):
        user_vote[user_id] = [option_choice]

    elif((option_choice in user_vote[user_id]) == False and access_to_vote):
        user_vote[user_id].append(option_choice)
    elif(option_choice in user_vote[user_id]):
        user_vote[user_id].remove(option_choice)

    if ((option_choice in user_vote[user_id]) and get_vote[option_choice] > vote_hightest_num):
        vote_hightest_num = get_vote[option_choice]
        vote_hightest_name = option_choice
    

@bot.message_handler(commands=['sv'])#顯示投票狀態
def show_vote_result(message):
    if (len(get_vote.keys()) == 0):
        bot.reply_to(message,"尚未投票")
    result = ""
    for k in get_vote.keys():
        result += k + " 獲得:" + str(get_vote[k]) + "票\n"
    bot.reply_to(message,result)

@bot.message_handler(commands=['next'])#顯示投票狀態
def show_vote_result(message):
    global movie
    global theater
    if (movie == None):
        movie = vote_hightest_name
        bot.reply_to(message, "那麼，就決定看:" + movie + "\n/vt 開始決定要去哪間電影院")
    elif (theater == None):
        theater = vote_hightest_name



bot.infinity_polling()