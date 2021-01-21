import telegram 
from telegram.ext import Updater, CommandHandler, ConversationHandler, CallbackQueryHandler
from telegram import ChatAction
import os
from bs4 import BeautifulSoup as soup

TOKEN = os.getenv("TOKEN")
VAR = 0
























def start(update, context):
	name = update.effective_user['first_name']
	update.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
	update.message.chat.send_message("dfghj")
	
def creditos_htlm():
	res = open("creditos-c2-cas-finales-pero-faltaban-detalles/creditos-MN-C2-hasta-2019-12-16.html")
	s = soup(res.read(), 'html.parser').table
	listado = []
	h = [[i.text for i in b.find_all('td')] for b in s.find_all('tr')]
	for item in h:
		s = ""
		for i in item:
			s += i.replace('\n', '')
		listado.append(s)
	return listado

def creditos(update, context):
	listado = creditos_htlm()
	print("aaaaaaaaaaaaa")
	print(listado)
	listado_botones = [telegram.InlineKeyboardButton(listado[i], callback_data = str(i)) for i in range(len(listado))]
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
	update.message.chat.send_message("Listado de creditos", parse_mode = 'Markdown', reply_markup = reply_markup)
	return VAR

def build_menu (buttons, n_cols, header_buttons = None, footer_buttons = None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
	#if header_buttons:
	#	menu.insert(0, header_buttons)
    
    #if footer_buttons:
    #	menu.append(footer_buttons)
    return menu

def creditos_del_usuario (update, context):
	pass

def main():
	my_bot = telegram.Bot(token = TOKEN)
	update = Updater(my_bot.token) 
	dp = update.dispatcher
	dp.add_handler(CommandHandler('start', start))
	dp.add_handler(ConversationHandler(
		entry_points = [CommandHandler('creditos', creditos)], 
		states = {
			VAR : [CallbackQueryHandler(creditos_del_usuario)]
		}, 
		fallbacks = []))
	update.start_polling()
	update.idle()



main()
