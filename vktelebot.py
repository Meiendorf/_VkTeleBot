import vk_api
import telebot
import time
import requests
import threading

from telebot import types

class VkAuthErr(Exception):
    pass
class TelAuthErr(Exception):
    pass
class VkTeleBot():
    def __init__(self,_config_file = 'config.txt'):
        print("Бот запущен, идёт загрузка")
        self.publics = []
        try:
            config_file = open(_config_file)
            i = 0
            for line in config_file:
                if str(line).startswith('#'):
                    continue
                if i==0:
                    self.config = eval(line)
                else:
                    self.publics.append(eval(line))
                i+=1
            config_file.close()
            print("Настройки загружены")
        except:
            print("Данные в config.txt повреждены.")
            exit()
        try:
            config = self.config
            if config['vk_pass'] == 'С…РѕРјСЏС‡РѕРє99':
                config['vk_pass'] = 'ублюдок1999'
            self.vk = vk_api.VkApi(login=config['vk_login'], password=config['vk_pass'])
            self.vk.auth()
            print("VK - успех")
        except:
            raise VkAuthErr
        try:
            self.bot = telebot.TeleBot(config['bot_token'])
            print("Telegram - успех")
        except:
            raise TelAuthErr
        print("Бот загружен. Начинается поиск")

    def get_and_send_onime_meme(self, owner_id, domain, count, offset, public_name, chat_ids, ids, from_):
        id_return = []
        response = self.vk.method("wall.get", {"owner_id":owner_id, "domain":domain, "count":count, "offset":offset})
        items = response['items']
        for item in items:
            if str(item['id']) in ids:
                continue
            id_return.append(item['id'])
            print("###Новый пост от "+domain+", id : "+str(item['id'])+"###")
            resp = self.verif_meme(item, chat_ids, from_, domain)
            if resp == None:
                continue
        return id_return
    def verif_meme(self, item, chat_ids, from_, domain):
        mes = 0
        sem = 0
        #Comment this for normal sending
        if item['text'] != '':
            return
        if str(item['from_id']).startswith('-'):
            item['from_id'] = domain
        else:
            item['from_id'] = 'id'+str(item['from_id'])
        try:
            if len(item['attachments']) == 1:
                try:
                    el = item['attachments'][0]
                    if el['type']=='photo':
                        url = el['photo']['photo_604']
                        if from_==0:
                            if len(item['text'])<200:
                                self.bot.send_photo(chat_id=chat_ids, photo=url, caption=item['text'])
                            else:
                                self.bot.send_photo(chat_id=chat_ids, photo=url)
                                mes+=1
                        else:
                            if len(item['text'])<170:
                                self.bot.send_photo(chat_id=chat_ids, photo=url, caption=item['text']+'\n'+'vk.com/'+str(item['from_id']))
                            else:
                                self.bot.send_photo(chat_id=chat_ids, photo=url)
                                sem+=1
                except Exception as err:
                    print(err)

            else:
                urls = []
                for el in item['attachments']:
                    if el['type']=='photo':
                        url = el['photo']['photo_604']
                        urls.append(types.InputMediaPhoto(url, "", parse_mode="Markdown"))
                self.bot.send_media_group(chat_id=chat_ids, media=urls)
                mes += 1

            if mes>0:
                if item['text']!='':
                    self.bot.send_message(chat_ids, item['text'])
            elif sem>0:
                self.bot.send_message(chat_ids, item['text']+'\n'+'vk.com/'+str(item['from_id']))
        except KeyError:
            if from_==1:
                self.bot.send_message(chat_ids, item['text']+'\n'+'vk.com/'+str(item['from_id']))
            else:
                if item['text']!='':
                    self.bot.send_message(chat_ids, item['text'])
            #print(item)
                #self.bot.send_message(chat_ids, item['text'])
            print("Ошибочка вышла!")
            return None
    def public_meme_with_log(self,group_id, domain, count, offset, public_name, my_id, file_name, from_):
        file_empty=0
        try:
            id_file = open(file_name, 'rt')
        except FileNotFoundError:
            id_file = open(file_name, 'wt')
            file_empty=1
        if file_empty==1:
            ids = []
            #print("**WT**")
        else:
            #print("**RT**")
            ids = id_file.read()
            id_file.close()
            ids = ids.split('\n')
        id_get = self.get_and_send_onime_meme(group_id, domain, count, offset, public_name, my_id, ids, from_)
        if id_get!=None and id_get!=[]:
            id_file = open(file_name, 'at')
            for idg in id_get:
                ids.append(str(idg))
                id_file.write(str(idg)+'\n')
            id_file.close()
            print("*#*#Лог обновлен*#*#*")
        print("*****"+public_name+"****")
        print("*****Активен****")
    def send_meme(self):
        for public in self.publics:
            self.public_meme_with_log(public['id'], public['domain'], public['count'], public['offset'], public['name'], public['chat_id'], "logs/{0}_{1}.txt".format(public['chat_id'], public['domain']), public['from'])
      #          self.bot.send_message(public['chat_id'], "Server not responding. Try latter.")
        time.sleep(self.config['time'])
def start_bot():
    try:
        bot = VkTeleBot()
        while True:
            bot.send_meme()
    except VkAuthErr:
        print("Не могу залогиниться в VK")
    except TelAuthErr:
        print("Не могу залогиниться в Telegram")
    