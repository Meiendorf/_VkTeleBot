import time
from vktelebot import start_bot

while True:
	try:
		start_bot()
	except:
		time.sleep(60)
		
#bot.send_meme()
#{'name':"/2d/ch", 'id':'-100892059', 'domain':"2d_ch", 'chat_id':'-1001102597680', 'count':5, 'offset':1}
#{'name':"Desuchan", 'id':'-132364112', 'domain':"desu4an", 'chat_id':'-1001102597680', 'count':5, 'offset':1}