import random
import os
import telebot
from systemd import journal
import mariadb
from datetime import date

dir = os.path.dirname(__file__)
TOKEN = '5035471046:AAGoP2kz6lq9eRT_R9CFJYNu_gNCaBS9jeI'
bot = telebot.TeleBot(TOKEN)
mode = 'ENG'  # to be set by bot command
wordlist = []

variables = {}

def getBoard(array):
    board=''
    for j in array:
        for i in j:
            if i == '_':
                board += '⬜'
            elif i == 'c':
                board += '🟨'
            elif i == 'b':
                board += '🟩'
        board+='\n'
    return board

try:
    conn = mariadb.connect(
        user="wordlerbot",
        password="i4mp455w0rd_",
        host="localhost",
        database="bot_db"

    )
    journal.write("Connected well")
except mariadb.Error as e:
    journal.write(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()


# handlers
@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    #journal.write(message)
    chat_id = message.chat.id
    d = str(date.today())
    name=' '.join(filter(None, (message.chat.first_name, message.chat.last_name)))
    try:
        
        cur.execute(
    "INSERT INTO wordlerbot_users (id, name, alias, comment) VALUES (?, ?, ?, ?) ON DUPLICATE KEY UPDATE name=?, alias=?, comment=?", 
    (chat_id, name, message.chat.username, d, name, message.chat.username, d) )
        conn.commit()
        journal.write(f"Inserted {chat_id}")
    except mariadb.Error as e:
        journal.write(f"Error in db: {e}")
    

    variables[chat_id] = {}
    # variables[chat_id]['mode']=mode
    variables[chat_id]['tries'] = 6
    variables[chat_id]['res'] = []
    
    lng = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    lng_btn1 = telebot.types.KeyboardButton('ENG')
    lng_btn2 = telebot.types.KeyboardButton('RUS')
    lng.add(lng_btn1, lng_btn2)
    msg = bot.send_message(chat_id, 'Выберите язык | Choose your language', reply_markup=lng)

    bot.register_next_step_handler(msg, askLang)


def askLang(message):
    chat_id = message.chat.id
    text = message.text
    variables[chat_id]['mode'] = 'RUS' if text == 'RUS' else 'ENG'
    with open(dir + '/' + ('eng' if variables[chat_id]['mode'] == 'ENG' else 'rus') + '_fivers.txt',
              encoding="utf-8") as f:
        with open(dir + '/' + ('eng' if variables[chat_id]['mode'] == 'ENG' else 'rus') + '_all_fivers.txt',
              encoding="utf-8") as f1:
            variables[chat_id]['wordlist'] = f1.readlines()
            variables[chat_id]['wordlist_selectable'] = f.readlines()
            variables[chat_id]['word'] = random.choice(variables[chat_id]['wordlist_selectable'])
    journal.write(str(chat_id)+': Word is chosen: ' + variables[chat_id]['word'])
    msg = bot.send_message(chat_id, '6 tries left' if variables[chat_id]['mode'] == 'ENG' else 'Осталось 6 попыток',
                           reply_markup=None)
    bot.register_next_step_handler(msg, guessStep)


def guessStep(message):
    chat_id = message.chat.id
    text = message.text
    if (len(text)>0):
        text = text.lower()
    journal.write(str(chat_id)+': Step no ' + str(variables[chat_id]['tries']))
    # check word
    if len(text) != 5:
        msg = bot.send_message(chat_id,
                               'Word must be 5 characters long\n' + str(variables[chat_id]['tries']) + ' tries left' if
                               variables[chat_id][
                                   'mode'] == 'ENG' else 'Слово должно быть длиной в 5 букв\nОсталось ' + str(
                                   variables[chat_id]['tries']) + (' попыток' if variables[chat_id][
                                                                                     'tries'] >= 5 else ' попытки' if
                               variables[chat_id]['tries'] > 1 else ' попытка'), reply_markup=None)
        bot.register_next_step_handler(msg, guessStep)
    elif text + '\n' not in variables[chat_id]['wordlist']:
        journal.write(str(chat_id)+': Candidate: ' + text)
        msg = bot.send_message(chat_id, 'Word must be present in dictionary\n' + str(
            variables[chat_id]['tries']) + ' tries left' if variables[chat_id][
                                                                'mode'] == 'ENG' else 'Слово должно встречаться в словаре\nОсталось ' + str(
            variables[chat_id]['tries']) + (' попыток' if variables[chat_id]['tries'] >= 5 else ' попытки' if
        variables[chat_id]['tries'] > 1 else ' попытка'), reply_markup=None)
        bot.register_next_step_handler(msg, guessStep)
    else:
        variables[chat_id]['tries'] -= 1
        res=''
        for pos in range(0, 5):
            if text[pos] == variables[chat_id]['word'][pos]:
                res += 'b'
            elif text[pos] in variables[chat_id]['word']:
                res += 'c'
            else:
                res += '_'
        (variables[chat_id]['res']).append(res)
        if (variables[chat_id]['res'][len(variables[chat_id]['res'])-1] == 'bbbbb'):
            bot.send_message(chat_id, getBoard(variables[chat_id]['res']), reply_markup=None)
            
            msg = bot.send_message(chat_id, 'You won. Send /start to play again' if variables[chat_id][
                                                                                        'mode'] == 'ENG' else 'Победа! Отправьте /start для новой игры',
                                   reply_markup=None)
            journal.write(str(chat_id)+': Word guessed')
            return
        elif variables[chat_id]['tries'] == 0:
            bot.send_message(chat_id, getBoard(variables[chat_id]['res']), reply_markup=None)
            msg = bot.send_message(chat_id, 'Sorry, all 6 tries are out. The word was: ' + variables[chat_id][
                'word'] + '\nSend /start to play again' if variables[chat_id][
                                                               'mode'] == 'ENG' else 'К сожалению, попытки закончились. Слово было: ' +
                                                                                     variables[chat_id][
                                                                                         'word'] + '\nОтправьте /start для новой игры',
                                   reply_markup=None)
            return
        else:
            answer = ''
            answer=getBoard([variables[chat_id]['res'][5-variables[chat_id]['tries']]])
            msg = bot.send_message(chat_id, answer + (
                '\n' + str(variables[chat_id]['tries']) + ' tries left' if variables[chat_id][
                                                                               'mode'] == 'ENG' else '\nОсталось ' + str(
                    variables[chat_id]['tries']) + (' попыток' if variables[chat_id]['tries'] >= 5 else ' попытки' if
                variables[chat_id]['tries'] > 1 else ' попытка')), reply_markup=None)
            bot.register_next_step_handler(msg, guessStep)


bot.polling(none_stop=True)