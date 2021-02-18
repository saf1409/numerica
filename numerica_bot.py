import telegram 
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
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
import emoji
import sqlite3
import threading

TOKEN = os.getenv("TOKEN")
MODE = os.getenv("MODE")

CONCURSO, JUGAR, SELECT_MODE_GAME, START_MODE_GAME, ANSWER, RANKING, CANCEL, NAME, SELECT_TIME, RANKING, CREDITOS, LISTADO, ADDCONCURSO, ADDADMINISTRADOR, RECLAMACION, RECLAMACIONADMINISTRADOR, BORRARRECLAMACIONES, PREMIOS, DETALLES_FIN_CONCURSO, DETALLES_POR_MODOS, DETALLES_POR_PREGUNTAS, DETALLESCREDITOS, RECLAMACION_CALLBACKQUERY = range(23)

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

def help(update, context):
	adm = False
	if not update.effective_user['id'] == 937372768 and not update.effective_user['id'] == 716780131 and not update.effective_user['id'] == 823911446:
		conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
		cursor = conexion.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS `Administrador` " \
			"(`ID_User` integer PRIMARY KEY NOT NULL)")
		cursor.execute("SELECT ID_User FROM Administrador")
		Users = cursor.fetchall()
		for item in Users:
			if item[0] == update._effective_chat.id:
				adm = True
				break
	else:
		adm = True

	if adm:
		update.message.chat.send_message("Hola eres administrador de este bot, por tanto ademas de los comandos visibles, tienes autorizacion para acceder a los siguientes comandos:\n /addconcurso\n /addadministrador \n /reclamaciones \n /premios")	
	else:
		update.message.chat.send_message("No eres administrador 😒 por tanto solo puedes ver y usar los comandos visibles 😅. Lamentamos los inconvenientes ocasionados 😢")	

	return ConversationHandler.END

def start(update, context):
	name = update.effective_user['first_name']
	update.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
	update.message.chat.send_message("Hola " + name + ", esta es una herramienta hecha especialmente para la asignatura Matematica Numerica, esperamos que le sea util.")
	conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
	cursor = conexion.cursor()
	cursor.execute("CREATE TABLE IF NOT EXISTS `Usuario` " \
		"(`ID_User` integer PRIMARY KEY NOT NULL, `Nombre_User` VARCHAR(50) NOT NULL)")
	cursor.execute("SELECT ID_User FROM Usuario WHERE ID_User = {0}".format(update.effective_user['id']))
	Users = cursor.fetchall()
	registrado = False
	for item in Users:
		registrado = True
		break

	if not registrado:
		update.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
		update.message.chat.send_message("Introduce tu nombre completo")
		return NAME
	else:
		return ConversationHandler.END

def name(update, context): 
	nombre = update.message.text
	conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
	cursor = conexion.cursor()
	cursor.execute("INSERT INTO `Usuario` (`ID_User`,`Nombre_User`) Values"\
			"('{0}', '{1}')".format(update.effective_user['id'], nombre))
	conexion.commit()
	conexion.close()
	update.message.chat.send_message("Gracias. Ya puedes usar los comandos que tiene el bot")
	return ConversationHandler.END

def add_concurso(update, context):
	if not update.effective_user['id'] == 937372768 and not update.effective_user['id'] == 716780131 and not update.effective_user['id'] == 823911446:
		conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
		cursor = conexion.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS `Administrador` " \
			"(`ID_User` integer PRIMARY KEY NOT NULL)")
		cursor.execute("SELECT ID_User FROM Administrador")
		Users = cursor.fetchall()
		registrado = False
		for item in Users:
			registrado = True
			break

		if not registrado:
			update.message.chat.send_message("Usted no tiene permiso para anadir concursos")
			return ConversationHandler.END
		
	update.message.chat.send_message("Por favor, envie la configuracion del nuevo concurso. Ejemplo: \n *Add_Concurso* \n FechaDeInicio=2021-2-3 \n HoraDeInicio=23:05\nFechaDeFin=2021-2-5\nHoraDeFin=18:10\nPagoPorJugar=10preguntas=300\nSupervivencia=500\nCuantoEnXminutos=1=1000\n2=1500\n5=2000\nPremioPorCadaPregunta=500\nPremioParaElGanadorEnCadaModo=10preguntas=2100\nSupervivencia=3147\nCuantoEnXminutos=1=1423\n2=5768\n5=6277\nPremioParaElGanadorEn2Modos= 2452\nPremioParaElGanadorEn3Modos=2969\nPremioParaElGanadorEn4Modos=5245\nPremioParaElGanadorEn5Modos=7567")
	return ADDCONCURSO
	
def add_concurso_callbackQuery(update, context):
	text = update.message.text
	text = text.split("\n")
	data = {}
	data['Configuracion'] = []
	data['Configuracion'].append({
	"FechaDeInicio": text[1].split('=')[1],
	"HoraDeInicio": text[2].split('=')[1],
	"FechaDeFin" : text[3].split('=')[1],
	"HoraDeFin": text[4].split('=')[1],
	"PagoPorJugar": [{"10Preguntas" : int(text[5].split('=')[2])}, {"Supervivencia": int(text[6].split('=')[1])}, {"CuantoEnXminutos" : [{text[7].split('=')[1] : int(text[7].split('=')[2])}, {text[8].split('=')[0]: int(text[8].split('=')[1])}, {text[9].split('=')[0]: int(text[9].split('=')[1])}]}],
	"PremioPorCadaPregunta" : int(text[10].split('=')[1]),
	"PremioParaElGanadorEnCadaModo": [{"10Preguntas" : int(text[11].split('=')[2])}, {"Supervivencia": int(text[12].split('=')[1])}, {"CuantoEnXminutos" : [{text[13].split('=')[1] : int(text[13].split('=')[2])}, {text[14].split('=')[0]: int(text[14].split('=')[1])}, {text[15].split('=')[0]: int(text[15].split('=')[1])}]}],
	"PremioParaElGanadorEn2Modos" : int(text[16].split('=')[1]),
	"PremioParaElGanadorEn3Modos": int(text[17].split('=')[1]),
	"PremioParaElGanadorEn4Modos": int(text[18].split('=')[1]),
	"PremioParaElGanadorEn5Modos": int(text[19].split('=')[1])})

	with open("ConfiguracionDelConcurso.json", 'w') as file:
		json.dump(data, file, indent = 11)

	configuracionDelConcurso_json = open("ConfiguracionDelConcurso.json")
	configuracion = json.loads(configuracionDelConcurso_json.read())["Configuracion"]
	conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
	cursor = conexion.cursor()
	cursor.execute("CREATE TABLE IF NOT EXISTS Concurso " \
			"(ID_Concurso integer  PRIMARY KEY AUTOINCREMENT NOT NULL, Fecha_Inicio datetime NOT NULL, Fecha_Fin datetime NOT NULL, Creditos_Por_Pregunta_Correcta int(11) NOT NULL)")
	
	cursor.execute("INSERT INTO concurso(`Fecha_Inicio`, `Fecha_Fin`,`Creditos_Por_Pregunta_Correcta`) VALUES" \
			"('{0}', '{1}', '{2}')".format(configuracion[0]["FechaDeInicio"] + " " + configuracion[0]["HoraDeInicio"], configuracion[0]["FechaDeFin"] + " " + configuracion[0]["HoraDeFin"], configuracion[0]["PremioPorCadaPregunta"]))

	cursor.execute("CREATE TABLE IF NOT EXISTS `Premio` (ID_Premio integer  PRIMARY KEY AUTOINCREMENT NOT NULL, `ID_Concurso` integer NOT NULL, `Modo_de_Juego` VARCHAR(50) NOT NULL, `Cantidad_Creditos` int(11) NOT NULL)")

	cursor.execute("CREATE TABLE IF NOT EXISTS `Premiado`" \
		"(`ID_P`integer PRIMARY KEY NOT NULL, `ID_Concurso` integer NOT NULL, `ID_User` integer NOT NULL, `Modo_de_Juego`  VARCHAR(50) NOT NULL)")

	cursor.execute("SELECT ID_Concurso FROM concurso ORDER BY ID_Concurso DESC LIMIT 1")
	concurso = cursor.fetchone()

	cursor.execute("INSERT INTO `Premio` (`ID_Concurso`,`Modo_de_Juego`,`Cantidad_Creditos`) VALUES"\
			"('{0}', '{1}', '{2}')".format(concurso[0], '10Preguntas', configuracion[0]["PremioParaElGanadorEnCadaModo"][0]["10Preguntas"]))

	cursor.execute("INSERT INTO `Premio` (`ID_Concurso`,`Modo_de_Juego`,`Cantidad_Creditos`) VALUES"\
			"('{0}', '{1}', '{2}')".format(concurso[0], 'Supervivencia', configuracion[0]["PremioParaElGanadorEnCadaModo"][1]["Supervivencia"]))

	cursor.execute("INSERT INTO `Premio` (`ID_Concurso`,`Modo_de_Juego`,`Cantidad_Creditos`) VALUES"\
			"('{0}', '{1}', '{2}')".format(concurso[0], 'preguntas_en_1min', configuracion[0]["PremioParaElGanadorEnCadaModo"][2]["CuantoEnXminutos"][0]["1"]))

	cursor.execute("INSERT INTO `Premio` (`ID_Concurso`,`Modo_de_Juego`,`Cantidad_Creditos`) VALUES"\
			"('{0}', '{1}', '{2}')".format(concurso[0], 'preguntas_en_2min', configuracion[0]["PremioParaElGanadorEnCadaModo"][2]["CuantoEnXminutos"][1]["2"]))

	cursor.execute("INSERT INTO `Premio` (`ID_Concurso`,`Modo_de_Juego`,`Cantidad_Creditos`) VALUES"\
			"('{0}', '{1}', '{2}')".format(concurso[0], 'preguntas_en_5min', configuracion[0]["PremioParaElGanadorEnCadaModo"][2]["CuantoEnXminutos"][2]["5"]))

	cursor.execute("CREATE TABLE IF NOT EXISTS `Coincidencia` (ID_Coincidencia integer  PRIMARY KEY AUTOINCREMENT NOT NULL, `ID_Concurso` int(11) NOT NULL,`Cantidad_Coincidencia` int(11) NOT NULL, `Cantidad_Creditos` int(11) NOT NULL)")

	cursor.execute("INSERT INTO `Coincidencia` (`ID_Concurso`,`Cantidad_Coincidencia`,`Cantidad_Creditos`) VALUES" \
			"('{0}', '{1}', '{2}')".format(concurso[0], 2, configuracion[0]["PremioParaElGanadorEn2Modos"]))

	cursor.execute("INSERT INTO `Coincidencia` (`ID_Concurso`,`Cantidad_Coincidencia`,`Cantidad_Creditos`) VALUES" \
			"('{0}', '{1}', '{2}')".format(concurso[0], 3, configuracion[0]["PremioParaElGanadorEn3Modos"]))

	cursor.execute("INSERT INTO `Coincidencia` (`ID_Concurso`,`Cantidad_Coincidencia`,`Cantidad_Creditos`) VALUES" \
			"('{0}', '{1}', '{2}')".format(concurso[0], 4, configuracion[0]["PremioParaElGanadorEn4Modos"]))

	cursor.execute("INSERT INTO `Coincidencia` (`ID_Concurso`,`Cantidad_Coincidencia`,`Cantidad_Creditos`) VALUES" \
			"('{0}', '{1}', '{2}')".format(concurso[0], 5, configuracion[0]["PremioParaElGanadorEn5Modos"]))

	cursor.execute("CREATE TABLE IF NOT EXISTS `Pago` (`ID_Pago` integer  PRIMARY KEY AUTOINCREMENT NOT NULL, `ID_Concurso` integer NOT NULL,`Modo_de_Juego` VARCHAR(50) NOT NULL,`Total` integer NOT NULL)")

	cursor.execute("INSERT INTO `Pago` (`ID_Concurso`,`Modo_de_Juego`,`Total`) VALUES"\
			"('{0}', '{1}', '{2}')".format(concurso[0], '10Preguntas', configuracion[0]["PagoPorJugar"][0]["10Preguntas"]))

	cursor.execute("INSERT INTO `Pago` (`ID_Concurso`,`Modo_de_Juego`,`Total`) VALUES"\
			"('{0}', '{1}', '{2}')".format(concurso[0], 'Supervivencia', configuracion[0]["PagoPorJugar"][1]["Supervivencia"]))

	cursor.execute("INSERT INTO `Pago` (`ID_Concurso`,`Modo_de_Juego`,`Total`) VALUES"\
			"('{0}', '{1}', '{2}')".format(concurso[0], 'preguntas_en_1min', configuracion[0]["PagoPorJugar"][2]["CuantoEnXminutos"][0]["1"]))

	cursor.execute("INSERT INTO `Pago` (`ID_Concurso`,`Modo_de_Juego`,`Total`) VALUES"\
			"('{0}', '{1}', '{2}')".format(concurso[0], 'preguntas_en_2min', configuracion[0]["PagoPorJugar"][2]["CuantoEnXminutos"][1]["2"]))

	cursor.execute("INSERT INTO `Pago` (`ID_Concurso`,`Modo_de_Juego`,`Total`) VALUES"\
			"('{0}', '{1}', '{2}')".format(concurso[0], 'preguntas_en_5min', configuracion[0]["PagoPorJugar"][2]["CuantoEnXminutos"][2]["5"]))

	update.message.chat.send_message("Concurso anadido")

	cursor.execute("SELECT * FROM Usuario")
	Users = cursor.fetchall()
	for item in Users:
		try:
			update.message.chat.bot.send_message(chat_id = item[0], text = "Hola " + item[1].split(" ")[0] + " solo queria hacerte saber que empieza un concurso el dia " + configuracion[0]["FechaDeInicio"] + " a las " + configuracion[0]["HoraDeInicio"] + " hasta el dia " + configuracion[0]["FechaDeFin"] + " a las " + configuracion[0]["HoraDeFin"] + " no pierdas la oportunidad de participar y ganar creditos", parse_mode = telegram.ParseMode.HTML)
		except:
			continue
	
	conexion.commit()
	conexion.close()
	fin = threading.Thread(target = resultados_concurso, args = (update, context))
	fin.start()
	return ConversationHandler.END

