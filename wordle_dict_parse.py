import re
dir='C:\\Users\\ekaterina.morozova\\Desktop\\wordle'
eng_5words=[]
rus_5words=[]
with open(dir+'\\words.txt',encoding="utf-8") as eng:
    line = eng.readline()
    while line:
        x=re.findall('^[a-z]{5}$', line)
        if (x):
            eng_5words.append(x[0])
        line = eng.readline()

with open(dir + '\\russian.txt',encoding="utf-8") as rus:
    line = rus.readline()
    while line:
        x = re.findall('^[а-я]{5}$', line)
        if (x):
            rus_5words.append(x[0])
        line = rus.readline()



with open(dir+'\\eng_fivers.txt', 'a') as out:
    for i in eng_5words:
        out.write(i + '\n')

with open(dir+'\\rus_fivers.txt', 'a') as out:
    for i in rus_5words:
        out.write(i + '\n')