import typing 
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultPhoto

token = "6618282878:AAHxSA6x_syoEijH83R80f4M-uBlqKN0l4E"

bot = telebot.TeleBot(token)

theater = None
movie = None


#電影
movie_choice = [["m1","m2","m3","m1","m2","m3","m1","m2","m3"],
                ["m1","m2","m3"],["m1","m2","m3"]]
movie_kind = ["kind1","kind2","kind3"]
#選電影院需要的東西
theater_choice = [["t__1","t__2","t__3","t__4","t__5","2t1","2t2","2t3","2t4","2t5","2t1","2t2","2t3","2t4","2t5"],
                  ["2t1","2t2","2t3","2t4","2t5"],["t__1","t__2","t__3","t__4","t__5"]]
cities = ["city 1","city 2","city 3"]
y_index = 0
x_index = 0
theater_get_vote = {}

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
            choice_appear.append(InlineKeyboardButton(this_page[i],
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

@bot.message_handler(commands=['start','help'])
def help_fuction(message):
    """
    使用者提示
    """
    bot.reply_to(message, """/vt 顯示電影院
/vm 投電影
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

def show_vote(message,options : typing.List,title : str,kind = typing.List):
    global y_index
    global x_index
    y_index = 0
    x_index = 0
    appear = vote_appear(options)
    show_reply_markup = button_array(appear)
    bot.send_message(message.chat.id, title + kind[x_index]
                    , reply_markup=show_reply_markup)


@bot.callback_query_handler(func=lambda cb: cb.data.startswith('button_'))
def theater_view(call):
    global y_index
    global x_index

    print(call.from_user.id)
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

def change_button_page(call,options : typing.List,title : str,kind = typing.List):
    appear = vote_appear(options)
    show_reply_markup = button_array(appear)
    bot.edit_message_text(text=title+ kind[x_index] ,
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=show_reply_markup)


        



bot.infinity_polling()