def resultados_concurso(update, context):
	configuracionDelConcurso_json = open("ConfiguracionDelConcurso.json")
	configuracion = json.loads(configuracionDelConcurso_json.read())["Configuracion"]
	FechaDeFin = configuracion[0]["FechaDeFin"].split('-')
	HoraDeFin = configuracion[0]["HoraDeFin"].split(':')
	falta = str(datetime.datetime(int(FechaDeFin[0]), int(FechaDeFin[1]), int(FechaDeFin[2]), int(HoraDeFin[0]), int(HoraDeFin[1]), 00, 000000) - datetime.datetime.now())
	falta = falta.split(",")
	tiempo = 0
	masdeundia = False
	if len(falta) > 1 and int(falta[0].split(" ")[0]) > 0:
		masdeundia = True
		tiempo += 86400 * int(falta[0].split(" ")[0])

	if masdeundia: 
		tiempo += int(falta[1].split(":")[0])*3600
		tiempo+= int(falta[1].split(":")[1])*60
	else:
		tiempo += int(falta[0].split(":")[0])*3600
		tiempo+= int(falta[0].split(":")[1])*60

	time.sleep(tiempo)

	conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
	cursor = conexion.cursor()

	cursor.execute("SELECT ID_Concurso FROM concurso ORDER BY ID_Concurso DESC LIMIT 1")
	concurso = cursor.fetchone()[0]

	cursor.execute("CREATE TABLE IF NOT EXISTS `Jugada`" \
		 	"(ID_Jugada integer  PRIMARY KEY AUTOINCREMENT NOT NULL, `ID_Concurso` integer, `ID_User` integer NOT NULL, `Modo_de_Juego`  VARCHAR(50) NOT NULL, `Creditos_Obtenidos` int(11) NOT NULL, `Total_Preguntas` int(11) NOT NULL, `Total_Preguntas_Correctas` int(11) NOT NULL, `Total_Preguntas_Incorrectas` int(11) NOT NULL)")
	
	cursor.execute("CREATE TABLE IF NOT EXISTS `Usuario` " \
			"(`ID_User` integer PRIMARY KEY NOT NULL, `Nombre_User` VARCHAR(50) NOT NULL)")
	
	cursor.execute("SELECT * FROM Premiado")
	a = cursor.fetchall()

	cursor.execute("SELECT  ID_User FROM jugada INNER JOIN usuario USING (ID_User) WHERE ID_Concurso = (SELECT ID_Concurso FROM concurso ORDER BY ID_Concurso DESC LIMIT 1) AND Modo_de_Juego = '{0}' ORDER BY Creditos_Obtenidos DESC LIMIT 1".format("10Preguntas"))
	
	

	ganador_10preguntas = cursor.fetchone()
	if not ganador_10preguntas == None:
 		cursor.execute("INSERT INTO `Premiado` (`ID_Concurso`, `ID_User`, `Modo_de_Juego`) VALUES" \
			"('{0}', '{1}', '{2}')".format(concurso, ganador_10preguntas[0], '10Preguntas'))

	cursor.execute("SELECT * FROM Premiado")
	a = cursor.fetchall()

	
	cursor.execute("SELECT  ID_User FROM jugada INNER JOIN usuario USING (ID_User) WHERE ID_Concurso = (SELECT ID_Concurso FROM concurso ORDER BY ID_Concurso DESC LIMIT 1) AND Modo_de_Juego = '{0}' ORDER BY Creditos_Obtenidos DESC LIMIT 1".format("Supervivencia"))

	ganador_Supervivencia = cursor.fetchone()
	if not ganador_Supervivencia == None:
		cursor.execute("INSERT INTO `Premiado` (`ID_Concurso`, `ID_User`, `Modo_de_Juego`) VALUES" \
			"('{0}', '{1}', '{2}')".format(concurso, ganador_Supervivencia[0], 'Supervivencia'))

	cursor.execute("SELECT * FROM Premiado")
	a = cursor.fetchall()
	cursor.execute("SELECT  ID_User FROM jugada INNER JOIN usuario USING (ID_User) WHERE ID_Concurso = (SELECT ID_Concurso FROM concurso ORDER BY ID_Concurso DESC LIMIT 1) AND Modo_de_Juego = '{0}' ORDER BY Creditos_Obtenidos DESC LIMIT 1".format("preguntas_en_1min"))

	ganador_preguntas_en_1min = cursor.fetchone()
	if not ganador_preguntas_en_1min == None:
		cursor.execute("INSERT INTO `Premiado` (`ID_Concurso`, `ID_User`, `Modo_de_Juego`) VALUES" \
			"('{0}', '{1}', '{2}')".format(concurso, ganador_preguntas_en_1min[0], 'preguntas_en_1min'))

	
	cursor.execute("SELECT  ID_User FROM jugada INNER JOIN usuario USING (ID_User) WHERE ID_Concurso = (SELECT ID_Concurso FROM concurso ORDER BY ID_Concurso DESC LIMIT 1) AND Modo_de_Juego = '{0}' ORDER BY Creditos_Obtenidos DESC LIMIT 1".format("preguntas_en_2min"))

	ganador_preguntas_en_2min = cursor.fetchone()
	if not ganador_preguntas_en_2min == None:
		cursor.execute("INSERT INTO `Premiado` (`ID_Concurso`, `ID_User`, `Modo_de_Juego`) VALUES" \
			"('{0}', '{1}', '{2}')".format(concurso, ganador_preguntas_en_2min[0], 'preguntas_en_2min'))

	
	cursor.execute("SELECT  ID_User FROM jugada INNER JOIN usuario USING (ID_User) WHERE ID_Concurso = (SELECT ID_Concurso FROM concurso ORDER BY ID_Concurso DESC LIMIT 1) AND Modo_de_Juego = '{0}' ORDER BY Creditos_Obtenidos DESC LIMIT 1".format("preguntas_en_5min"))

	ganador_preguntas_en_5min = cursor.fetchone()
	if not ganador_preguntas_en_5min == None:
		cursor.execute("INSERT INTO `Premiado` (`ID_Concurso`, `ID_User`, `Modo_de_Juego`) VALUES" \
			"('{0}', '{1}', '{2}')".format(concurso, ganador_preguntas_en_5min[0], 'preguntas_en_5min'))


	cursor.execute("SELECT ID_User, Nombre_User FROM jugada INNER JOIN usuario USING (ID_User) WHERE ID_Concurso = (SELECT ID_Concurso FROM concurso ORDER BY ID_Concurso DESC LIMIT 1) GROUP BY ID_User")
	listado_botones = []
	listado_botones.append(telegram.InlineKeyboardButton("Detalles", callback_data = "Detalles_Fin_Concurso"))
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
	
	Users = cursor.fetchall()
	for item in Users:
		try:
			update.message.chat.bot.send_message(chat_id = item[0], text = "Hola " + item[1].split(" ")[0] + " acaba de terminar el concurso en el cual participaste. Si desea ver sus resultados toque el siguiente boton ",parse_mode = 'Markdown', reply_markup=reply_markup)
		except:
			continue

	conexion.commit()
	conexion.close()
	
	return DETALLES_FIN_CONCURSO

def detalles_concurso_callbackquery(update, context):
	mode=update.callback_query.data

	if mode == "Cancelar":
		update.callback_query.message.delete()
		return ConversationHandler.END
	

	conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
	cursor = conexion.cursor()

	cursor.execute("SELECT ID_Concurso FROM concurso ORDER BY ID_Concurso DESC LIMIT 1")
	concurso = cursor.fetchone()
	
	cursor.execute("SELECT Total_Preguntas, Total_Preguntas_Correctas, Total_Preguntas_Incorrectas, Creditos_Obtenidos FROM jugada WHERE ID_Concurso = {0} AND ID_User = {1}".format(concurso[0], update._effective_chat.id))
	jugadas = cursor.fetchone()
	msg = "En este modo usted respondio {0} preguntas correctas y {1} preguntas incorrectas para un total de {2} preguntas, obteniendo {3} creditos.".format(jugadas[1], jugadas[2], jugadas[0], jugadas[3])

	listado_botones = []
	listado_botones.append(telegram.InlineKeyboardButton("Detalles", callback_data = "Detalles_Por_Preguntas_0_"+mode))
	listado_botones.append(telegram.InlineKeyboardButton("Cancelar", callback_data = "Cancelar_Fin"))
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))

	update.callback_query.bot.send_message(chat_id=update._effective_chat.id, text=msg,parse_mode = 'Markdown', reply_markup=reply_markup)
	return DETALLES_POR_PREGUNTAS

def detalles_por_preguntas(update, context):
	if update.callback_query.data == "Cancelar":
		update.callback_query.message.delete()
		return DETALLES_POR_MODOS
	elif update.callback_query.data == "Cancelar_Fin":
		update.callback_query.message.delete()
		return DETALLES_POR_PREGUNTAS
	data_split = update.callback_query.data.split("_")
	index = int(data_split[3])
	mode = ""
	for i in range(4, len(data_split)):
		mode += data_split[i]
		if i + 1 < len(data_split):
			mode += "_"

	if mode == "10Preguntas":
    		mode = "preguntas_10_mode"
	elif mode == "Supervivencia":
    		mode = "supervivencia_mode"

	respuesta = context.user_data[mode][1][index][1]

	msg = str(index + 1) +". " + str(context.user_data[mode][0][index]["Texto"]) + "\n"+\
		"Respondistes: " + str(context.user_data[mode][0][index]["RespuestasPosibles"][int(respuesta)][respuesta]) +"\n"+\
		"Respuesta Correcta: " + str(context.user_data[mode][0][index]["RespuestaCorrecta"]) + "\n"+\
		"Justificacion: "+ str(context.user_data[mode][0][index]["Explicacion"])
	
	listado_botones = []
	if index > 0:
		listado_botones.append(telegram.InlineKeyboardButton("Atras", callback_data = "Detalles_Por_Preguntas_{0}_".format(index - 1)+mode))
	if index < len(context.user_data[mode][0]) - 1:
		listado_botones.append(telegram.InlineKeyboardButton("Siguiente", callback_data = "Detalles_Por_Preguntas_{0}_".format(index + 1)+mode))
	

	listado_botones.append(telegram.InlineKeyboardButton("Cancelar", callback_data = "Cancelar"))
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1 if index == 0 else 2))

	update.callback_query.message.edit_text(msg,parse_mode = 'Markdown', reply_markup=reply_markup)
	return DETALLES_POR_PREGUNTAS

