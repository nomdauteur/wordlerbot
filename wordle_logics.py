import random
dir='C:\\Users\\ekaterina.morozova\\Desktop\\wordle'
mode = 'ENG' #to be set by bot command
wordlist=[]
#Choosing the word
with open(dir+'\\'+('eng' if mode == 'ENG' else 'rus')+'_fivers.txt',encoding="utf-8") as f:
    wordlist=f.readlines()
    word=random.choice(wordlist)
print(word)
tries = 5
while tries > 0:
    print(str(tries)+' tries left')
    wrd=input('enter your word\n')

    #Checking word validity
    if len(wrd)!=5:
        print('Your word must be 5 letters')
    elif wrd+'\n' not in wordlist:
        print('Your word must be from dictionary')
    else:
        tries-=1
        res=''
        for pos in range (0,5):
            if wrd[pos]==word[pos]:
                res+='b'
            elif wrd[pos] in word:
                res+='c'
            else:
                res+='_'
        print('your try is: '+res)
        if (res == 'bbbbb'):
            print('You won!')
            exit(0)
        elif (tries == 0):
            print('Good luck next time')