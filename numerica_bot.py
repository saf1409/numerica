import telegram 
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler
from telegram import ChatAction
import telegram.ext
import os
from bs4 import BeautifulSoup as soup
from datetime import datetime

TOKEN = os.getenv("TOKEN")
VAR = 0
MODE = os.getenv("MODE")
if MODE == "dev":
	def run(update):
		update.start_polling()
		update.idle()
elif MODE == "prod":
	def run(updater):
		PORT = int(os.environ.get("PORT", "8443"))
		HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
		updater.start_webhook(listen = "0.0.0.0", port = PORT, url_path = TOKEN)
		updater.bot.set_webhook(f"https://{HEROKU_APP_NAME}.herokuapp.com/{TOKEN}")


def start(update, context):
	name = update.effective_user['first_name']
	update.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
	update.message.chat.send_message("Hola " + name + ", esta es una herramienta hecha especialmente para la asignatura Matematica Numerica, esperamos que le sea util.")
	
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
	listado_botones = [telegram.InlineKeyboardButton(listado[i], callback_data = (listado[i])) for i in range(len(listado))]
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
	update.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
	update.message.chat.send_message("Listado de creditos", parse_mode = 'Markdown', reply_markup = reply_markup)

def build_menu (buttons, n_cols, header_buttons = None, footer_buttons = None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    return menu

def clic_en_boton(update, context):
	query = update.callback_query
	etiqueta = query.data
	if etiqueta == "0": #Modo de 10 preguntas
		preguntas_10_mode(update, context)
		return
	if etiqueta == "1":#Supervivencia
		supervivencia_mode(update, context)
		return
	if etiqueta == "2": #Cuantas preguntas puedes resolver en 2 minutos
		preguntas_en_2min(update, context)
		return
	if etiqueta == "3": #Comenzar de Modo de 10 preguntas
	    #preguntas_10_start(update, context, count)
		return
	if etiqueta == "4": #Cancelar de Modo de 10 preguntas
		return
	if etiqueta == "5": #Comenzar de Supervivencia
		return
	if etiqueta == "6": #Cancelar de Supervivencia
		return
	if etiqueta == "7": #Comenzar de Cuantas preguntas puedes resolver en 2 minutos
		return
	if etiqueta == "8": #Cancelar de Cuantas preguntas puedes resolver en 2 minutos
		return

	etiqueta = etiqueta.split(" ")
	name = ""
	for index in range(2, len(etiqueta) - 7):
		name += etiqueta[index] + " " 
	name += etiqueta[len(etiqueta) - 7]
	res = open("creditos-c2-cas-finales-pero-faltaban-detalles/detalles-de-los-creditos-MN-C2-hasta-2019-12-16/" + name + ".html")
	texto = soup(res.read(), 'html.parser').get_text()
	texto = texto.split("\n")
	message = ""
	isFecha = False
	index = 0
	while index < len(texto):
		if texto[index].isspace() or len(texto[index]) == 0:
			index += 1
			continue
		elif not isFecha:
			if isDate(texto[index][0:len(texto[index]) - 2]):
				if len(str("\n"  + texto[index] + "\n")) + len(message) > 4096:
					query.bot.send_message(chat_id = query.message.chat_id, text= message, parse_mode = telegram.ParseMode.HTML)
					message = ""
				message+= "\n" +  texto[index] + "\n"
				isFecha = True
			else:
				if len(str(texto[index] + "\n"))> 4096:
					query.bot.send_message(chat_id = query.message.chat_id, text= message, parse_mode = telegram.ParseMode.HTML)
					message = ""
				message+= texto[index] + "\n"
		elif isDate(texto[index][0:len(texto[index]) - 2]):
			if len(str(texto[index] + "\n")) + len(message) > 4096:
				query.bot.send_message(chat_id = query.message.chat_id, text= message, parse_mode = telegram.ParseMode.HTML)
				message = ""
			message+= texto[index] + "\n"
		else:
			if len(str(texto[index] + " " + texto[index + 2] + "\n\n")) + len(message) > 4096:
				query.bot.send_message(chat_id = query.message.chat_id, text= message, parse_mode = telegram.ParseMode.HTML)
				message = ""
			message+=  texto[index] + " " + texto[index + 2] + "\n\n"
			index +=2
		index +=1
	query.bot.send_message(chat_id = query.message.chat_id, text= message, parse_mode = telegram.ParseMode.HTML)

def isDate(date):
	try:
		datetime.strptime(date, '%Y-%m-%d')
		return True
	except ValueError:
		return False

def preguntas_10_mode(update, context):
	listado = ["Comenzar", "Cancelar"]
	listado_botones = [telegram.InlineKeyboardButton(listado[i], callback_data = (str(i+3))) for i in range(len(listado))]
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
	update.callback_query.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
	update.callback_query.message.chat.send_message("En este modo de juego, se te haran 10 preguntas para las cuales tendras un tiempo determinado para responderlas", parse_mode = 'Markdown', reply_markup = reply_markup)

def supervivencia_mode(update, context):
	listado = ["Comenzar", "Cancelar"]
	listado_botones = [telegram.InlineKeyboardButton(listado[i], callback_data = (str(i+5))) for i in range(len(listado))]
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
	update.callback_query.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
	update.callback_query.message.chat.send_message("En este modo de juego, podras responder preguntas hasta que contestes 3 incorrectamente", parse_mode = 'Markdown', reply_markup = reply_markup)

def preguntas_en_2min(update, context):
	listado = ["Comenzar", "Cancelar"]
	listado_botones = [telegram.InlineKeyboardButton(listado[i], callback_data = (str(i+7))) for i in range(len(listado))]
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
	update.callback_query.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
	update.callback_query.message.chat.send_message("En este modo de juego, podras responder todas las preguntas que puedas en 2 minutos", parse_mode = 'Markdown', reply_markup = reply_markup)

#def preguntas_10_start(update, context, count):


def creditos_del_usuario_htlm(name):
	res = open("creditos-c2-cas-finales-pero-faltaban-detalles/detalles-de-los-creditos-MN-C2-hasta-2019-12-16/" + name + ".html")
	Contenido_htlm = res.read()
	return quitarEtiquetas(Contenido_htlm)

def quitarEtiquetas (Contenido_htlm):
	Contenido_htlm = str(Contenido_htlm)
	lugarInicio = Contenido_htlm.find("<body>")
	lugarFin = Contenido_htlm.find("</body>")
	Contenido_htlm = Contenido_htlm[lugarInicio : lugarFin]
	adentro = 0
	texto = ''
	for caract in Contenido_htlm:
		if caract == '<':
			adentro = 1
		elif adentro == 1 and caract == '>':
			adentro = 0
		elif adentro == 1:
			continue
		else:
			texto += caract
	return texto	

def concurso(update, context):
	listado = ["10 preguntas", "Supervivencia", "Cuantas preguntas puedes resolver en 2 minutos"]
	listado_botones = [telegram.InlineKeyboardButton(listado[i], callback_data = (str(i))) for i in range(len(listado))]
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
	update.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
	update.message.chat.send_message("En que modo deseas jugar?", parse_mode = 'Markdown', reply_markup = reply_markup)


def main():
	bot = telegram.Bot(token = '1583703417:AAHJesGQmy8AvnuR-d-9u12jNOSRd6PNQrs')
	update = Updater(bot.token, use_context=True) 
	dp = update.dispatcher
	dp.add_handler(CommandHandler('start', start))
	dp.add_handler(CommandHandler('creditos', creditos))
	dp.add_handler(CallbackQueryHandler(clic_en_boton))
	dp.add_handler(CommandHandler('concurso', concurso))
	run(update)
	#update.start_polling()
	#update.idle()

main()