def resultados_concurso_callbackquery(update, context):
	if update.callback_query.data == "Detalles_Fin_Concurso":
		msg = "Usted participo en los siguientes modos. \n\n"
		conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
		cursor = conexion.cursor()
		cursor.execute("SELECT Modo_de_Juego FROM Jugada WHERE ID_User = {0} AND ID_Concurso = (SELECT ID_Concurso FROM concurso ORDER BY ID_Concurso DESC LIMIT 1)".format(update._effective_chat.id))
		current = cursor.fetchall()
		listado_botones = []

		for item in current:
			if item[0] == '10Preguntas':
				msg += "10 Preguntas \n"
				listado_botones.append(telegram.InlineKeyboardButton("10 Preguntas", callback_data = "10Preguntas"))
			elif item[0] == 'Supervivencia':
				msg += "Supervivencia \n"
				listado_botones.append(telegram.InlineKeyboardButton("Supervivencia", callback_data = "Supervivencia"))
			elif item[0][0:13] == 'preguntas_en_':
				msg += "Pregutas en {0} minutos \n".format(item[0][13])
				listado_botones.append(telegram.InlineKeyboardButton("Pregutas en {0} minutos \n".format(item[0][13]), callback_data = "pregutas_en_{0}min".format(item[0][13])))

		cursor.execute("SELECT Modo_de_Juego, Nombre_User FROM Premiado INNER JOIN Usuario USING(ID_User) WHERE ID_Concurso = (SELECT ID_Concurso FROM concurso ORDER BY ID_Concurso DESC LIMIT 1)")
		ganadores = cursor.fetchall()
		msg += "Los ganadores del concurso por modo de juego son: \n"
		for item in ganadores:
			msg += item[0] + ": " + item[1] + "\n"

		listado_botones.append(telegram.InlineKeyboardButton("Cancelar", callback_data = "Cancelar"))
		reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
		msg += "\nSi desea ver detalles toque el siguiente boton."
		update.callback_query.message.edit_text(msg,parse_mode = 'Markdown', reply_markup=reply_markup)
		return DETALLES_POR_MODOS

def add_administrador(update, context):
	conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
	cursor = conexion.cursor()
	if not update.effective_user['id'] == 937372768 and not update.effective_user['id'] == 716780131 and not update.effective_user['id'] == 823911446:
		cursor.execute("CREATE TABLE IF NOT EXISTS `Administrador` " \
			"(`ID_User` integer PRIMARY KEY NOT NULL)")
		cursor.execute("SELECT ID_User FROM Administrador")
		Users = cursor.fetchall()
		registrado = False
		for item in Users:
			if item[0] == update.effective_user['id']:
				registrado = True
				break
		if not registrado:
			update.message.chat.send_message("Usted no tiene permiso para agregar administradores")
			return ConversationHandler.END
		
	update.message.chat.send_message("Ingrese el id del nuevo administrador")
	return ADDADMINISTRADOR
	
def add_administrador_callbackQuery(update, context):
	text = update.message.text
	conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
	cursor = conexion.cursor()
	cursor.execute("CREATE TABLE IF NOT EXISTS `Administrador` " \
			"(`ID_User` integer PRIMARY KEY NOT NULL)")
	cursor.execute("SELECT ID_User FROM Administrador")
	Users = cursor.fetchall()
	registrado = False
	for item in Users:
		if item[0] == int(text):
			registrado = True
			break
	if  registrado:
		update.message.chat.send_message("Ya esta en la lista de los administradores")
		return ConversationHandler.END

	cursor.execute("INSERT INTO `Administrador` (`ID_User`) Values"\
			"('{0}')".format(int(text)))
	
	conexion.commit()
	conexion.close()
	update.message.chat.send_message("Administrador agregado")
	return ConversationHandler.END

def reclamaciones_administrador(update, context, is_back = False):
	conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
	cursor = conexion.cursor()
	if not update.effective_user['id'] == 937372768 and not update.effective_user['id'] == 716780131 and not update.effective_user['id'] == 823911446:
		cursor.execute("CREATE TABLE IF NOT EXISTS `Administrador` " \
		"(`ID_User` integer PRIMARY KEY NOT NULL)")
		cursor.execute("SELECT ID_User FROM Administrador")
		Users = cursor.fetchall()
		registrado = False
		for item in Users:
			if item[0] == update.effective_user['id']:
				registrado = True
				break

		if not registrado:
			update.message.chat.send_message("Usted no tiene permiso para acceder a este comando")
			return ConversationHandler.END

	listado = ["Ver Reclamaciones", "Borrar reclamaciones", "Cancelar"]
	listado_botones = []
	listado_botones.append(telegram.InlineKeyboardButton(listado[0], callback_data = "Reclamaciones"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[1], callback_data = "Borrar reclamaciones"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[2], callback_data = "Cancelar"))
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
	if not is_back: 
		update.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
		update.message.chat.send_message("Que desea hacer?", parse_mode = 'Markdown', reply_markup = reply_markup)
	else:
		update.callback_query.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
		update.callback_query.message.edit_text("Que desea hacer?", parse_mode = 'Markdown', reply_markup = reply_markup)
	
	return RECLAMACIONADMINISTRADOR

def reclamaciones_administrador_callbackQuery(update, context):
	query = update.callback_query
	if query.data == "Reclamaciones":
		conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
		cursor = conexion.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS Reclamacion " \
				"(`ID_R` integer  PRIMARY KEY AUTOINCREMENT NOT NULL, ID_User NOT NULL, `Texto`  VARCHAR(1000) NOT NULL)")
		cursor.execute("CREATE TABLE IF NOT EXISTS `Usuario` " \
		"(`ID_User` integer PRIMARY KEY NOT NULL, `Nombre_User` VARCHAR(50) NOT NULL)")
		cursor.execute("SELECT Nombre_User, Texto FROM RECLAMACION INNER JOIN Usuario USING(ID_User)")
		reclamaciones = cursor.fetchall()
		texto = ""
		index = 0
		for item in reclamaciones:
			texto += str(index + 1) + ". " + str(item[0]) + ": " + str(item[1]) + "\n"
			if index + 1 < len(reclamaciones):
				texto += "-"*30 + '\n'
			index += 1
		conexion.close()
		if texto == "":
			update.callback_query.message.chat.send_message("No hay reclamaciones en estos momentos")
		else:
			update.callback_query.message.chat.send_message(texto)
	elif query.data == "Borrar reclamaciones":
		return borrar_reclamaciones(update, context)
	elif query.data == "Cancelar":
		query.message.delete()
		return ConversationHandler.END

def borrar_reclamaciones(update, context):
	listado = ["Si", "No", "Cancelar"]
	listado_botones = []
	listado_botones.append(telegram.InlineKeyboardButton(listado[0], callback_data = "Si"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[1], callback_data = "No"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[2], callback_data = "Cancelar"))
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
	update.callback_query.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
	update.callback_query.message.edit_text("Estas seguro que quieres eliminar las reclamaciones?", parse_mode = 'Markdown', reply_markup = reply_markup)
	
	return BORRARRECLAMACIONES

def borrar_reclamaciones_callbackQuery(update, context):
	query = update.callback_query
	if query.data == "Si":
		conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
		cursor = conexion.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS Reclamacion " \
				"(`ID_R` integer  PRIMARY KEY AUTOINCREMENT NOT NULL, ID_User NOT NULL, `Texto`  VARCHAR(1000) NOT NULL)")
		cursor.execute("DROP TABLE Reclamacion")
		update.callback_query.message.edit_text("Todas las reclamaciones han sido borradas")
	elif query.data == "No":
		return reclamaciones_administrador(update, context, is_back = True)
	elif query.data == "Cancelar":
		query.message.delete()
		return ConversationHandler.END

def premios (update, context):
	conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
	cursor = conexion.cursor()
	if not update.effective_user['id'] == 937372768 and not update.effective_user['id'] == 716780131 and not update.effective_user['id'] == 823911446:
		cursor.execute("CREATE TABLE IF NOT EXISTS `Administrador` " \
		"(`ID_User` integer PRIMARY KEY NOT NULL)")
		cursor.execute("SELECT ID_User FROM Administrador")
		Users = cursor.fetchall()
		registrado = False
		for item in Users:
			if item[0] == update.effective_user.id:
				registrado = True
				break
		if not registrado:
			update.message.chat.send_message("Usted no tiene permiso para acceder a este comando")
			return ConversationHandler.END

	listado = ["Ver los premios del ultimo concurso", "Ver los premios general por Usuario", "Ver los premios general por Concurso", "Cancelar"]
	listado_botones = []
	listado_botones.append(telegram.InlineKeyboardButton(listado[0], callback_data = "Ver los premios del ultimo concurso"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[1], callback_data = "Ver los premios general por Usuario"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[2], callback_data = "Ver los premios general por Concurso"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[3], callback_data = "Cancelar"))
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
	update.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
	update.message.chat.send_message("Que desea hacer?", parse_mode = 'Markdown', reply_markup = reply_markup)
	return PREMIOS

def premios_callbackQuery(update, context): #probar todo
	query = update.callback_query
	conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
	cursor = conexion.cursor()
	cursor.execute("CREATE TABLE IF NOT EXISTS `Premiado`" \
		"(`ID_P`integer PRIMARY KEY NOT NULL, `ID_Concurso` integer NOT NULL, `ID_User` integer NOT NULL, `Modo_de_Juego`  VARCHAR(50) NOT NULL)")
	if query.data == "Ver los premios del ultimo concurso":
		cursor.execute("SELECT Nombre_User, Modo_de_Juego, Cantidad_Creditos FROM Premiado INNER JOIN Usuario USING(ID_User) NATURAL JOIN Premio WHERE Premiado.ID_Concurso = (SELECT ID_Concurso FROM concurso ORDER BY ID_Concurso DESC LIMIT 1) ORDER BY Nombre_User")
		premios = cursor.fetchall()
		texto = "Los datos se mostraran en el siguiente orden (Nombre_User, Modo_de_Juego, Cantidad_Creditos): \n"
		haypremios = False
		name = ""
		for item in premios:
			haypremios = True
			if name == "" or name != item[0]:
				name = item[0]
				texto += name+"\n"

			texto += "✔️ " +item[1] + " " + str(item[2])  + "\n"

		if not haypremios:
			texto = "No hay premios en estos momentos"

		update.callback_query.message.chat.send_message(texto)
	elif query.data == "Ver los premios general por Usuario":
		cursor.execute("SELECT Fecha_Inicio, Fecha_Fin, Nombre_User, Modo_de_Juego, Cantidad_Creditos FROM Premiado INNER JOIN Usuario USING(ID_User) INNER JOIN concurso USING(ID_Concurso) INNER JOIN Premio USING(Modo_de_Juego) ORDER BY Nombre_User")
		premios = cursor.fetchall()
		texto = "Los datos se mostraran en el siguiente orden (Fecha_Inicio, Fecha_Fin, Nombre_User, Modo_de_Juego, Cantidad_Creditos): \n"
		haypremios = False
		for item in premios:
			haypremios = True
			texto += str(item[0]) + " " + str(item[1]) + " " + item[2] + " " + item[3] + " " + str(item[4])  + "\n"

		if not haypremios:
			texto = "No hay premios en estos momentos"

		update.callback_query.message.chat.send_message(texto)
	elif query.data == "Ver los premios general por Concurso":
		cursor.execute("SELECT Fecha_Inicio, Fecha_Fin, Nombre_User, Modo_de_Juego, Cantidad_Creditos FROM Premiado INNER JOIN Usuario USING(ID_User) INNER JOIN concurso USING(ID_Concurso) INNER JOIN Premio USING(Modo_de_Juego)")
		premios = cursor.fetchall()
		texto = "Los datos se mostraran en el siguiente orden (Fecha_Inicio, Fecha_Fin, Nombre_User, Modo_de_Juego, Cantidad_Creditos): \n"
		haypremios = False
		for item in premios:
			haypremios = True
			texto += str(item[0]) + " " + str(item[1]) + " " + item[2] + " " + item[3] + " " + str(item[4])  + "\n"

		if not haypremios:
			texto = "No hay premios en estos momentos"

		update.callback_query.message.chat.send_message(texto)
	else:
		query.message.delete()
		return ConversationHandler.END

