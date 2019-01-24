#!/usr/bin/env python
# coding: utf-8

# In[99]:


import requests
from time import sleep
import datetime


search = "http://1001mem.ru/search?q="


def send_img(chat_id, link, url):
    if link == -1:
        send_mess(chat_id, 'Error 404')
    else:
        try:
            res = requests.get(link)
            requests.post(url=url + 'sendPhoto', data={'chat_id': chat_id, 'photo': link})
        except:
            send_mess(chat_id, 'Error 404')
                                                     

def search_gen(text):
    if len(text) > 7 and text[0:7] == ':search':
        t = text.split()
        if len(t) >= 3:
            return text[8 + len(t[1]) + 1:], t[1]
        else:
            return text[8:], None
    else:
        search="http://1001mem.ru/search?q="
        text_list = text.split()
        for i in text_list:
            search = search + '+' + i
        return search, None
            

def src_search(text):
    x = text.find('<img src=')
    if x == -1:
        return -1
    else:
        while text[x] != '"': x += 1
        x += 1
        while text[x] == '/': x += 1
        link = ''
        while text[x] != '"': 
            link += text[x]
            x += 1
        return link, x
        
        
def search_img(text):
    search, form = search_gen(text)
    try:
        response = requests.get(search)
        link, x = src_search(response.text)
        y = x
        if form is None:
            while link != -1 and link[:4] != 'http':
                y += x
                link, x= src_search(response.text[y:])
        else:
            while link != -1 and (link[-len(form):] != form or link[:4] != 'http'):
                y += x
                link, x= src_search(response.text[y:])
    except:
        return -1
    return link


def get_updates_json(request, offset):  
    params = {'timeout': 100, 'offset': offset}
    try:
        response = requests.get(request + 'getUpdates', data=params)
        return response.json()
    except:
        return None


def last_update(data):  
    if data is None:
        return -1
    results = data['result']
    total_updates = len(results) - 1
    return results[total_updates]


def get_update(data, update_id, last):  
    results = data['result']
    return results[- last + update_id -1]


def get_chat_id(update):  
    chat_id = update['message']['chat']['id']
    return chat_id

def send_mess(chat, text):
    params = {'chat_id': chat, 'text': text}
    while True:
        try:
            response = requests.post(url + 'sendMessage', data=params)
            return response
        except:
            sleep(1)

def extract_mess(update):
    text = update['message']['text']
    return text

def main():
    hello = 'Здравствуйте!\nЯ бот который будет искать за вас мемы: просто напишите ваш поисковой запрос и я вам вышлю мем на эту тему\nОтправьте сообщение :everyday, чтобы я автоматически здоровался с вами каждый день, и меня всегда будет легко найти\nЧтобы я больше вам так не спамил, наберите :stop\nЕсли у вас есть какие-либо пожелания или жалобы, можете их написать после :wish и тогда мои разработчики обязательно вас услышат(особенно будем рады конструктивным предложениям по улучшению поиска мемов)\nЕсли хотите еще раз увидеть это сообщение просто напишите мне "Привет"\nТакже есть функция :search [image format] url, которая будет искать первую картинку в таком формате по указанной ссылке. Пример использования: :search jpg http://kotomatrix.ru/search.php?q=%D0%BC%D0%BE%D0%B7%D0%B3. Если формат указан не будет, то будет найдена просто первая картинка на этой странице.'
    new_offset = None
    iterat = 0
    user_id = #put your chat_id
    now = datetime.datetime.now()
    day = now.day
    right_hour = 12
    url, new_offset, day1 = map(int, open('serv.txt').read().split())
    if day1 == day:
        day += 1
    chat_id_list = list(map(int, open('chat_id_list.txt').read().split()))
    everyday_list = list(map(int, open('everyday_list.txt').read().split()))
    lol = 0
    first = 1
    update_id = last_update(get_updates_json(url, new_offset))['update_id']
    while lol  == 0:
        last = last_update(get_updates_json(url, new_offset))['update_id']
        if last == -1:
            continue
        if first == 1 and last != update_id:
            first = 0
            update_id += 1
        while update_id <= last and first == 0:
            update = get_update(get_updates_json(url, new_offset), update_id, last)
            text = extract_mess(update)
            chat_id = get_chat_id(update)
            print(text.lower())
            if chat_id == user_id and text.lower() == 'stop':
                lol = 1
                f = open('serv.txt', 'w')
                print(new_offset, day-1, sep=' ', file=f)
                f.close()
            elif chat_id not in chat_id_list:
                send_mess(chat_id, hello)
                chat_id_list.append(chat_id)
                f = open('chat_id_list.txt', 'a')
                print(chat_id, end=' ', file=f)
                f.close()
            elif text.lower() == 'привет':
                send_mess(chat_id, hello)
            elif text == ':everyday':
                if chat_id not in chat_id_list:
                    everyday_list.append(chat_id)
                    f = open('everyday_list.txt', 'a')
                    print(chat_id, end=' ', file=f)
                    f.close()
            elif text == ':stop':
                f = open('everyday_list.txt', 'w')
                m = len(everyday_list)
                i = 0
                while i < m:
                    if everyday_list[i] == chat_id:
                        everyday_list.pop(i)
                        m -= 1
                    else:
                        print(chat_id, end=' ', file=f)
                        i += 1
                f.close()
            elif len(text) > 5 and text[:5] == ':wish':
                send_mess(user_id, text[5:])
            else:
                link = search_img(text)
                send_img(chat_id, link, url)
            update_id += 1
        new_offset = update_id - 2
        iterat += 1
        if iterat%10 == 0:
            now = datetime.datetime.now()
            if now.hour > right_hour and day == now.day:
                for id in everyday_list:
                    send_mess(id, 'Hola!')
                day+=1
        sleep(1)       

if __name__ == '__main__':  
    main()









