import random
import os
import telebot
dir = os.path.dirname(__file__)
TOKEN = '5035471046:AAGoP2kz6lq9eRT_R9CFJYNu_gNCaBS9jeI'
bot = telebot.TeleBot(TOKEN)
mode = 'ENG' #to be set by bot command
wordlist=[]

variables={}

#handlers
@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    chat_id = message.chat.id
    variables[chat_id]={}
    #variables[chat_id]['mode']=mode
    variables[chat_id]['tries']=5
    msg = bot.send_message(chat_id, 'Выберите язык')
    bot.register_next_step_handler(msg, asklang)

def askLang(message):
    text=message.text
    variables[chat_id]['mode'] = text
    with open(dir + '/' + ('eng' if variables[chat_id]['mode'] == 'ENG' else 'rus') + '_fivers.txt', encoding="utf-8") as f:
        wordlist = f.readlines()
        variables[chat_id]['word'] = random.choice(wordlist)
    msg = bot.send_message(chat_id, 'Осталось 5 попыток')
    bot.register_next_step_handler(msg, guessStep)

def guessStep(message):
    chat_id = message.chat.id
    text=message.text
    #check word
    if len(text)!=5:
        msg = bot.send_message(chat_id, 'Your word must be 5 letters')
        bot.register_next_step_handler(msg, guessStep)
    elif text+'\n' not in wordlist:
        msg = bot.send_message(chat_id, 'Your word must be from dictionary')
        bot.register_next_step_handler(msg, guessStep)
    else:
        variables[chat_id]['tries']-=1
        res=''
        for pos in range (0,5):
            if text[pos]==variables[chat_id]['word'][pos]:
                res+='b'
            elif text[pos] in variables[chat_id]['word']:
                res+='c'
            else:
                res+='_'
        #print('your try is: '+res)
        msg = bot.send_message(chat_id, res)
        if (res == 'bbbbb'):
            msg = bot.send_message(chat_id, 'You won!')
            return
        elif variables[chat_id]['tries'] == 0:
            msg = bot.send_message(chat_id, 'К сожалению, попытки закончились. Слово было: '+ variables[chat_id]['word'])
            return

bot.polling(none_stop=True)