def mensaje(update, context):
	text = update.message.text
	text = text.split("\n")
	if text[0] == "*Add_Concurso*": 
		if  not update.effective_user['id'] == 937372768:
			conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
			cursor = conexion.cursor()
			cursor.execute("CREATE TABLE IF NOT EXISTS `Administrador` " \
				"(`ID_User` integer PRIMARY KEY NOT NULL)")
			cursor.execute("SELECT ID_User FROM Administrador")
			Users = cursor.fetchall()
			registrado = False
			for item in Users:
				registrado = True
				break

			if not registrado:
				update.message.chat.send_message("Usted no tiene permiso para anadir concursos")
				return

		data = {}
		data['Configuracion'] = []
		data['Configuracion'].append({
		"FechaDeInicio": text[1].split('=')[1],
		"HoraDeInicio": text[2].split('=')[1],
		"FechaDeFin" : text[3].split('=')[1],
		"HoraDeFin": text[4].split('=')[1],
		"PagoPorJugar": [{"10Preguntas" : int(text[5].split('=')[2])}, {"Supervivencia": int(text[6].split('=')[1])}, {"CuantoEnXminutos" : [{text[7].split('=')[1] : int(text[7].split('=')[2])}, {text[8].split('=')[0]: int(text[8].split('=')[1])}, {text[9].split('=')[0]: int(text[9].split('=')[1])}]}],
		"PremioPorCadaPregunta" : int(text[10].split('=')[1]),
		"PremioParaElGanadorEnCadaModo": [{"10Preguntas" : int(text[11].split('=')[2])}, {"Supervivencia": int(text[12].split('=')[1])}, {"CuantoEnXminutos" : [{text[13].split('=')[1] : int(text[13].split('=')[2])}, {text[14].split('=')[0]: int(text[14].split('=')[1])}, {text[15].split('=')[0]: int(text[15].split('=')[1])}]}],
		"PremioParaElGanadorEn2Modos" : int(text[16].split('=')[1]),
		"PremioParaElGanadorEn3Modos": int(text[17].split('=')[1]),
		"PremioParaElGanadorEn4Modos": int(text[18].split('=')[1]),
		"PremioParaElGanadorEn5Modos": int(text[19].split('=')[1])})

		with open("ConfiguracionDelConcurso.json", 'w') as file:
			json.dump(data, file, indent = 11)

		conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
		cursor = conexion.cursor()
		configuracionDelConcurso_json = open("ConfiguracionDelConcurso.json")
		configuracion = json.loads(configuracionDelConcurso_json.read())["Configuracion"]
		conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
		cursor = conexion.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS Concurso " \
				"(ID_Concurso integer  PRIMARY KEY AUTOINCREMENT NOT NULL, Fecha_Inicio datetime NOT NULL, Fecha_Fin datetime NOT NULL, Creditos_Por_Pregunta_Correcta int(11) NOT NULL)")
	
		cursor.execute("INSERT INTO concurso(`Fecha_Inicio`, `Fecha_Fin`,`Creditos_Por_Pregunta_Correcta`) VALUES" \
				"('{0}', '{1}', '{2}')".format(configuracion[0]["FechaDeInicio"] + " " + configuracion[0]["HoraDeInicio"], configuracion[0]["FechaDeFin"] + " " + configuracion[0]["HoraDeFin"], configuracion[0]["PremioPorCadaPregunta"]))
		conexion.commit()
		conexion.close()
		update.message.chat.send_message("Concurso anadido")

	elif text[0] == "*Add_Administrador*":
		conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
		cursor = conexion.cursor()
		if  not update.effective_user['id'] == 937372768:
			cursor.execute("CREATE TABLE IF NOT EXISTS `Administrador` " \
				"(`ID_User` integer PRIMARY KEY NOT NULL)")
			cursor.execute("SELECT ID_User FROM Administrador")
			Users = cursor.fetchall()
			registrado = False
			for item in Users:
				registrado = True
				break

			if not registrado:
				update.message.chat.send_message("Usted no tiene permiso para agregar administradores")
				return

		cursor.execute("INSERT INTO `Administrador` (`ID_User`) Values"\
			"('{0}')".format(int(text[1])))
		conexion.commit()
		conexion.close()
		update.message.chat.send_message("Administrador agregado")

def creditos(update, context, is_back = False):
	listado = ["Ver listado de Creditos", "Reclamar", "Cancelar"]
	listado_botones = []
	listado_botones.append(telegram.InlineKeyboardButton(listado[0], callback_data = "Listado de Creditos"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[1], callback_data = "Reclamar"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[2], callback_data = "Cancelar"))
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
	if not is_back: 
		update.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
		update.message.chat.send_message("Que desea hacer?", parse_mode = 'Markdown', reply_markup = reply_markup)
	else:
		update.callback_query.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
		update.callback_query.message.edit_text("Que desea hacer?", parse_mode = 'Markdown', reply_markup = reply_markup)
	return CREDITOS

def detalles_de_creditos(update, context):
	msg = ""
	query = update.callback_query
	listado = []
	listado_json = open("lista-de-estudiantes.json")
	estudiantes = json.loads(listado_json.read())["Estudiantes"]
	d = estudiantes[int(query.data.split(' ')[1])]["Fecha"]

	msg = estudiantes[int(query.data.split(' ')[1])]["Nombre"] + "\nTotal de Creditos: " + str(estudiantes[int(query.data.split(' ')[1])]["Total de Creditos"])
	index = 0
	for item in d:
		listado.append(list(item.keys())[0] + " -> " + str(estudiantes[int(query.data.split(' ')[1])]["Fecha"][index][list(item.keys())[1]]))
		index += 1
		
	listado_botones = [telegram.InlineKeyboardButton(listado[i], callback_data = ("Detalles de " + query.data.split(' ')[1] + " en index " + str(i)  + " fecha "+ listado[i])) for i in range(len(listado))]
	listado_botones.append(telegram.InlineKeyboardButton("Ver Todo", callback_data = "Ver_Todo_" + query.data.split(' ')[1]))
	listado_botones.append(telegram.InlineKeyboardButton("Atras", callback_data = "Atras_Listado_Creditos"))
	listado_botones.append(telegram.InlineKeyboardButton("Cancelar", callback_data = "Cancelar_Listado_Creditos"))
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
	update.callback_query.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
	update.callback_query.message.edit_text(msg, parse_mode = 'Markdown', reply_markup = reply_markup)
	return DETALLESCREDITOS

def creditos_callbackQuery(update, context):
	query = update.callback_query
	if query.data == "Listado de Creditos":
		return listado_creditos(update, context)
	elif query.data == "Reclamar":
		listado_botones = []
		listado_botones.append(telegram.InlineKeyboardButton("Si", callback_data = "Si"))
		listado_botones.append(telegram.InlineKeyboardButton("Atras", callback_data = "Atras"))
		listado_botones.append(telegram.InlineKeyboardButton("Cancelar", callback_data = "Cancelar"))
		reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
		query.bot.edit_message_text(chat_id = query.message.chat_id,message_id= query.message.message_id, text= "Esta seguro que desea enviar una reclamacion?", reply_markup=reply_markup)
		return RECLAMACION_CALLBACKQUERY
	elif query.data == "Cancelar":
		query.message.delete()
		return ConversationHandler.END

def listado_creditos(update, context):
	listado = []
	listado_json = open("lista-de-estudiantes.json")
	estudiantes = json.loads(listado_json.read())["Estudiantes"]
	for i in range(len(estudiantes)):
		listado.append(str(i + 1) + ". " + estudiantes[i]["Nombre"] + " -> " + estudiantes[i]["Total de Creditos"])

	listado_botones = [telegram.InlineKeyboardButton(listado[i], callback_data = ("Creditos " + str(i))) for i in range(len(listado))]
	listado_botones.append(telegram.InlineKeyboardButton("Atras", callback_data = "Atras_Listado_Creditos"))
	listado_botones.append(telegram.InlineKeyboardButton("Cancelar", callback_data = "Cancelar_Listado_Creditos"))
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
	update.callback_query.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
	update.callback_query.message.edit_text("Listado de creditos", parse_mode = 'Markdown', reply_markup = reply_markup)
	return LISTADO

def listado_callbackQuery(update, context):
	query = update.callback_query
	if query.data.split(' ')[0] == "Creditos":
		return detalles_de_creditos(update, context)
	elif query.data == "Atras_Listado_Creditos":
		return creditos(update, context, is_back = True)
	elif query.data == "Cancelar_Listado_Creditos":
		query.message.delete()
		return ConversationHandler.END

def reclamacion_callbackQuery(update, context):
	text = update.message.text
	conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
	cursor = conexion.cursor()
	cursor.execute("CREATE TABLE IF NOT EXISTS Reclamacion " \
			"(`ID_R` integer  PRIMARY KEY AUTOINCREMENT NOT NULL, ID_User NOT NULL, `Texto`  VARCHAR(1000) NOT NULL)")
	cursor.execute("INSERT INTO `Reclamacion` (ID_User, `Texto`) VALUES"\
					"('{0}', '{1}')".format(update.effective_user['id'], text))

	conexion.commit()
	conexion.close()
	update.message.chat.send_message("Su reclamacion ha sido agregada a la lista de reclamaciones, se le atendera lo mas rapido posible")
	return ConversationHandler.END
	
def detalles_de_creditos_callbackQuery(update, context):
	query = update.callback_query
	msg = ""
	if query.data.split(' ')[0] == "Detalles":
		listado_json = open("lista-de-estudiantes.json")
		estudiantes = json.loads(listado_json.read())["Estudiantes"]
		fecha = estudiantes[int(query.data.split(' ')[2])]["Fecha"][int(query.data.split(' ')[5])][query.data.split(' ')[7]]
		date_temp = ""
		amount_total_temp = 0
		index_temp = 0
		for date_temp, amount_total_temp in estudiantes[int(query.data.split(' ')[2])]["Fecha"]:
			if index_temp == int(query.data.split(' ')[5]):
					break
			index_temp += 1
		msg = "Fecha: " + date_temp + "\nMonto Total: " + str(estudiantes[int(query.data.split(' ')[2])]["Fecha"][index_temp][amount_total_temp]) + "\n\n"

		for item in fecha:
			if len("+"+str(item["Monto"]) + " " + item["Detalles"] + "\n" + msg) < 4096:
				msg += "+"+str(item["Monto"]) + " " + item["Detalles"] + "\n"
			else:
				update.callback_query.message.chat.send_message(msg)
				msg= ""

		if msg != "":
			update.callback_query.message.chat.send_message(msg)
	elif query.data.split('_')[0] == "Ver":
		listado_json = open("lista-de-estudiantes.json")
		estudiantes = json.loads(listado_json.read())["Estudiantes"]
		index_studient = int(query.data.split('_')[2])
		index_date = 0
		for date, total_amount in estudiantes[index_studient]["Fecha"]:
			if len("Fecha: " + date + "\nMonto Total:" + str(estudiantes[index_studient]["Fecha"][index_date][total_amount]) + "\n\n") < 4096:
				msg += "Fecha: " + date + "\nMonto Total: " + str(estudiantes[index_studient]["Fecha"][index_date][total_amount]) + "\n\n"
			else:
				update.callback_query.message.chat.send_message(msg)
				msg= ""
			index_detail = 0
			for amount, detail in estudiantes[index_studient]["Fecha"][index_date][date]:
				if len("+" + str(estudiantes[index_studient]["Fecha"][index_date][date][index_detail][amount]) + " " + estudiantes[index_studient]["Fecha"][index_date][date][index_detail][detail] + "\n") < 4096:
					msg +=  "+" + str(estudiantes[index_studient]["Fecha"][index_date][date][index_detail][amount]) + " " + estudiantes[index_studient]["Fecha"][index_date][date][index_detail][detail] + "\n"
				else:
					update.callback_query.message.chat.send_message(msg)
					msg= ""
				index_detail += 1
			msg += "\n"
			index_date += 1
		if msg != "":
			update.callback_query.message.chat.send_message(msg)
	elif query.data == "Atras_Listado_Creditos":
		return listado_creditos(update, context)
	elif query.data == "Cancelar_Listado_Creditos":
		query.message.delete()
		return ConversationHandler.END

