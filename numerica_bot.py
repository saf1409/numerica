import telegram 
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
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
	update.message.chat.send_message("Hola " + name + ", es una herramienta hecha especialmente para la asignatura Matematica Numerica, esperamos que les sea util.")
	
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

def creditos_del_usuario(update, context):
	query = update.callback_query
	name1 = query.data
	name1 = name1.split(" ")
	name = ""
	for index in range(2, len(name1) - 7):
		name += name1[index] + " " 
	name += name1[len(name1) - 7]
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

def modo_de_juego(update, context):
	query = update.callback_query
	button = query.data
	if button == 1:
		query.bot.send_message(chat_id = query.message.chat_id, text= message, parse_mode = telegram.ParseMode.HTML)


def main():
	bot = telegram.Bot(token = '1583703417:AAHJesGQmy8AvnuR-d-9u12jNOSRd6PNQrs')
	update = Updater(bot.token, use_context=True) 
	dp = update.dispatcher
	dp.add_handler(CommandHandler('start', start))
	dp.add_handler(CommandHandler('creditos', creditos))
	dp.add_handler(CallbackQueryHandler(creditos_del_usuario))
	dp.add_handler(CommandHandler('concurso', concurso))
	dp.add_handler(CallbackQueryHandler(modo_de_juego))
	run(update)

main()