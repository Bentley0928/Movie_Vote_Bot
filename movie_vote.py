import telebot

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultPhoto

token = "6296100029:AAEajKtQNCxpJWTuG6qTd86pf9PdT-yZG64"

bot = telebot.TeleBot(token)

theater = None
movie = None


#選電影院需要的東西
theater_choice = [["t__1","t__2","t__3","t__4","t__5"],["2t1","2t2","2t3","2t4","2t5"],["t__1","t__2","t__3","t__4","t__5"]]
cities = ["city 1","city 2","city 3"]
theater_index = 0
cities_index = 0



def theater_appear():
    theater_choice_appear = ""
    for i in range(len(theater_choice[cities_index])):
        theater_choice_appear += "  "*6
        if (i == theater_index):
            theater_choice_appear += theater_choice[cities_index][i] + '<<' + '\n'
        else:
            theater_choice_appear += theater_choice[cities_index][i] + '\n'
    return theater_choice_appear

vote_theater_reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("up", callback_data="t_up"),
                InlineKeyboardButton("down", callback_data="t_down"),
                InlineKeyboardButton("left", callback_data="t_left"),
                InlineKeyboardButton("right", callback_data="t_right"),
                InlineKeyboardButton("vote", callback_data="t_vote"),
                
            ]
        ])


@bot.message_handler(commands=['start','help'])
def help_fuction(message):
    """
    使用者提示
    """
    bot.reply_to(message, """/vote 發起投票
""")


@bot.message_handler(commands=['vote'])
def vote(message):
    
    if (theater == None):
        
        theater_choice_appear = theater_appear()

        

        bot.reply_to(message, '城市：'+ cities[cities_index] + '\n' + 
                     theater_choice_appear
                     , reply_markup=vote_theater_reply_markup)




@bot.callback_query_handler(func=lambda cb: cb.data.startswith('t_'))
def time_cb(call):
    global theater_index
    global cities_index

    if (call.data == "t_down" and theater_index < len(theater_choice[cities_index]) - 1):
        theater_index += 1
    elif (call.data == "t_up" and theater_index > 0):
        theater_index -= 1
    elif (call.data == "t_right" and cities_index < len(cities) - 1):
        cities_index += 1
    elif (call.data == "t_left" and cities_index > 0):
        cities_index -= 1
    else:
        return

    theater_choice_appear = theater_appear()
    print(theater_choice_appear)
    
    bot.edit_message_text(text='城市：'+ cities[cities_index] + '\n' + 
                     theater_choice_appear,
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=vote_theater_reply_markup)
    

bot.infinity_polling()