def build_menu (buttons, n_cols, header_buttons = None, footer_buttons = None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    return menu

def preguntas_10_mode(update, context, its_ok):
	configuracionDelConcurso_json = open("ConfiguracionDelConcurso.json")
	configuracion = json.loads(configuracionDelConcurso_json.read())["Configuracion"]
	msg = "En este modo de juego, se te haran 10 preguntas para las cuales tendras un tiempo determinado para responderlas."
	listado = ["Comenzar", "Atras", "Ranking", "Cancelar"]
	listado_botones = []
	if its_ok:
		listado_botones.append(telegram.InlineKeyboardButton(listado[0], callback_data = "Comenzar_preguntas_10_mode"))
		msg += "\nPrecio de juego: " + str(configuracion[0]["PagoPorJugar"][0]["10Preguntas"]) + \
			"\nPremio para el ganador: " + str(configuracion[0]["PremioParaElGanadorEnCadaModo"][0]["10Preguntas"])
	listado_botones.append(telegram.InlineKeyboardButton(listado[2], callback_data = "Ranking_Modo10preguntas"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[1], callback_data = "Atras"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[3], callback_data = "Cancelar"))
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
	update.callback_query.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
	update.callback_query.message.edit_text(msg, parse_mode = 'Markdown', reply_markup = reply_markup)
	return START_MODE_GAME

def siguiente_pregunta(update, context, mode, is_back=False):
	preguntas_json = open("Preguntas/Preguntas.json")
	preguntas = json.loads(preguntas_json.read())["Preguntas"]
	cant_preguntas = len(preguntas)
	index = random.randint(0, cant_preguntas - 1)
	while context.user_data[mode][0].__contains__(preguntas[index]):
		index = random.randint(0, cant_preguntas - 1)
	context.user_data[mode][0].append(preguntas[index])
	opciones = [telegram.InlineKeyboardButton(str(preguntas[index]["RespuestasPosibles"][i][str(i)]), callback_data = ("Respuesta " + str(i) + " "+ str(len(context.user_data[mode][0])))) for i in range(len(preguntas[index]["RespuestasPosibles"]))]
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(opciones, n_cols = 1))
	update.callback_query.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
	quetions = "Pregunta " + str(len(context.user_data[mode][0])) + ") " + preguntas[index]["Texto"]

	if mode == "preguntas_10_mode" or mode == "supervivencia_mode":
		quetions_time = str(preguntas[index]["Tiempo"])+"s"

		messsageID = update.callback_query.message.chat.send_message(quetions).message_id
		def asd(secs_left, update_message, full_time, cant_preg):
			if cant_preg > len(context.user_data[mode][1]):
				update.callback_query.bot.edit_message_text(chat_id=update.callback_query.message.chat_id, message_id=messsageID,text= quetions + '\n'+ 'Te quedan {} {}'.format(secs_left, ' segundos para responder esta pregunta') +'\n' + render_progressbar(full_time, secs_left) + ("\n Vidas restantes:" + " \U00002764 "*context.user_data["vidas"] if mode == "supervivencia_mode" else ""), reply_markup = reply_markup)

		list_button = []
		def timeover(cant_preg):
			if cant_preg > len(context.user_data[mode][1]):
				list_button.append(telegram.InlineKeyboardButton("Siguiente", callback_data = "Respuesta -1 " + str(len(context.user_data[mode][0]))))
				reply_markup = telegram.InlineKeyboardMarkup(build_menu(list_button, n_cols = 1))
				update.callback_query.bot.edit_message_text(chat_id=update.callback_query.message.chat_id, message_id=messsageID, text= "Se te acabo el tiempo. Lo siento \n\n La pregunta era: " + quetions, reply_markup= reply_markup)

		create_timer(parse('{}'.format(quetions_time)), timeover, len(context.user_data[mode][0]))

		create_countdown(parse('{}'.format(quetions_time)), asd, update_message=messsageID,
    	                     full_time=int(parse('{}'.format(quetions_time))), cant_preg=len(context.user_data[mode][0]), context=context, mode=mode)

	elif mode[0: 13] == "preguntas_en_":
		quetions_time = str(int(mode[13]) * 60) + "s"
		secs_left = quetions_time
		if is_back:
			now_timestamp = datetime.datetime.now().timestamp()
			secs_left = str(int(parse('{}'.format(quetions_time)) - now_timestamp + context.user_data["start_timestamp"])) + "s"
			
		messsageID = update.callback_query.message.chat.send_message(quetions).message_id
		
		def asd(secs_left, update_message, full_time, cant_preg):
			if cant_preg > len(context.user_data[mode][1]):
				update.callback_query.bot.edit_message_text(chat_id=update.callback_query.message.chat_id, message_id=messsageID,text= quetions + '\n'+ 'Te quedan {} {}'.format(secs_left, 'segundos para responder esta pregunta') +'\n' + render_progressbar(full_time, secs_left), reply_markup = reply_markup)

		list_button = []
		def timeover(cant_preg):
			if cant_preg > len(context.user_data[mode][1]):
				context.user_data["status"] = "finish"
				list_button.append(telegram.InlineKeyboardButton("Terminar", callback_data = "Respuesta -1 " + str(len(context.user_data[mode][0]))))
				reply_markup = telegram.InlineKeyboardMarkup(build_menu(list_button, n_cols = 1))
				update.callback_query.bot.edit_message_text(chat_id=update.callback_query.message.chat_id, message_id=messsageID, text= "Se te acabo el tiempo. Lo siento \n\n La pregunta era: " + quetions + "\nPulse \"Terminar\" para continuar.", reply_markup= reply_markup)
				return ANSWER

		if context.user_data["status"] == "no_active":
			context.user_data["status"] = "is_running"

		if parse('{}'.format(secs_left)) > 0:
			create_timer(parse('{}'.format(secs_left)), timeover, len(context.user_data[mode][0]))

			create_countdown(parse('{}'.format(secs_left)), asd, update_message=messsageID,
				full_time=int(parse('{}'.format(quetions_time))), cant_preg=len(context.user_data[mode][0]), context=context, mode=mode)
		else:
			timeover(len(context.user_data[mode][0]))

	return ANSWER

def supervivencia_mode(update, context, its_ok):
	configuracionDelConcurso_json = open("ConfiguracionDelConcurso.json")
	configuracion = json.loads(configuracionDelConcurso_json.read())["Configuracion"]
	listado = ["Comenzar", "Atras" , "Ranking" , "Cancelar"]
	listado_botones = []
	msg = "En este modo de juego, podras responder preguntas hasta que contestes 3 incorrectamente."
	if its_ok:
		listado_botones.append(telegram.InlineKeyboardButton(listado[0], callback_data = "Comenzar_supervivencia_mode"))
		msg += " Pago por jugar: " + str(configuracion[0]["PagoPorJugar"][1]["Supervivencia"]) +\
			"\nPremio para el ganador: " + str(configuracion[0]["PremioParaElGanadorEnCadaModo"][1]["Supervivencia"])
	listado_botones.append(telegram.InlineKeyboardButton(listado[2], callback_data = "Ranking_ModoSupervivencia"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[1], callback_data = "Atras"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[3], callback_data = "Cancelar"))
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
	update.callback_query.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
	update.callback_query.message.edit_text(msg, parse_mode = 'Markdown', reply_markup = reply_markup)
	return START_MODE_GAME

def preguntas_en_Xmin(update, context, its_ok, mode = None):
	if mode == None:
		mode = update.callback_query.data
	configuracionDelConcurso_json = open("ConfiguracionDelConcurso.json")
	index = 0
	if int(mode[13]) == 5:
		index = 2
	else:
		index = int(mode[13]) - 1
	configuracion = json.loads(configuracionDelConcurso_json.read())["Configuracion"]

	msg = "En este modo de juego, podras responder todas las preguntas que puedas en " + mode[13] +  " minutos."
	listado = ["Comenzar", "Atras", "Ranking", "Cancelar"]
	listado_botones = []
	if its_ok:
		listado_botones.append(telegram.InlineKeyboardButton(listado[0], callback_data = "Comenzar_" + mode))
		msg += " Pago por jugar: " + str(configuracion[0]["PagoPorJugar"][2]["CuantoEnXminutos"][index][mode[13]]) +\
			"\nPremio para el ganador: " + str(configuracion[0]["PremioParaElGanadorEnCadaModo"][2]["CuantoEnXminutos"][index][mode[13]])
	listado_botones.append(telegram.InlineKeyboardButton(listado[2], callback_data = "Ranking_Modo" + mode))
	listado_botones.append(telegram.InlineKeyboardButton(listado[1], callback_data = "Atras"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[3], callback_data = "Cancelar"))
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
	update.callback_query.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
	
	update.callback_query.message.edit_text(msg, parse_mode = 'Markdown', reply_markup = reply_markup)
	return START_MODE_GAME

def cuenta_Regresiva(update, context):
	update.callback_query.message.edit_text(str(3))
	time.sleep(1)
	update.callback_query.message.edit_text(str(2))
	time.sleep(1)
	update.callback_query.message.edit_text(str(1))
	time.sleep(1)
	update.callback_query.message.edit_text("Listo!!!!")

def modo_de_juego(update, context):
	listado = ["10 preguntas", "Supervivencia", "Cuantas preguntas puedes resolver en 'X' minutos", "Atras", "Cancelar"]
	listado_botones = []
	listado_botones.append(telegram.InlineKeyboardButton(listado[0], callback_data = "preguntas_10_mode"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[1], callback_data = "supervivencia_mode"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[2], callback_data = "preguntas_en_Xmin"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[3], callback_data = "Atras"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[4], callback_data = "Cancelar_Modo_de_juego"))
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
	update.callback_query.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
	update.callback_query.message.edit_text("En que modo deseas jugar?", parse_mode = 'Markdown', reply_markup = reply_markup)
	return SELECT_MODE_GAME

def concurso (update, context, is_back=False):
	listado = ["Jugar", "Ranking", "Cancelar"]
	listado_botones = []
	listado_botones.append(telegram.InlineKeyboardButton(listado[0], callback_data = "Jugar"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[1], callback_data = "Ranking_General"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[2], callback_data = "Cancelar_Concurso"))
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
	its_ok = hay_concurso()
	configuracionDelConcurso_json = open("ConfiguracionDelConcurso.json")
	configuracion = json.loads(configuracionDelConcurso_json.read())["Configuracion"]
	msg = ""
	if its_ok:
    		msg = "Este concurso esta vigente desde el dia " + configuracion[0]["FechaDeInicio"] + " a las " + configuracion[0]["HoraDeInicio"]+ " hasta el dia " +  configuracion[0]["FechaDeFin"] + " a las " + configuracion[0]["HoraDeFin"] +\
				 ". Cada modo de juego tiene un precio en creditos que se debe pagar por jugar, si el monto excede lo que tienes de bono entonces se te descontara del saldo principal de creditos" +\
					 "\n\nPremios para los ganadores en mas de un modo:"+\
						 "\nPremio para el ganador en 2 modos: " + str(configuracion[0]["PremioParaElGanadorEn2Modos"])+\
							"\nPremio para el ganador en 3 modos: " + str(configuracion[0]["PremioParaElGanadorEn3Modos"])+\
								"\nPremio para el ganador en 4 modos: " + str(configuracion[0]["PremioParaElGanadorEn4Modos"])+\
									"\nPremio para el ganador en 5 modos: " + str(configuracion[0]["PremioParaElGanadorEn5Modos"])
	else:
    		msg = "No hay concurso disponible.\n\nCada modo de juego tiene un precio en creditos que se debe pagar por jugar, si el monto excede lo que tienes de bono entonces se te descontara del saldo principal de creditos"
	if not is_back:
		update.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
		if not its_ok:
			update.message.chat.send_message(msg,  parse_mode = 'Markdown', reply_markup = reply_markup)
		else:
			update.message.chat.send_message(msg,  parse_mode = 'Markdown', reply_markup = reply_markup)
	else:
		update.callback_query.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
		if not its_ok:
			update.callback_query.message.edit_text(msg,  parse_mode = 'Markdown', reply_markup = reply_markup)
		else:
			update.callback_query.message.edit_text(msg,  parse_mode = 'Markdown', reply_markup = reply_markup)
	return CONCURSO

def concurso_callbackQuery(update, context):
	query = update.callback_query
	if query.data == "Jugar":
		return modo_de_juego(update, context)
	elif query.data == "Ranking_General":
		return ranking_menu(update, context, mode = None)
	elif query.data == "Cancelar_Concurso":
		query.message.delete()
		return ConversationHandler.END

