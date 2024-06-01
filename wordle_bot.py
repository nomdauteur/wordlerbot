import random
import os
import telebot
from systemd import journal
import mariadb
from datetime import date

dir = os.path.dirname(__file__)
journal.write(os.environ['W_TOKEN'])
TOKEN = os.environ['W_TOKEN']
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

def send_help(chat_id):
    m='''Your objective is to guess a secret five-letter word in as few guesses as possible. To submit a guess, type any five-letter word and press enter. All of your guesses must be real words. The bot will color-code each letter in your guess to tell you how close it was to the letters in the hidden word.
A gray or black square means that this letter does not appear in the secret word at all.
A yellow square means that this letter appears in the secret word, but it’s in the wrong spot within the word.
A green square means that this letter appears in the secret word, and it’s in exactly the right place.
You'll have six tries to guess the word.
Press /start to play.
___
Цель игры — как можно быстрее угадать слово из пяти букв. Наберите любое существующее слово из пяти букв и отправьте боту. В ответ он пришлет вам результат вашей попытки. 
Серый квадрат на месте буквы значит, что ее в слове нет. 
Желтый — такая буква есть, но на другом месте.
Зеленый — такая буква есть, и именно здесь.
На то, чтобы угадать слово, у вас будет шесть попыток.
Нажмите /start, чтобы сыграть.'''
    bot.send_message(chat_id,m)    

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


@bot.message_handler(commands=['help'])
def helper(message):
    send_help(message.chat.id)

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
    if (text is None):
        bot.send_message(chat_id, 'Input must not be empty! Press /start to go on')
        return
    if (message.text == '/help'):
        send_help(chat_id)
    variables[chat_id]['mode'] = 'RUS' if text == 'RUS' else 'ENG'
    with open(dir + '/' + ('eng' if variables[chat_id]['mode'] == 'ENG' else 'rus') + '_fivers.txt',
              encoding="utf-8") as f:
        with open(dir + '/' + ('eng' if variables[chat_id]['mode'] == 'ENG' else 'rus') + '_all_fivers.txt',
              encoding="utf-8") as f1:
            variables[chat_id]['wordlist'] = f1.readlines()
            variables[chat_id]['wordlist_selectable'] = f.readlines()
            variables[chat_id]['word'] = random.choice(variables[chat_id]['wordlist_selectable'])
    journal.write(str(chat_id)+': Word is chosen: ' + variables[chat_id]['word'])
    msg = bot.send_message(chat_id, '6 tries left. Input your word.' if variables[chat_id]['mode'] == 'ENG' else 'Введите слово. У вас 6 попыток',
                           reply_markup=None)
    bot.register_next_step_handler(msg, guessStep)


def guessStep(message):
    chat_id = message.chat.id
    text = message.text
    if (text is None):
        bot.send_message(chat_id, 'Input must not be empty! Press /start to go on')
        return
    if (message.text == '/help'):
        send_help(chat_id)
    if (text is not None):
        text = text.lower()
    journal.write(str(chat_id)+': Step no ' + str(variables[chat_id]['tries']))
    journal.write(text)
    # check word
    if (text is not None) and len(text) != 5:
        msg = bot.send_message(chat_id,
                               'Word must be 5 characters long\n' + str(variables[chat_id]['tries']) + ' tries left' if
                               variables[chat_id][
                                   'mode'] == 'ENG' else 'Слово должно быть длиной в 5 букв\nУ вас ' + str(
                                   variables[chat_id]['tries']) + (' попыток' if variables[chat_id][
                                                                                     'tries'] >= 5 else ' попытки' if
                               variables[chat_id]['tries'] > 1 else ' попытка'), reply_markup=None)
        bot.register_next_step_handler(msg, guessStep)
    elif text + '\n' not in variables[chat_id]['wordlist']:
        journal.write(str(chat_id)+': Candidate: ' + text)
        msg = bot.send_message(chat_id, 'Word must be present in dictionary\n' + str(
            variables[chat_id]['tries']) + ' tries left' if variables[chat_id][
                                                                'mode'] == 'ENG' else 'Слово должно встречаться в словаре\nУ вас ' + str(
            variables[chat_id]['tries']) + (' попыток' if variables[chat_id]['tries'] >= 5 else ' попытки' if
        variables[chat_id]['tries'] > 1 else ' попытка'), reply_markup=None)
        bot.register_next_step_handler(msg, guessStep)
    else:
        variables[chat_id]['tries'] -= 1
        res=[]
        occurs=[]
        greens = {}
        for g in [chr(i) for i in range(ord('a'),ord('z')+1)]:
            greens[g]=0
        for g in [chr(i) for i in range(ord('а'),ord('я')+1)]:
            greens[g]=0
        greens['ё']=0
        for pos in range(0, 5):
            occurs.append(text[:pos+1].count(text[pos]))
            if text[pos] == variables[chat_id]['word'][pos]:
                res.append('b')
                greens[text[pos]] = greens[text[pos]] + 1
                
            elif (text[pos] in variables[chat_id]['word']):
                res.append('c')
                
            else:
                res.append('_')
                
        for pos in range(0, 5):
            if (res[pos] == 'c' and occurs[pos] > (variables[chat_id]['word'].count(text[pos]) - greens[text[pos]])):
                res[pos] = '_'
        (variables[chat_id]['res']).append(''.join(res))
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
                '\n' + str(variables[chat_id]['tries']) + ' tries left. Input your word.' if variables[chat_id][
                                                                               'mode'] == 'ENG' else '\nВведите слово. У вас ' + str(
                    variables[chat_id]['tries']) + (' попыток' if variables[chat_id]['tries'] >= 5 else ' попытки' if
                variables[chat_id]['tries'] > 1 else ' попытка')), reply_markup=None)
            bot.register_next_step_handler(msg, guessStep)


bot.polling(none_stop=True)