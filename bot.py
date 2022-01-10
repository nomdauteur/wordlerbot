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
    print('chat id is '+str(chat_id))
    variables[chat_id]={}
    #variables[chat_id]['mode']=mode
    variables[chat_id]['tries']=5
    print('Choosing lang')
    msg = bot.send_message(chat_id, 'Выберите язык')
    bot.register_next_step_handler(msg, askLang)

def askLang(message):
    chat_id = message.chat.id
    text=message.text
    variables[chat_id]['mode'] = text
    with open(dir + '/' + ('eng' if variables[chat_id]['mode'] == 'ENG' else 'rus') + '_fivers.txt', encoding="utf-8") as f:
        variables[chat_id]['wordlist'] = f.readlines()
        variables[chat_id]['word'] = random.choice(variables[chat_id]['wordlist'])
    print('Word is chosen: '+ variables[chat_id]['word'])
    msg = bot.send_message(chat_id, 'Осталось 5 попыток')
    bot.register_next_step_handler(msg, guessStep)

def guessStep(message):
    chat_id = message.chat.id
    text=message.text
    print('Step no '+str(variables[chat_id]['tries']))
    #check word
    if len(text)!=5:
        msg = bot.send_message(chat_id, 'Слово должно быть длиной в 5 букв')
        bot.register_next_step_handler(msg, guessStep)
    elif text+'\n' not in variables[chat_id]['wordlist']:
        msg = bot.send_message(chat_id, 'Слово должно существовать в словаре')
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
        if (res == 'bbbbb'):
            msg = bot.send_message(chat_id, 'You won!')
            return
        elif variables[chat_id]['tries'] == 0:
            msg = bot.send_message(chat_id, 'К сожалению, попытки закончились. Слово было: '+ variables[chat_id]['word'])
            return
        else:
            msg = bot.send_message(chat_id, res)
            bot.register_next_step_handler(msg, guessStep)

bot.polling(none_stop=True)