def ranking_menu(update, context, mode = None):
	listado_botones = []
	if mode == None:
		listado_botones.append(telegram.InlineKeyboardButton("Ranking Semanal", callback_data = "Ranking_Semanal_General"))
		listado_botones.append(telegram.InlineKeyboardButton("Ranking General", callback_data = "Ranking_General"))
		listado_botones.append(telegram.InlineKeyboardButton("Atras", callback_data = "Atras_Ranking_General"))
	elif mode == "10preguntas":
		listado_botones.append(telegram.InlineKeyboardButton("Ranking Semanal", callback_data = "Ranking_Semanal_Modo10Preguntas"))
		listado_botones.append(telegram.InlineKeyboardButton("Ranking General", callback_data = "Ranking_General_Modo10Preguntas"))
		listado_botones.append(telegram.InlineKeyboardButton("Atras", callback_data = "Atras_Modo10Preguntas"))
	elif mode == "Supervivencia":
		listado_botones.append(telegram.InlineKeyboardButton("Ranking Semanal", callback_data = "Ranking_Semanal_ModoSupervivencia"))
		listado_botones.append(telegram.InlineKeyboardButton("Ranking General", callback_data = "Ranking_General_ModoSupervivencia"))
		listado_botones.append(telegram.InlineKeyboardButton("Atras", callback_data = "Atras_ModoSupervivencia"))
	elif mode == "preguntas_en_1min":
		listado_botones.append(telegram.InlineKeyboardButton("Ranking Semanal", callback_data = "Ranking_Semanal_Modopreguntas_en_1min"))
		listado_botones.append(telegram.InlineKeyboardButton("Ranking General", callback_data = "Ranking_General_Modopreguntas_en_1min"))
		listado_botones.append(telegram.InlineKeyboardButton("Atras", callback_data = "Atras_Modopreguntas_en_1min"))
	elif mode == "preguntas_en_2min":
		listado_botones.append(telegram.InlineKeyboardButton("Ranking Semanal", callback_data = "Ranking_Semanal_Modopreguntas_en_2min"))
		listado_botones.append(telegram.InlineKeyboardButton("Ranking General", callback_data = "Ranking_General_Modopreguntas_en_2min"))
		listado_botones.append(telegram.InlineKeyboardButton("Atras", callback_data = "Atras_Modopreguntas_en_2min"))
	elif mode == "preguntas_en_5min":
		listado_botones.append(telegram.InlineKeyboardButton("Ranking Semanal", callback_data = "Ranking_Semanal_Modopreguntas_en_5min"))
		listado_botones.append(telegram.InlineKeyboardButton("Ranking General", callback_data = "Ranking_General_Modopreguntas_en_5min"))
		listado_botones.append(telegram.InlineKeyboardButton("Atras", callback_data = "Atras_Modopreguntas_en_5min"))

	listado_botones.append(telegram.InlineKeyboardButton("Cancelar", callback_data = "Cancelar"))
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
	update.callback_query.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
	update.callback_query.message.edit_text("Que ranking deseas ver?",  parse_mode = 'Markdown', reply_markup = reply_markup)
	return RANKING

def ranking_callbackQuery(update, context):
	query = update.callback_query
	its_ok = hay_concurso()
	if query.data == "Ranking_General":
		conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
		cursor = conexion.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS `Jugada`" \
		 			"(ID_Jugada integer  PRIMARY KEY AUTOINCREMENT NOT NULL, `ID_Concurso` integer, `ID_User` integer NOT NULL, `Modo_de_Juego`  VARCHAR(50) NOT NULL, `Creditos_Obtenidos` int(11) NOT NULL, `Total_Preguntas` int(11) NOT NULL, `Total_Preguntas_Correctas` int(11) NOT NULL, `Total_Preguntas_Incorrectas` int(11) NOT NULL)")
		cursor.execute("CREATE TABLE IF NOT EXISTS `Usuario` " \
		"(`ID_User` integer PRIMARY KEY NOT NULL, `Nombre_User` VARCHAR(50) NOT NULL)")
		cursor.execute("SELECT Nombre_User, SUM(Creditos_Obtenidos) AS Creditos FROM jugada INNER JOIN usuario USING (ID_User) GROUP BY ID_User ORDER BY Creditos DESC")
		Users = cursor.fetchall()
		listado = ""
		index = 1
		for item in Users:
			listado += str(index) + " " + item[0] + " " + str(item[1]) + "\n"
			index +=1
		update.callback_query.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
		if listado == "":
			listado = "No hay registros hasta el momento"
		update.callback_query.message.chat.send_message(listado)

	elif query.data == "Ranking_Semanal_General":
		conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
		cursor = conexion.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS `Jugada`" \
		 			"(ID_Jugada integer  PRIMARY KEY AUTOINCREMENT NOT NULL, `ID_Concurso` integer, `ID_User` integer NOT NULL, `Modo_de_Juego`  VARCHAR(50) NOT NULL, `Creditos_Obtenidos` int(11) NOT NULL, `Total_Preguntas` int(11) NOT NULL, `Total_Preguntas_Correctas` int(11) NOT NULL, `Total_Preguntas_Incorrectas` int(11) NOT NULL)")
		cursor.execute("CREATE TABLE IF NOT EXISTS `Usuario` " \
		"(`ID_User` integer PRIMARY KEY NOT NULL, `Nombre_User` VARCHAR(50) NOT NULL)")
		cursor.execute("SELECT Nombre_User, SUM(Creditos_Obtenidos) as Creditos FROM jugada INNER JOIN usuario USING (ID_User) WHERE ID_Concurso = (SELECT ID_Concurso FROM concurso ORDER BY ID_Concurso DESC LIMIT 1) GROUP BY ID_User ORDER BY Creditos DESC")
		Users = cursor.fetchall()
		listado = ""
		index = 1
		for item in Users:
			listado += str(index) + " " + item[0] + " " + str(item[1]) + "\n"
			index +=1
		update.callback_query.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
		if listado == "":
			listado = "No hay registros hasta el momento"
		update.callback_query.message.chat.send_message(listado)

	elif query.data == "Ranking_Semanal_Modo10Preguntas" or query.data == "Ranking_Semanal_ModoSupervivencia" or query.data == "Ranking_Semanal_Modopreguntas_en_1min" or query.data == "Ranking_Semanal_Modopreguntas_en_2min" or query.data == "Ranking_Semanal_Modopreguntas_en_5min":
		conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
		cursor = conexion.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS `Jugada`" \
		 			"(ID_Jugada integer  PRIMARY KEY AUTOINCREMENT NOT NULL, `ID_Concurso` integer, `ID_User` integer NOT NULL, `Modo_de_Juego`  VARCHAR(50) NOT NULL, `Creditos_Obtenidos` int(11) NOT NULL, `Total_Preguntas` int(11) NOT NULL, `Total_Preguntas_Correctas` int(11) NOT NULL, `Total_Preguntas_Incorrectas` int(11) NOT NULL)")
		cursor.execute("CREATE TABLE IF NOT EXISTS `Usuario` " \
		"(`ID_User` integer PRIMARY KEY NOT NULL, `Nombre_User` VARCHAR(50) NOT NULL)")
		cursor.execute("SELECT Nombre_User, Creditos_Obtenidos FROM jugada INNER JOIN usuario USING (ID_User) WHERE ID_Concurso = (SELECT ID_Concurso FROM concurso ORDER BY ID_Concurso DESC LIMIT 1) AND Modo_de_Juego = '{0}' ORDER BY Creditos_Obtenidos DESC".format(query.data[20: len(query.data)]))
		Users = cursor.fetchall()
		listado = ""
		index = 1
		for item in Users:
			listado += str(index) + " " + item[0] + " " + str(item[1]) + "\n"
			index +=1
		update.callback_query.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
		if listado == "":
			listado = "No hay registros hasta el momento"
		update.callback_query.message.chat.send_message(listado)

	elif query.data == "Ranking_General_Modo10Preguntas" or query.data == "Ranking_General_ModoSupervivencia" or query.data == "Ranking_General_Modopreguntas_en_1min" or query.data == "Ranking_General_Modopreguntas_en_2min" or query.data == "Ranking_General_Modopreguntas_en_5min":
		conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
		cursor = conexion.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS `Jugada`" \
		 			"(ID_Jugada integer  PRIMARY KEY AUTOINCREMENT NOT NULL, `ID_Concurso` integer, `ID_User` integer NOT NULL, `Modo_de_Juego`  VARCHAR(50) NOT NULL, `Creditos_Obtenidos` int(11) NOT NULL, `Total_Preguntas` int(11) NOT NULL, `Total_Preguntas_Correctas` int(11) NOT NULL, `Total_Preguntas_Incorrectas` int(11) NOT NULL)")
		cursor.execute("CREATE TABLE IF NOT EXISTS `Usuario` " \
		"(`ID_User` integer PRIMARY KEY NOT NULL, `Nombre_User` VARCHAR(50) NOT NULL)")
		cursor.execute("SELECT Nombre_USER, SUM(Creditos_Obtenidos) AS Creditos FROM jugada INNER JOIN usuario USING (ID_User) WHERE Modo_de_Juego = '{0}' GROUP BY ID_User ORDER BY Creditos DESC".format(query.data[20: len(query.data)]))
		Users = cursor.fetchall()
		listado = ""
		index = 1
		for item in Users:
			listado += str(index) + " " + item[0] + " " + str(item[1]) + "\n"
			index +=1
		update.callback_query.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
		if listado == "":
			listado = "No hay registros hasta el momento"
		update.callback_query.message.chat.send_message(listado)

	elif query.data == "Atras_Ranking_General":
		return concurso(update, context, is_back = True)

	elif query.data == "Atras_Modo10Preguntas":
		return preguntas_10_mode(update, context, its_ok=its_ok)

	elif query.data == "Atras_ModoSupervivencia":
		return supervivencia_mode(update, context, its_ok=its_ok)

	elif query.data == "Atras_Modopreguntas_en_1min" or query.data == "Atras_Modopreguntas_en_2min" or query.data == "Atras_Modopreguntas_en_5min":
		return preguntas_en_Xmin(update, context,its_ok=its_ok, mode = query.data[10: len(query.data)])

	elif query.data == "Cancelar":
		query.message.delete()
		return ConversationHandler.END
		
def select_mode_game(update, context):
	its_ok = hay_concurso()

	query = update.callback_query
	if query.data == "preguntas_10_mode":
		return preguntas_10_mode(update, context, its_ok)
	elif query.data == "supervivencia_mode":
		return supervivencia_mode(update, context, its_ok)
	elif query.data == "preguntas_en_Xmin":
		return time_options(update, context)
	elif query.data == "Atras":
		return concurso(update, context, is_back=True)
	else:
		query.message.delete()
		return ConversationHandler.END
		
