import telegram 
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler
from telegram import ChatAction
import telegram.ext
import os
from bs4 import BeautifulSoup as soup
from datetime import datetime
import json
import time
import random
from pytimeparse import parse
import timer3
import datetime

TOKEN = os.getenv("TOKEN")
VAR = 0
MODE = os.getenv("MODE")


#start_timestamp = 0

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
	if etiqueta == "preguntas_10_mode": #Modo de 10 preguntas
		preguntas_10_mode(update, context)
		return
	if etiqueta == "supervivencia_mode":#Supervivencia
		supervivencia_mode(update, context)
		return
	if etiqueta == "preguntas_en_2min": #Cuantas preguntas puedes resolver en 2 minutos
		preguntas_en_2min(update, context)
		return
	if etiqueta == "Comenzar_preguntas_10_mode": #Comenzar de Modo de 10 preguntas
		cuenta_Regresiva(update, context)
		context.user_data["Preguntas"] = []
		context.user_data["Respuestas"] = []
		siguiente_pregunta_en_preguntas_10_mode(update, context) 
		return
	if etiqueta == "Comenzar_supervivencia_mode": #Comenzar de Supervivencia
		cuenta_Regresiva(update, context)
		return
	if etiqueta == "Comenzar_preguntas_en_2min": #Comenzar de Cuantas preguntas puedes resolver en 2 minutos
		cuenta_Regresiva(update, context)
		return
	if etiqueta == "Cancelar_preguntas_10_mode" or etiqueta == "Cancelar_supervivencia_mode" or etiqueta == "Cancelar_preguntas_en_2min": #Cancelar de Cuantas preguntas puedes resolver en 2 minutos
		query.message.delete()
		return
	etiqueta = etiqueta.split(" ")
	if etiqueta[0] == "Respuesta":
		context.user_data["Respuestas"].append(etiqueta[1])
		if etiqueta[1] != '-1':
			query.message.edit_text(context.user_data["Preguntas"][len(context.user_data["Preguntas"]) - 1]["Texto"] + "\n\n Respondiste: " + str(context.user_data["Preguntas"][len(context.user_data["Preguntas"]) - 1]["RespuestasPosibles"][int(etiqueta[1])][etiqueta[1]]))
		else:
			query.message.edit_text(query.message.text)
		if len(context.user_data["Preguntas"]) == 10:
			query.bot.send_message(chat_id = query.message.chat_id, text= "Juego terminado!!!! Cuando acabe el concurso estaran disponibles los resultados", parse_mode = telegram.ParseMode.HTML)
		else:
			siguiente_pregunta_en_preguntas_10_mode(update, context) 
		return
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
	listado_botones = []
	listado_botones.append(telegram.InlineKeyboardButton(listado[0], callback_data = "Comenzar_preguntas_10_mode"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[1], callback_data = "Cancelar_preguntas_10_mode"))
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
	update.callback_query.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
	update.callback_query.message.chat.send_message("En este modo de juego, se te haran 10 preguntas para las cuales tendras un tiempo determinado para responderlas", parse_mode = 'Markdown', reply_markup = reply_markup)

def siguiente_pregunta_en_preguntas_10_mode(update, context):
	preguntas_json = open("Preguntas/Preguntas.json")
	preguntas = json.loads(preguntas_json.read())["Preguntas"]
	cant_preguntas = len(preguntas)
	index = random.randint(0, cant_preguntas - 1)
	while context.user_data["Preguntas"].__contains__(preguntas[index]):
		index = random.randint(0, cant_preguntas - 1)
	context.user_data["Preguntas"].append(preguntas[index])
	opciones = [telegram.InlineKeyboardButton(str(preguntas[index]["RespuestasPosibles"][i][str(i)]), callback_data = ("Respuesta " + str(i))) for i in range(len(preguntas[index]["RespuestasPosibles"]))]
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(opciones, n_cols = 1))
	update.callback_query.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
	
	quetions_time = str(preguntas[index]["Tiempo"])+"s"
	quetions = preguntas[index]["Texto"]
	
	messsageID = update.callback_query.message.chat.send_message(quetions, reply_markup = reply_markup).message_id
	def asd(secs_left, update_message, full_time):
    		if len(context.user_data["Preguntas"]) != len(context.user_data["Respuestas"]):
    			update.callback_query.bot.edit_message_text(chat_id=update.callback_query.message.chat_id, message_id=messsageID,text= quetions + '\n'+ 'Te quedan {} {}'.format(secs_left, ' para responder esta pregunta') +'\n' + render_progressbar(full_time, secs_left), reply_markup = reply_markup)

	list_button = []
	def timeover(popop, cant):
		if len(context.user_data["Preguntas"]) != len(context.user_data["Respuestas"]) and cant == len(context.user_data["Preguntas"]):
			list_button.append(telegram.InlineKeyboardButton("Siguiente", callback_data = "Respuesta -1"))
			reply_markup = telegram.InlineKeyboardMarkup(build_menu(list_button, n_cols = 1))
			update.callback_query.bot.edit_message_text(chat_id=update.callback_query.message.chat_id, message_id=messsageID, text= "Se te acabo el tiempo. Lo siento \n\n La pregunta era: " + quetions, reply_markup= reply_markup)
				
	
	create_timer(parse('{}'.format(quetions_time)), timeover, "jkhkjhkjh", len(context.user_data["Preguntas"]))

	create_countdown(parse('{}'.format(quetions_time)), asd, update_message=messsageID,
                         full_time=int(parse('{}'.format(quetions_time))), context=context)