def start_modo_game(update, context):
	query = update.callback_query
	if query.data.split('_')[0] == "Comenzar":
		configuracionDelConcurso_json = open("ConfiguracionDelConcurso.json")
		configuracion = json.loads(configuracionDelConcurso_json.read())["Configuracion"]
		FechaDeInicio = configuracion[0]["FechaDeInicio"].split('-')
		FechaDeFin = configuracion[0]["FechaDeFin"].split('-')
		HoraDeInicio = configuracion[0]["HoraDeInicio"].split(':')
		HoraDeFin = configuracion[0]["HoraDeFin"].split(':')
		if not (datetime.datetime(int(FechaDeInicio[0]), int(FechaDeInicio[1]), int(FechaDeInicio[2]), int(HoraDeInicio[0]), int(HoraDeInicio[1]), 00, 000000) < datetime.datetime.now() and  datetime.datetime.now() < datetime.datetime(int(FechaDeFin[0]), int(FechaDeFin[1]), int(FechaDeFin[2]), int(HoraDeFin[0]), int(HoraDeFin[1]), 00, 000000)):
			update.callback_query.message.chat.send_message("Lo siento no hay concurso disponible en estos momentos")
			return

	if query.data == "Comenzar_preguntas_10_mode":
		conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
		cursor = conexion.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS `Jugada`" \
		 			"(ID_Jugada integer  PRIMARY KEY AUTOINCREMENT NOT NULL, `ID_Concurso` integer, `ID_User` integer NOT NULL, `Modo_de_Juego`  VARCHAR(50) NOT NULL, `Creditos_Obtenidos` int(11) NOT NULL, `Total_Preguntas` int(11) NOT NULL, `Total_Preguntas_Correctas` int(11) NOT NULL, `Total_Preguntas_Incorrectas` int(11) NOT NULL)")
		cursor.execute("CREATE TABLE IF NOT EXISTS Concurso " \
			"(ID_Concurso integer  PRIMARY KEY AUTOINCREMENT NOT NULL, Fecha_Inicio datetime NOT NULL, Fecha_Fin datetime NOT NULL, Creditos_Por_Pregunta_Correcta int(11) NOT NULL)")
	
		cursor.execute("SELECT ID_User FROM jugada WHERE Modo_de_Juego = '10Preguntas' and  ID_Concurso = (SELECT ID_Concurso FROM concurso ORDER BY ID_Concurso DESC LIMIT 1) GROUP BY ID_User")
		Users = cursor.fetchall()
		registrado = False
		for item in Users:
			if update.effective_user['id'] == int(item[0]):
				registrado = True
				break
		if registrado:
			query.message.edit_text("Ya jugaste en este modo en este concurso")
			return ConversationHandler.END
		else:
			context.user_data["preguntas_10_mode"] = [[],[]] #LISTA DE LEN 2 DONDE VAN HACER PREGUNTAS, RESPUESTAS
			context.user_data["current_mode"] = "preguntas_10_mode"
			query.message.edit_text(query.message.text)
			return siguiente_pregunta(update, context, mode="preguntas_10_mode")

	elif query.data == "Comenzar_supervivencia_mode":
		conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
		cursor = conexion.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS `Jugada`" \
		 			"(ID_Jugada integer  PRIMARY KEY AUTOINCREMENT NOT NULL, `ID_Concurso` integer, `ID_User` integer NOT NULL, `Modo_de_Juego`  VARCHAR(50) NOT NULL, `Creditos_Obtenidos` int(11) NOT NULL, `Total_Preguntas` int(11) NOT NULL, `Total_Preguntas_Correctas` int(11) NOT NULL, `Total_Preguntas_Incorrectas` int(11) NOT NULL)")
		cursor.execute("CREATE TABLE IF NOT EXISTS Concurso " \
			"(ID_Concurso integer  PRIMARY KEY AUTOINCREMENT NOT NULL, Fecha_Inicio datetime NOT NULL, Fecha_Fin datetime NOT NULL, Creditos_Por_Pregunta_Correcta int(11) NOT NULL)")
	
		cursor.execute("SELECT ID_User FROM jugada WHERE Modo_de_Juego = 'Supervivencia' and  ID_Concurso = (SELECT ID_Concurso FROM concurso ORDER BY ID_Concurso DESC LIMIT 1) GROUP BY ID_User")
		Users = cursor.fetchall()
		registrado = False
		for item in Users:
			if update.effective_user['id'] == int(item[0]):
				registrado = True
				break
		if registrado:
			query.message.edit_text("Ya jugaste en este modo en este concurso")
			return ConversationHandler.END
		else:
			context.user_data["supervivencia_mode"] = [[],[]] #LISTA DE LEN 2 DONDE VAN HACER PREGUNTAS, RESPUESTAS
			context.user_data["current_mode"] = "supervivencia_mode"
			context.user_data["vidas"] = 3
			query.message.edit_text(query.message.text)
			return siguiente_pregunta(update, context, mode="supervivencia_mode")

	elif query.data[0 : 22] == "Comenzar_preguntas_en_":
		mode = "preguntas_en_" + query.data[22] + "min"
		conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
		cursor = conexion.cursor()
		cursor.execute("CREATE TABLE IF NOT EXISTS `Jugada`" \
		 			"(ID_Jugada integer  PRIMARY KEY AUTOINCREMENT NOT NULL, `ID_Concurso` integer, `ID_User` integer NOT NULL, `Modo_de_Juego`  VARCHAR(50) NOT NULL, `Creditos_Obtenidos` int(11) NOT NULL, `Total_Preguntas` int(11) NOT NULL, `Total_Preguntas_Correctas` int(11) NOT NULL, `Total_Preguntas_Incorrectas` int(11) NOT NULL)")
		cursor.execute("CREATE TABLE IF NOT EXISTS Concurso " \
			"(ID_Concurso integer  PRIMARY KEY AUTOINCREMENT NOT NULL, Fecha_Inicio datetime NOT NULL, Fecha_Fin datetime NOT NULL, Creditos_Por_Pregunta_Correcta int(11) NOT NULL)")
	
		cursor.execute("SELECT ID_User FROM jugada WHERE Modo_de_Juego = '{0}' and  ID_Concurso = (SELECT ID_Concurso FROM concurso ORDER BY ID_Concurso DESC LIMIT 1) GROUP BY ID_User".format(mode))
		Users = cursor.fetchall()
		registrado = False
		for item in Users:
			if update.effective_user['id'] == int(item[0]):
				registrado = True
				break
		if registrado:
			query.message.edit_text("Ya jugaste en este modo en este concurso")
			return ConversationHandler.END
		else:
			context.user_data["preguntas_en_" + query.data[22] + "min"] = [[],[]] #LISTA DE LEN 2 DONDE VAN HACER PREGUNTAS, RESPUESTAS
			context.user_data["current_mode"] = "preguntas_en_" + query.data[22] + "min"
			context.user_data["status"] = "no_active"
			context.user_data["start_timestamp"] = -1
			query.message.edit_text(query.message.text)
			return siguiente_pregunta(update, context, mode="preguntas_en_" + query.data[22] + "min")
	elif query.data == "Atras":
		return modo_de_juego(update, context)
	elif query.data.split("_")[0] == "Ranking":
		return ranking_menu(update, context, mode = query.data[12: len(query.data)])
	else:
		query.message.delete()
		return ConversationHandler.END

def time_options(update, context):
	listado = ["1 minuto", "2 minutos", "5 minutos", "Atras", "Cancelar"]
	listado_botones = []
	listado_botones.append(telegram.InlineKeyboardButton(listado[0], callback_data = "preguntas_en_1min"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[1], callback_data = "preguntas_en_2min"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[2], callback_data = "preguntas_en_5min"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[3], callback_data = "Atras"))
	listado_botones.append(telegram.InlineKeyboardButton(listado[4], callback_data = "Cancelar_time"))
	reply_markup = telegram.InlineKeyboardMarkup(build_menu(listado_botones, n_cols = 1))
	update.callback_query.message.chat.send_action(action = ChatAction.TYPING, timeout = None)
	update.callback_query.message.edit_text("Cuanto tiempo quieres jugar?", parse_mode = 'Markdown', reply_markup = reply_markup)
	return SELECT_TIME

def select_time(update, context):
	its_ok = hay_concurso()
	query = update.callback_query
	if query.data[0: 13] == "preguntas_en_":
		return preguntas_en_Xmin(update, context, its_ok=its_ok)
	elif query.data == "Atras":
		return modo_de_juego(update, context)
	else:
		query.message.delete()
		return ConversationHandler.END