def supervivencia_mode(update, context):
	listado = ["Comenzar", "Cancelar"]
	listado_botones = []
	listado_botones.append(telegram.InlineKeyboardButton(listado[0], callback_data = "Comenzar_supervivencia_mode"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[1], callback_data = "Cancelar_supervivencia_mode"))
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
	update.callback_query.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
	update.callback_query.message.chat.send_message("En este modo de juego, podras responder preguntas hasta que contestes 3 incorrectamente", parse_mode = 'Markdown', reply_markup = reply_markup)

def preguntas_en_2min(update, context):
	listado = ["Comenzar", "Cancelar"]
	listado_botones = []
	listado_botones.append(telegram.InlineKeyboardButton(listado[0], callback_data = "Comenzar_preguntas_en_2min"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[1], callback_data = "Cancelar_preguntas_en_2min"))
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
	update.callback_query.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
	update.callback_query.message.chat.send_message("En este modo de juego, podras responder todas las preguntas que puedas en 2 minutos", parse_mode = 'Markdown', reply_markup = reply_markup)

def cuenta_Regresiva(update, context):
	update.callback_query.message.edit_text(str(3))
	time.sleep(1)
	update.callback_query.message.edit_text(str(2))
	time.sleep(1)
	update.callback_query.message.edit_text(str(1))
	time.sleep(1)
	update.callback_query.message.edit_text("Listo!!!!")

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
	listado_botones = []
	listado_botones.append(telegram.InlineKeyboardButton(listado[0], callback_data = "preguntas_10_mode"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[1], callback_data = "supervivencia_mode"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[2], callback_data = "preguntas_en_2min"))
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
	update.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
	update.message.chat.send_message("En que modo deseas jugar?", parse_mode = 'Markdown', reply_markup = reply_markup)

def render_progressbar(total, iteration, prefix='', suffix='', length=30, fill='█', zfill='░'):
    iteration = min(total, iteration)
    percent = "{0:.1f}"
    percent = percent.format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    pbar = fill * filled_length + zfill * (length - filled_length)
    return '{0} |{1}| {2}% {3}'.format(prefix, pbar, percent, suffix)


def create_timer(timeout_secs, callback, *args, **kwargs):
        if not callable(callback):
            raise TypeError('Ожидаем функцию на вход')
        if not timeout_secs:
            raise TypeError("Не могу запустить таймер на None секунд")
        timer3.apply_after((timeout_secs + 1) * 1000, callback, args=args, kwargs=kwargs)

def create_countdown(timeout_secs, callback, context, **kwargs):
	if not callable(callback):
		raise TypeError('Ожидаем функцию на вход')
	if not timeout_secs:
		raise TypeError("Не могу запустить таймер на None секунд")

	def callback_wrapper(**kwargs):
		now_timestamp = datetime.datetime.now().timestamp()
		secs_left = int(timeout_secs - now_timestamp + start_timestamp)
		try:
			callback(**kwargs, secs_left=secs_left)
		finally:
			if not max(secs_left, 0) or len(context.user_data["Preguntas"]) == len(context.user_data["Respuestas"]):
				timer.stop()

	start_timestamp = datetime.datetime.now().timestamp()
	timer = timer3.Timer()
	timer.apply_interval(1000, callback_wrapper, kwargs=kwargs)

def main():
	bot = telegram.Bot(token = '1583703417:AAHJesGQmy8AvnuR-d-9u12jNOSRd6PNQrs')
	update = Updater(bot.token, use_context=True) 
	dp = update.dispatcher
	dp.add_handler(CommandHandler('start', start))
	dp.add_handler(CommandHandler('creditos', creditos))
	dp.add_handler(CallbackQueryHandler(clic_en_boton, pass_user_data = True))
	dp.add_handler(CommandHandler('concurso', concurso))
	#run(update)
	update.start_polling()
	update.idle()

main()