def answer_quetions(update, context):
	query = update.callback_query
	mode = context.user_data["current_mode"]
	respuesta = query.data.split(" ")
	if mode == "preguntas_10_mode":
		if int(respuesta[2]) > len(context.user_data[mode][1]):
			context.user_data[mode][1].append(respuesta)
			if respuesta[1] != '-1':
				query.bot.edit_message_text(chat_id = query.message.chat_id,message_id= query.message.message_id, text= context.user_data[mode][0][len(context.user_data[mode][0]) - 1]["Texto"] + "\n\n Respondiste: " + str(context.user_data[mode][0][len(context.user_data[mode][0]) - 1]["RespuestasPosibles"][int(respuesta[1])][respuesta[1]]))
			else:
				query.message.edit_text(query.message.text)
			
			if len(context.user_data[mode][0]) == 10:
				query.bot.send_message(chat_id = query.message.chat_id, text= "Juego terminado!!!! Cuando acabe el concurso estaran disponibles los resultados", parse_mode = telegram.ParseMode.HTML)
				conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
				cursor = conexion.cursor()
				cursor.execute("CREATE TABLE IF NOT EXISTS `Jugada`" \
		 			"(ID_Jugada integer  PRIMARY KEY AUTOINCREMENT NOT NULL, `ID_Concurso` integer, `ID_User` integer NOT NULL, `Modo_de_Juego`  VARCHAR(50) NOT NULL, `Creditos_Obtenidos` int(11) NOT NULL, `Total_Preguntas` int(11) NOT NULL, `Total_Preguntas_Correctas` int(11) NOT NULL, `Total_Preguntas_Incorrectas` int(11) NOT NULL)")

				respuestas_correctas = procesador_de_soluciones(context.user_data["preguntas_10_mode"])
				cursor.execute("SELECT ID_Concurso, Creditos_Por_Pregunta_Correcta FROM concurso ORDER BY ID_Concurso DESC LIMIT 1")
				Concurso_actual = cursor.fetchone()
				if Concurso_actual == None:
					return ConversationHandler.END
				cursor.execute("INSERT INTO `Jugada` (`ID_Concurso`,`ID_User`,`Modo_de_Juego`,`Creditos_Obtenidos`,`Total_Preguntas`,`Total_Preguntas_Correctas`,`Total_Preguntas_Incorrectas`) VALUES"\
					"('{0}', '{1}', '10Preguntas', '{2}', 10, '{3}', '{4}')".format(Concurso_actual[0], update.effective_user['id'], Concurso_actual[1] * respuestas_correctas ,len(context.user_data["preguntas_10_mode"][0]), respuestas_correctas, len(context.user_data["preguntas_10_mode"][0]) - respuestas_correctas))
				conexion.commit()
				conexion.close()
				return ConversationHandler.END
			else:
				ConversationHandler.END
				return siguiente_pregunta(update, context, mode)
	elif mode == "supervivencia_mode":
		if int(respuesta[2]) > len(context.user_data[mode][1]):
			context.user_data[mode][1].append(respuesta)
			if respuesta[1] != '-1':
				query.bot.edit_message_text(chat_id = query.message.chat_id,message_id= query.message.message_id, text= context.user_data[mode][0][len(context.user_data[mode][0]) - 1]["Texto"] + "\n\n Respondiste: " + str(context.user_data[mode][0][len(context.user_data[mode][0]) - 1]["RespuestasPosibles"][int(respuesta[1])][respuesta[1]]))
				correct_answer = context.user_data[mode][0][len(context.user_data[mode][0]) - 1]["RespuestaCorrecta"]
				if context.user_data[mode][0][len(context.user_data[mode][0]) - 1]["RespuestasPosibles"][int(respuesta[1])][respuesta[1]] != correct_answer:
					context.user_data["vidas"] -= 1
			else:
				query.message.edit_text(query.message.text)
				context.user_data["vidas"] -= 1
			if context.user_data["vidas"] == 0:
				query.bot.send_message(chat_id = query.message.chat_id, text= "Juego terminado!!!! Cuando acabe el concurso estaran disponibles los resultados", parse_mode = telegram.ParseMode.HTML)
				conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
				cursor = conexion.cursor()
				cursor.execute("CREATE TABLE IF NOT EXISTS `Jugada`" \
		 			"(ID_Jugada integer  PRIMARY KEY AUTOINCREMENT NOT NULL, `ID_Concurso` integer, `ID_User` integer NOT NULL, `Modo_de_Juego`  VARCHAR(50) NOT NULL, `Creditos_Obtenidos` int(11) NOT NULL, `Total_Preguntas` int(11) NOT NULL, `Total_Preguntas_Correctas` int(11) NOT NULL, `Total_Preguntas_Incorrectas` int(11) NOT NULL)")

				respuestas_correctas = procesador_de_soluciones(context.user_data["supervivencia_mode"])
				cursor.execute("SELECT ID_Concurso, Creditos_Por_Pregunta_Correcta FROM concurso ORDER BY ID_Concurso DESC LIMIT 1")
				Concurso_actual = cursor.fetchone()
				cursor.execute("INSERT INTO `Jugada` (`ID_Concurso`,`ID_User`,`Modo_de_Juego`,`Creditos_Obtenidos`,`Total_Preguntas`,`Total_Preguntas_Correctas`,`Total_Preguntas_Incorrectas`) VALUES"\
					"({0}, {1}, 'Supervivencia', {2}, {3}, {4}, 3)".format(Concurso_actual[0], update.effective_user['id'], Concurso_actual[1] * respuestas_correctas ,len(context.user_data["supervivencia_mode"][0]), respuestas_correctas))
				conexion.commit()
				conexion.close()
				return ConversationHandler.END
			else:
				ConversationHandler.END
				return siguiente_pregunta(update, context, mode)
	elif mode[0:13] == "preguntas_en_":
		if context.user_data["status"] == "finish":
			query.bot.send_message(chat_id = query.message.chat_id, text= "Juego terminado!!!! Cuando acabe el concurso estaran disponibles los resultados", parse_mode = telegram.ParseMode.HTML)
			conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
			cursor = conexion.cursor()
			cursor.execute("CREATE TABLE IF NOT EXISTS `Jugada`" \
		 			"(ID_Jugada integer  PRIMARY KEY AUTOINCREMENT NOT NULL, `ID_Concurso` integer, `ID_User` integer NOT NULL, `Modo_de_Juego`  VARCHAR(50) NOT NULL, `Creditos_Obtenidos` int(11) NOT NULL, `Total_Preguntas` int(11) NOT NULL, `Total_Preguntas_Correctas` int(11) NOT NULL, `Total_Preguntas_Incorrectas` int(11) NOT NULL)")
			respuestas_correctas = procesador_de_soluciones(context.user_data[mode])
			cursor.execute("SELECT ID_Concurso, Creditos_Por_Pregunta_Correcta FROM concurso ORDER BY ID_Concurso DESC LIMIT 1")
			Concurso_actual = cursor.fetchone()
			cursor.execute("INSERT INTO `Jugada` (`ID_Concurso`,`ID_User`,`Modo_de_Juego`,`Creditos_Obtenidos`,`Total_Preguntas`,`Total_Preguntas_Correctas`,`Total_Preguntas_Incorrectas`) VALUES"\
					"('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format(Concurso_actual[0], update.effective_user['id'], mode, Concurso_actual[1] * respuestas_correctas, len(context.user_data[mode][0]), respuestas_correctas, len(context.user_data[mode][0]) - respuestas_correctas))
			
			conexion.commit()
			conexion.close()
			
			return ConversationHandler.END
		elif int(respuesta[2]) > len(context.user_data[mode][1]) and context.user_data["status"] == "is_running":
			context.user_data[mode][1].append(respuesta)
			query.bot.edit_message_text(chat_id = query.message.chat_id,message_id= query.message.message_id, text= context.user_data[mode][0][len(context.user_data[mode][0]) - 1]["Texto"] + "\n\n Respondiste: " + str(context.user_data[mode][0][len(context.user_data[mode][0]) - 1]["RespuestasPosibles"][int(respuesta[1])][respuesta[1]]))
			return siguiente_pregunta(update, context, mode, is_back=True)		

def procesador_de_soluciones(preguntas):
	respuestas_correctas = 0
	for item in range(0, len(preguntas[0]) - 1):
		correct_answer = preguntas[0][item]["RespuestaCorrecta"]
		if int(preguntas[1][item][1]) != -1 and preguntas[0][item]["RespuestasPosibles"][int(preguntas[1][item][1])][str(preguntas[1][item][1])] == correct_answer:
			respuestas_correctas+=1
	return respuestas_correctas

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
        	TypeError("Timeout is None {}".format(timeout_secs))
        timer3.apply_after((timeout_secs + 1) * 1000, callback, args=args, kwargs=kwargs)

def create_countdown(timeout_secs, callback, context, mode, **kwargs):
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
			if not max(secs_left, 0) or len(context.user_data[context.user_data["current_mode"]][0]) == len(context.user_data[context.user_data["current_mode"]][1]):
				timer.stop()

	start_timestamp = datetime.datetime.now().timestamp()

	if mode[0: 13] == "preguntas_en_" and context.user_data["start_timestamp"] == -1:
		context.user_data["start_timestamp"] = start_timestamp
	timer = timer3.Timer()
	timer.apply_interval(1000, callback_wrapper, kwargs=kwargs)

def update_databese(update, context):
	if update.effective_user['id'] == 937372768 or update.effective_user['id'] == 716780131:
		database = open("NumericaBotDatabase/numericabot.db",  "rb")
		update.message.chat.send_document(database)
	else:
		update.message.chat.send_message("Usted no tiene accseso al comando solicitado.")

def reclamacion_CQ(update,context):
	query = update.callback_query
	if query.data == "Si":
		query.bot.edit_message_text(chat_id = query.message.chat_id,message_id= query.message.message_id, text= "Por favor, escriba su reclamacion, sea lo mas claro posible")
		return RECLAMACION
	elif query.data == "Atras":
		return creditos(update, context, True)
	elif query.data == "Cancelar":
		query.message.delete()
		return ConversationHandler.END

def hay_concurso():
	configuracionDelConcurso_json = open("ConfiguracionDelConcurso.json")
	configuracion = json.loads(configuracionDelConcurso_json.read())["Configuracion"]
	FechaDeInicio = configuracion[0]["FechaDeInicio"].split('-')
	FechaDeFin = configuracion[0]["FechaDeFin"].split('-')
	HoraDeInicio = configuracion[0]["HoraDeInicio"].split(':')
	HoraDeFin = configuracion[0]["HoraDeFin"].split(':')	

	return datetime.datetime(int(FechaDeInicio[0]), int(FechaDeInicio[1]), int(FechaDeInicio[2]), int(HoraDeInicio[0]), int(HoraDeInicio[1]), 00, 000000) < datetime.datetime.now() and  datetime.datetime.now() < datetime.datetime(int(FechaDeFin[0]), int(FechaDeFin[1]), int(FechaDeFin[2]), int(HoraDeFin[0]), int(HoraDeFin[1]), 00, 000000)

def get_coincidence():
	pass

def my_send_message_all(update, context):
	if len(context.args) >= 1:
		conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
		cursor = conexion.cursor()
		cursor.execute("SELECT * FROM Usuario")
		user = cursor.fetchall()
		msg = ""
		for i in range(1, len(context.args)):
			msg += context.args[i] + " "
		for id_user in user[0]:
			if id_user == update.effective_user['id']:
				continue
			try:
				update.message.chat.bot.send_message(chat_id=id_user, text=msg)
			except:
				continue
		update.message.chat.send_message("✅ Mensaje enviado correctamente.")
	else:
		update.message.chat.send_message("⛔️ Algo no estas haciendo bien. La sintaxis correcta es la siguente: \n\n /send_message <message>")
	

def my_send_message(update, context):
	if len(context.args) >= 2:
		msg = ""
		for i in range(1, len(context.args)):
			msg += context.args[i] + " " 
		msg += "\n\n Mensaje enviado por: @" + update.effective_user['username']
		all_ok = True
		try:
			update.message.chat.bot.send_message(chat_id=context.args[0], text=msg)
		except:
			all_ok = False
			update.message.chat.send_message("⛔️ Algo salio mal, por favor revise el ID del usuario si es correcto.")
		finally:
			if all_ok:
				update.message.chat.send_message("✅ Mensaje enviado correctamente.")
	else:
		update.message.chat.send_message("⛔️ Algo no estas haciendo bien. La sintaxis correcta es la siguente: \n\n /send_message <id_user> <message>")

def get_alluser(update, context):
	conexion = sqlite3.connect("NumericaBotDatabase/numericabot.db")
	cursor = conexion.cursor()
	cursor.execute("SELECT * FROM Usuario")
	user = cursor.fetchall()
	msg = "Estos son todos los usuarios registrados:\n"
	index = 1
	for item in user:
		msg += str(index) + ". " + str(item) + "\n"
		index += 1
	update.message.chat.send_message(msg)

def get_info(update, context):
	update.message.chat.send_message("Estos son todos los comados disponibles: \
		\n\n/get_database \
		\n/get_alluser \
		\n/send_message <id_user> <message>\
		\n/send_message_all <message>")

def main():
	bot = telegram.Bot(token = "1670025923:AAHsyihT5o0Oaoj3YLDOki0A77R1JarBGQ0")
	update = Updater(bot.token, use_context=True) 
	dp = update.dispatcher
	start_handler = ConversationHandler(
		entry_points = [
			CommandHandler('start', start),
		],

		states = {
			NAME : [MessageHandler(Filters.text, name)]
		}, 
			fallbacks = []
	)

	creditos_handler = ConversationHandler(
		entry_points = [
			CommandHandler('creditos', creditos),
		],

		states={
			CREDITOS:[CallbackQueryHandler(creditos_callbackQuery, pass_user_data=True)],
			LISTADO:[CallbackQueryHandler(listado_callbackQuery, pass_user_data=True)],
			RECLAMACION_CALLBACKQUERY: [CallbackQueryHandler(reclamacion_CQ)],
			RECLAMACION : [MessageHandler(Filters.text, reclamacion_callbackQuery)],
			DETALLESCREDITOS: [CallbackQueryHandler(detalles_de_creditos_callbackQuery, pass_user_data=True)]
		},

		fallbacks=[]
	)

	concurso_handler = ConversationHandler(
		entry_points = [
			CommandHandler('concurso', concurso),
		],

		states={
			CONCURSO: [CallbackQueryHandler(concurso_callbackQuery)],
			JUGAR: [CallbackQueryHandler(modo_de_juego)],
			SELECT_MODE_GAME: [CallbackQueryHandler(select_mode_game)],
			START_MODE_GAME: [CallbackQueryHandler(start_modo_game, pass_user_data=True)],
			ANSWER: [CallbackQueryHandler(answer_quetions, pass_user_data=True)],
			SELECT_TIME: [CallbackQueryHandler(select_time, pass_user_data=True)],
			RANKING: [CallbackQueryHandler(ranking_callbackQuery, pass_user_data=True)]
		},

		fallbacks=[]
	)

	add_concurso_handler = ConversationHandler(
		entry_points = [
			CommandHandler('addconcurso', add_concurso),
		],

		states = {
			ADDCONCURSO : [MessageHandler(Filters.text, add_concurso_callbackQuery)],
			#DETALLES_FIN_CONCURSO: [CallbackQueryHandler(resultados_concurso_callbackquery)],
			#DETALLES_POR_MODOS: [CallbackQueryHandler(detalles_concurso_callbackquery)],
			#DETALLES_POR_PREGUNTAS: [CallbackQueryHandler(detalles_por_preguntas)]
		}, 
			
		fallbacks = []
	)

	detalles_concurso_handler = ConversationHandler(
		entry_points = [
			CallbackQueryHandler(resultados_concurso_callbackquery),
		],

		states = {
			DETALLES_POR_MODOS: [CallbackQueryHandler(detalles_concurso_callbackquery)],
			DETALLES_POR_PREGUNTAS: [CallbackQueryHandler(detalles_por_preguntas)]
		},

		fallbacks = []
	)

	add_administrador_handler = ConversationHandler(
		entry_points = [
			CommandHandler('addadministrador', add_administrador),
		],

		states = {
			ADDADMINISTRADOR : [MessageHandler(Filters.text, add_administrador_callbackQuery)],
		}, 

		fallbacks = []
	)

	reclamaciones_administrador_handler = ConversationHandler(
		entry_points = [
			CommandHandler('reclamaciones', reclamaciones_administrador),
		],

		states = {
			RECLAMACIONADMINISTRADOR:[CallbackQueryHandler(reclamaciones_administrador_callbackQuery, pass_user_data=True)],
			BORRARRECLAMACIONES:[CallbackQueryHandler(borrar_reclamaciones_callbackQuery, pass_user_data=True)]
		}, 

		fallbacks = []
	)

	premiados_handler = ConversationHandler(
		entry_points = [
			CommandHandler('premios', premios),
		],

		states = {
			PREMIOS:[CallbackQueryHandler(premios_callbackQuery, pass_user_data=True)],
		}, 

		fallbacks = []
	)

	help_handler = ConversationHandler(
		entry_points = [
			CommandHandler('help', help),
		],

		states = {
		}, 

		fallbacks = []
	)

	dp.add_handler(concurso_handler)
	dp.add_handler(creditos_handler)
	dp.add_handler(start_handler)
	dp.add_handler(add_concurso_handler)
	dp.add_handler(add_administrador_handler)
	dp.add_handler(reclamaciones_administrador_handler)
	dp.add_handler(premiados_handler)
	dp.add_handler(help_handler)
	dp.add_handler(detalles_concurso_handler)
	dp.add_handler(CommandHandler('get_coincidence', get_coincidence))

	dp.add_handler(CommandHandler('get_database', update_databese))
	dp.add_handler(CommandHandler('get_info', get_info))
	dp.add_handler(CommandHandler('get_alluser', get_alluser))
	dp.add_handler(CommandHandler('send_message', my_send_message))
	dp.add_handler(CommandHandler('send_message_all', my_send_message_all))
	run(update)

main()
