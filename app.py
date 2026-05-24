import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telethon import TelegramClient, events
import asyncio
import os
import threading
import re
# --- LIBRERÍAS PARA EL SERVIDOR WEB FALSO (REQUERIDO POR RENDER) ---
from http.server import BaseHTTPRequestHandler, HTTPServer

# 🌐 Servidor web falso para simular tráfico continuo e impedir la suspensión de Render
# 🌐 Servidor web falso modificado para soportar peticiones HEAD y GET de UptimeRobot
class FakeServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("Sistema Multimotor Activo 🚀\nMonitoreo en línea.".encode("utf-8"))

    def do_HEAD(self):
        # Responde con éxito (200) a las verificaciones rápidas de cabeceras
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()

def iniciar_servidor_falso():
    # Render asigna dinámicamente un puerto en la variable de entorno PORT
    puerto = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', puerto), FakeServer)
    print(f"📡 Servidor de simulación escuchando en el puerto {puerto}")
    server.serve_forever()

# Lanzamos el servidor falso en un hilo en segundo plano antes de iniciar los bots
threading.Thread(target=iniciar_servidor_falso, daemon=True).start()


# --- TUS LLAVES CONFIGURADAS ---
API_ID = 35589986  
API_HASH = '245c358257a1df9097378c9673b471df'  
BOT_TOKEN = '8980070175:AAGHcydC2FcIXxGaEtC_gDszo-OVFkHectk'  

# 🔍 PALABRAS CLAVE PARA ENCONTRAR LOS GRUPOS TRADICIONALES
TXT_FRANCHESCO = "FRANCHESCO"
TXT_DF_VIP     = "DF VIP"

# 🤖 USERNAMES PARA LOS BOTS DIRECTOS CHAT UNO A UNO
USER_NORTH_BOT = "northdatabasicbot"
USER_LIAM_BOT  = "Yinwodataa_bot"  

bot = telebot.TeleBot(BOT_TOKEN)
client = TelegramClient('sesion_hugo', API_ID, API_HASH)

chat_id_hugo = None
loop_principal = None  

# Entidades de Telegram
entidad_franchesco = None
entidad_df_vip     = None
entidad_north_bot  = None  
entidad_liam_bot   = None

# 🗝️ ID NUMÉRICOS INMUTABLES DE LA SESIÓN
id_franchesco = None
id_df_vip     = None
id_north_bot  = None
id_liam_bot   = None

# 📋 CONTROL DE ESTADOS INDEPENDIENTES (Estructuras de datos dinámicas)
control_operaciones = {}
north_respondido_exito = {} 
imagenes_procesadas_recientes = []  # 🔥 Candado absoluto para segundos mensajes/publicidad

# --- FUNCIÓN INTERNA: MAPEO Y EXTRACCIÓN DE IDS REALES ---
async def mapear_motores_por_id():
    global entidad_franchesco, entidad_df_vip, entidad_north_bot, entidad_liam_bot
    global id_franchesco, id_df_vip, id_north_bot, id_liam_bot
    
    await client.start()
    print("📋 Sincronizando e indexando IDs reales de Telegram...")
    
    GRUPOS_A_OBVIAR = ["CANAL FRANCHESCO DATA SAC", "FRANCHESCO MASTER", "DF VIP [ GRUPO 09 ]"]
    
    async for dialog in client.iter_dialogs(limit=150):
        if dialog.name:
            nombre_chat = dialog.name.upper().strip()
            if any(obviar.upper() in nombre_chat for obviar in GRUPOS_A_OBVIAR):
                continue
            
            if TXT_FRANCHESCO in nombre_chat and not entidad_franchesco:
                entidad_franchesco = dialog.input_entity
                id_franchesco = dialog.id
                print(f"🎯 ID Franchesco Fijado: {id_franchesco} ({dialog.name})")
            elif TXT_DF_VIP in nombre_chat and not entidad_df_vip:
                entidad_df_vip = dialog.input_entity
                id_df_vip = dialog.id
                print(f"🎯 ID DF VIP Fijado: {id_df_vip} ({dialog.name})")

    try:
        entidad_north_bot = await client.get_input_entity(USER_NORTH_BOT)
        full_north = await client.get_entity(entidad_north_bot)
        id_north_bot = full_north.id
        print(f"🎯 ID North Bot Fijado: {id_north_bot} (@{USER_NORTH_BOT})")
    except Exception as e:
        print(f"⚠️ Alerta North Bot: {e}")

    try:
        entidad_liam_bot = await client.get_input_entity(USER_LIAM_BOT)
        full_liam = await client.get_entity(entidad_liam_bot)
        id_liam_bot = full_liam.id
        print(f"🎯 ID Liam Bot Fijado: {id_liam_bot} (@{USER_LIAM_BOT})")
    except Exception as e:
        print(f"⚠️ Alerta Liam: {e}")

# --- COLA DE REINTENTO CONDICIONAL PARA NORTH DATA (EXCLUSIVO /TIVE) ---
async def flujo_especial_north(placa, clave_operacion):
    global entidad_north_bot, north_respondido_exito, control_operaciones
    if not entidad_north_bot: return
    
    north_respondido_exito[clave_operacion] = False
    
    print(f"⏱️ [NORTH DATA] Enviando primer intento /tiv {placa} para {clave_operacion}")
    try:
        await client.send_message(entidad_north_bot, f"/tiv {placa}")
    except Exception as e: 
        print(f"❌ Error al enviar a North: {e}")
    
    await asyncio.sleep(30)
    
    if north_respondido_exito.get(clave_operacion) == True:
        print(f"✅ [NORTH DATA] PDF recibido a tiempo para {clave_operacion}. Reintento cancelado.")
        return

    if clave_operacion in control_operaciones:
        print(f"🔄 [NORTH DATA] Sin PDF en 30s. Reintentando con /tive {placa}")
        try:
            await client.send_message(entidad_north_bot, f"/tive {placa}")
        except Exception as e: 
            print(f"❌ Error en reintento a North: {e}")

# --- LIBERADOR ABSOLUTO DE MEMORIA POR OPERACIÓN ---
def liberar_operacion_de_memoria(clave_operacion):
    global control_operaciones, north_respondido_exito
    if clave_operacion in control_operaciones:
        msg_carga = control_operaciones[clave_operacion].get("msg_carga")
        if msg_carga:
            try:
                bot.delete_message(msg_carga.chat.id, msg_carga.message_id)
            except: pass
        
        del control_operaciones[clave_operacion]
        print(f"🧹 [MEMORIA] Operación [{clave_operacion}] liberada de forma aislada.")
    
    if clave_operacion in north_respondido_exito: 
        del north_respondido_exito[clave_operacion]


# --- TIME-OUT LARGO DE RESPALDO (Optimizado a 90s) ---
async def timeout_seguridad_operacion(clave_operacion, segundos=90):
    await asyncio.sleep(segundos)
    global control_operaciones
    if clave_operacion in control_operaciones:
        print(f"⏱️ [TIME-OUT] Forzando liberación de [{clave_operacion}] por inactividad ({segundos}s).")
        liberar_operacion_de_memoria(clave_operacion)

# --- VERIFICADOR INTERNO DE COBERTURA ---
def verificar_y_marcar_respuesta(clave_operacion, motor):
    global control_operaciones
    if clave_operacion not in control_operaciones:
        return
    
    if motor in control_operaciones[clave_operacion]["motores"]:
        control_operaciones[clave_operacion]["motores"][motor] = True
        print(f"📊 [PROGRESO {clave_operacion}]: {motor} -> ✅ REGISTRADO.")
    
    if all(control_operaciones[clave_operacion]["motores"].values()):
        liberar_operacion_de_memoria(clave_operacion)


# =====================================================================
# --- 🔥 SECCIÓN DE COMANDOS INDEPENDIENTES ---
# =====================================================================

# 1️⃣ COMANDO: /partidav (Exclusivo DF VIP)
@bot.message_handler(commands=['partidav'])
def recibir_orden_docs(message):
    global chat_id_hugo, entidad_df_vip, loop_principal, control_operaciones
    chat_id_hugo = message.chat.id  
    texto = message.text.split()
    if len(texto) < 2: return
    placa = texto[1].upper().strip()
    
    clave_operacion = f"{placa}_PARTIDAV"
    
    if entidad_df_vip:
        msg_carga = bot.reply_to(message, f"🔍 Consultando PDF para {placa} en DF VIP...")
        
        control_operaciones[clave_operacion] = {
            "placa": placa,
            "origen": "PARTIDAV",
            "msg_carga": msg_carga,
            "motores": {"DF VIP": False}
        }
        
        if loop_principal:
            asyncio.run_coroutine_threadsafe(client.send_message(entidad_df_vip, f"/PARTIDAV {placa}"), loop_principal)
            asyncio.run_coroutine_threadsafe(timeout_seguridad_operacion(clave_operacion, 90), loop_principal)


# 2️⃣ COMANDO: /placa (Exclusivo FRANCHESCO Reenvío Directo)
@bot.message_handler(commands=['placa'])
def recibir_orden_imagenes(message):
    global chat_id_hugo, entidad_franchesco, loop_principal, control_operaciones
    chat_id_hugo = message.chat.id  
    texto = message.text.split()
    if len(texto) < 2: return
    placa = texto[1].upper().strip()
    
    clave_operacion = f"{placa}_PLACA"
    
    if entidad_franchesco:
        msg_carga = bot.reply_to(message, f"📸 Consultando en FRANCHESCO para {placa}...")
        
        control_operaciones[clave_operacion] = {
            "placa": placa,
            "origen": "PLACA",
            "msg_carga": msg_carga,
            "motores": {"FRANCHESCO": False}
        }
        
        if loop_principal:
            asyncio.run_coroutine_threadsafe(client.send_message(entidad_franchesco, f"/pla {placa}"), loop_principal)
            asyncio.run_coroutine_threadsafe(timeout_seguridad_operacion(clave_operacion, 90), loop_principal)


# 3️⃣ COMANDO: /tive (Ráfaga Colectiva Total)
@bot.message_handler(commands=['tive'])
def recibir_orden_tive_global(message):
    global chat_id_hugo, loop_principal, control_operaciones
    global entidad_df_vip, entidad_franchesco, entidad_north_bot, entidad_liam_bot
    
    chat_id_hugo = message.chat.id  
    texto = message.text.split()
    if len(texto) < 2:
        bot.reply_to(message, "❌ Envia la placa. Ejemplo: /tive CAJ270")
        return
        
    placa = texto[1].upper().strip()
    clave_operacion = f"{placa}_TIVE"
    
    msg_carga = bot.reply_to(message, f"⚡ ¡Ráfaga /tive activada para {placa}!\nDisparando consultas a todos los proveedores...")

    if not loop_principal: return
    
    control_operaciones[clave_operacion] = {
        "placa": placa,
        "origen": "TIVE",
        "msg_carga": msg_carga,
        "motores": {
            "DF VIP": False,
            "FRANCHESCO": False,
            "NORTH DATA": False,
            "LIAM DATA": False
        }
    }

    if entidad_franchesco:
        asyncio.run_coroutine_threadsafe(client.send_message(entidad_franchesco, f"/tive {placa}"), loop_principal)
    if entidad_df_vip:
        asyncio.run_coroutine_threadsafe(client.send_message(entidad_df_vip, f"/tive {placa}"), loop_principal)
    if entidad_north_bot:
        asyncio.run_coroutine_threadsafe(flujo_especial_north(placa, clave_operacion), loop_principal)
    if entidad_liam_bot:
        asyncio.run_coroutine_threadsafe(client.send_message(entidad_liam_bot, f"/tive {placa}"), loop_principal)

    asyncio.run_coroutine_threadsafe(timeout_seguridad_operacion(clave_operacion, 90), loop_principal)


# 4️⃣ COMANDO: /boleta (Ráfaga para Boletas Informativas - Protegido contra Timeouts)
@bot.message_handler(commands=['boleta'])
def recibir_orden_boleta_global(message):
    global chat_id_hugo, loop_principal, control_operaciones
    global entidad_df_vip, entidad_franchesco, entidad_north_bot, entidad_liam_bot
    
    chat_id_hugo = message.chat.id  
    texto = message.text.split()
    if len(texto) < 2:
        bot.reply_to(message, "❌ Envía la placa. Ejemplo: /boleta CAJ270")
        return
        
    placa = texto[1].upper().strip()
    clave_operacion = f"{placa}_BOLETA" 
    
    msg_carga = None
    try:
        msg_carga = bot.reply_to(message, f"🧾 ¡Ráfaga /boleta activada para {placa}!\nDisparando consultas de boletas informativas...")
    except Exception as network_error:
        print(f"⚠️ Aviso: Retardo en la red al enviar mensaje de carga: {network_error}")

    if not loop_principal: return
    
    control_operaciones[clave_operacion] = {
        "placa": placa,
        "origen": "BOLETA", 
        "msg_carga": msg_carga,
        "motores": {
            "DF VIP": False,
            "FRANCHESCO": False,
            "NORTH DATA": False,
            "LIAM DATA": False
        }
    }

    if entidad_franchesco:
        asyncio.run_coroutine_threadsafe(client.send_message(entidad_franchesco, f"/boi {placa}"), loop_principal)
    if entidad_df_vip:
        asyncio.run_coroutine_threadsafe(client.send_message(entidad_df_vip, f"/boi {placa}"), loop_principal)
    if entidad_liam_bot:
        asyncio.run_coroutine_threadsafe(client.send_message(entidad_liam_bot, f"/bolif {placa}"), loop_principal)
    if entidad_north_bot:
        asyncio.run_coroutine_threadsafe(client.send_message(entidad_north_bot, f"/bolinf {placa}"), loop_principal)

    asyncio.run_coroutine_threadsafe(timeout_seguridad_operacion(clave_operacion, 90), loop_principal)

# =====================================================================

# --- 🎛️ PANEL INTERACTIVO ---
@bot.message_handler(commands=['cmds', 'help', 'menu'])
def enviar_panel_comandos(message):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🆔 RENIEC", callback_data="menu_reniec"),
        InlineKeyboardButton("📞 TELEFONIA", callback_data="menu_telef"),
        InlineKeyboardButton("🏢 SUNAT", callback_data="menu_sunat"),
        InlineKeyboardButton("🏠 SUNARP", callback_data="menu_sunarp"),
        InlineKeyboardButton("🚙 VEHICULOS", callback_data="menu_vehiculos"),
        InlineKeyboardButton("💎 VIP", callback_data="menu_vip")
    )
    texto_bienvenida = (
        f"Hola, *{message.from_user.first_name}*\n\n"
        "🎛️ **[ PANEL DE COMANDOS ]**\n"
        "Selecciona una opción según la categoría que deseas explorar."
    )
    bot.send_message(message.chat.id, texto_bienvenida, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def responder_clicks_botones(call):
    if call.data == "menu_vehiculos":
        markup_vehiculos = InlineKeyboardMarkup()
        btn_regresar = InlineKeyboardButton("⬅️ Volver al Menú", callback_data="volver_principal")
        markup_vehiculos.add(btn_regresar)
        
        texto_vehiculos = (
            "📋 **[ CATEGORÍA ⇒ VEHÍCULOS ]**\n\n"
            "1️⃣ **CONSULTA PDF ORIGINAL (DF VIP)**\n"
            "• Comando: `/partidav` `[placa]` \n\n"
            "2️⃣ **CONSULTA IMAGEN (FRANCHESCO)**\n"
            "• Comando: `/placa` `[placa]` \n"
            "• Ejemplo: `/placa CAJ270` \n\n"
            "3️⃣ **RÁFAGA MULTIDISPARO TOTAL (TIVE)**\n"
            "• Comando: `/tive` `[placa]` \n\n"
            "4️⃣ **RÁFAGA BOLETAS INFORMATIVAS (BOLETA)**\n"
            "• Comando: `/boleta` `[placa]`"
        )
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=texto_vehiculos, parse_mode="Markdown", reply_markup=markup_vehiculos)
    elif call.data == "volver_principal":
        pass

def arrancar_bot_padre():
    bot.infinity_polling(timeout=60, long_polling_timeout=60, logger_level=50)

# --- FUNCIÓN PRINCIPAL ASÍNCRONA ---
async def main():
    global loop_principal, control_operaciones, north_respondido_exito
    global id_franchesco, id_df_vip, id_north_bot, id_liam_bot
    loop_principal = asyncio.get_running_loop()
    
    await mapear_motores_por_id()
    
    @client.on(events.NewMessage())
    async def escuchador_global_mensajes(event):
        global chat_id_hugo, control_operaciones, north_respondido_exito
        global id_franchesco, id_df_vip, id_north_bot, id_liam_bot
        
        chat_actual_id = event.chat_id
        if not chat_id_hugo or not control_operaciones:
            return

        origen_texto = "DESCONOCIDO"
        
        if id_franchesco and chat_actual_id == id_franchesco: origen_texto = "FRANCHESCO"
        elif id_df_vip and chat_actual_id == id_df_vip: origen_texto = "DF VIP"
        elif id_north_bot and chat_actual_id == id_north_bot: origen_texto = "NORTH DATA"
        elif id_liam_bot and chat_actual_id == id_liam_bot: origen_texto = "LIAM DATA"

        if origen_texto == "DESCONOCIDO": return

        op_encontrada = None
        placa_detectada = None
        
        texto_a_buscar = ""
        if event.message.text:
            texto_a_buscar = event.message.text.upper()
        if event.message.media and event.message.document:
            for attr in event.message.document.attributes:
                if hasattr(attr, 'file_name') and attr.file_name:
                    texto_a_buscar += " " + attr.file_name.upper()

        for clave, op_data in list(control_operaciones.items()):
            if op_data["placa"] in texto_a_buscar.replace("-", "").replace("_", "").replace(" ", ""):
                if origen_texto in op_data["motores"]:
                    op_encontrada = clave
                    placa_detectada = op_data["placa"]
                    break

        if not op_encontrada:
            for clave, op_data in list(control_operaciones.items()):
                if origen_texto in op_data["motores"] and not op_data["motores"][origen_texto]:
                    if origen_texto == "NORTH DATA" or origen_texto == "LIAM DATA":
                        if op_data["origen"] in ["TIVE", "BOLETA"]: 
                            op_encontrada = clave
                            placa_detectada = op_data["placa"]
                            break
                    elif origen_texto == "DF VIP" and op_data["origen"] == "PARTIDAV":
                        op_encontrada = clave
                        placa_detectada = op_data["placa"]
                        break
                    elif origen_texto == "FRANCHESCO":
                        if op_data["origen"] in ["PLACA", "TIVE", "BOLETA"]:
                            op_encontrada = clave
                            placa_detectada = op_data["placa"]
                            break

        if not op_encontrada: 
            return

        # 📥 CASO 1: DOCUMENTO PDF
        if event.message.media and event.message.document:
            nombre_original = "documento.pdf"
            for attr in event.message.document.attributes:
                if hasattr(attr, 'file_name') and attr.file_name:
                    nombre_original = attr.file_name
                    break
            
            if origen_texto == "NORTH DATA": 
                north_respondido_exito[op_encontrada] = True
                
            ruta = await event.message.download_media(file=nombre_original)
            caption_personalizado = f"📄 **Resultado ({origen_texto})**\n🏁 Placa/Partida: `{placa_detectada}`"
            
            with open(ruta, 'rb') as doc:
                bot.send_document(chat_id_hugo, doc, caption=caption_personalizado, parse_mode="Markdown")
            
            if os.path.exists(ruta):
                try: os.remove(ruta)
                except: pass
                
            verificar_y_marcar_respuesta(op_encontrada, origen_texto)
            return

        # 📸 CASO 2: FOTOS
        elif event.message.media and event.message.photo and origen_texto == "FRANCHESCO":
            comando_origen = control_operaciones[op_encontrada]["origen"]
            
            if comando_origen in ["TIVE", "BOLETA"]:
                print(f"🤫 Imagen publicitaria/secundaria omitida en ráfaga /{comando_origen.lower()} para {placa_detectada}.")
                verificar_y_marcar_respuesta(op_encontrada, "FRANCHESCO")
                return

            caption_proveedor = event.message.message if event.message.message else ""

            if "ESTAMOS PROCESANDO" in caption_proveedor.upper() or "UN MOMENTO POR FAVOR" in caption_proveedor.upper():
                print(f"⏳ [PROCESANDO] Franchesco mostró su pantalla de carga para {placa_detectada}. Esperando el reporte real...")
                return

            if placa_detectada in imagenes_procesadas_recientes:
                print(f"🛑 [FILTRADO] Mensaje duplicado omitido para {placa_detectada}.")
                return

            print(f"📸 ¡Reporte final detectado para {placa_detectada}! Eliminando carga y reenviando...")
            ruta_img = await event.message.download_media(file=f"{placa_detectada}.jpg")
            
            try:
                if "ESTADO DE CUENTA" in caption_proveedor.upper():
                    partes = re.split(r'(?i)\[⚡\]\s*ESTADO DE CUENTA|ESTADO DE CUENTA', caption_proveedor)
                    caption_proveedor = partes[0].strip()
                
                caption_final = f"📸 **Reporte de [{origen_texto}]:**\n\n{caption_proveedor}"

                msg_carga = control_operaciones[op_encontrada].get("msg_carga")
                if msg_carga:
                    try:
                        bot.delete_message(msg_carga.chat.id, msg_carga.message_id)
                        print(f"🗑️ [CARGA ELIMINADA] Mensaje de espera borrado para {placa_detectada}.")
                    except Exception as e:
                        print(f"⚠️ No se pudo borrar el mensaje de carga: {e}")

                with open(ruta_img, 'rb') as foto_enviar:
                    bot.send_photo(chat_id_hugo, foto_enviar, caption=caption_final)
                print(f"✅ [ÉXITO] Reporte final entregado en espejo para {placa_detectada}")
                
                imagenes_procesadas_recientes.append(placa_detectada)
                
            except Exception as e:
                print(f"❌ Error en el flujo de réplica: {e}")
            
            verificar_y_marcar_respuesta(op_encontrada, "FRANCHESCO")
            if os.path.exists(ruta_img):
                try: os.remove(ruta_img)
                except: pass
            return

        # 🛑 CASO 3: RESPUESTA ES TEXTO PLANO
        elif event.message.text:
            texto_grupo = event.message.text.upper()
            
            if texto_grupo.startswith(('/TIVE', '/TIV', '/PLA', '/PARTI', '/BOI', '/BOLI', '/BOLETA')) and len(texto_grupo) < 15 and not "NO SE" in texto_grupo: 
                return

            if texto_grupo.strip() == "CMDS" or (texto_grupo.startswith('/') and len(texto_grupo) < 7): return

            if origen_texto == "FRANCHESCO" and "ANTI-SPAM ACTIVADO" in texto_grupo:
                print(f"⚠️ [FRANCHESCO] Detectado Anti-Spam activo para la operación {op_encontrada}.")
                bot.send_message(chat_id_hugo, f"⏳ **Alerta [{origen_texto}]:**\n\n⚠️ Tienes el Anti-Spam activado en este proveedor. Espera unos segundos.")
                verificar_y_marcar_respuesta(op_encontrada, "FRANCHESCO")
                return

            palabras_carga = [
                "BUSCANDO", "PROCESANDO", "ESPERE", "CONSULTANDO", "RECIBIDO", 
                "UN MOMENTO", "BUSQUEDA ACTIVADA", "SOLICITUD RECIBIDA", "CRÉDITOS RESTANTES",
                "OBTENIENDO LA TIVE", "OBTENIENDO", "𝐄𝐬𝐭𝐚𝐦𝐨𝐬 𝐩𝐫𝐨𝐜𝐞𝐬𝐚𝐧𝐝𝐨", "𝐔𝐧 𝐦ο𝐦𝐞𝐧𝐭ο"
            ]
            if any(carga in texto_grupo for carga in palabras_carga): return

            comando_origen = control_operaciones[op_encontrada]["origen"]
            
            if origen_texto == "FRANCHESCO":
                if "NO SE ENCONTRÓ" in texto_grupo or "NO SE ENCONTRO" in texto_grupo or "ERROR" in texto_grupo:
                    print(f"❌ [FRANCHESCO] Reportó error en texto plano para {placa_detectada}.")
                    
                    if comando_origen == "PLACA":
                        msg_carga = control_operaciones[op_encontrada].get("msg_carga")
                        if msg_carga:
                            try: bot.delete_message(msg_carga.chat.id, msg_carga.message_id)
                            except: pass

                    bot.send_message(chat_id_hugo, f"📢 **Respuesta de [{origen_texto}]:**\n🏁 Placa/Partida: `{placa_detectada}`\n\n❌ No se encontró información para los datos ingresados.")
                    verificar_y_marcar_respuesta(op_encontrada, origen_texto)
                    return

            if origen_texto == "DF VIP":
                es_error_df = "NO SE ENCONTRÓ" in texto_grupo or "NO SE ENCONTRO" in texto_grupo or "ERROR" in texto_grupo or "NO EXISTE" in texto_grupo
                
                if es_error_df:
                    print(f"❌ [DF VIP] Reportó error para la placa {placa_detectada}.")
                    if comando_origen == "PARTIDAV":
                        msg_carga = control_operaciones[op_encontrada].get("msg_carga")
                        if msg_carga:
                            try: bot.delete_message(msg_carga.chat.id, msg_carga.message_id)
                            except: pass
                    
                    bot.send_message(chat_id_hugo, f"⚠️ **Resultado [{origen_texto}]:**\n🏁 Placa: `{placa_detectada}`\n\n❌ No se encontró información o partida registrada.")
                    verificar_y_marcar_respuesta(op_encontrada, origen_texto)
                    return
                elif comando_origen == "PARTIDAV":
                    print(f"🤫 Texto plano intermedio de DF VIP ignorado para {placa_detectada}. Esperando el PDF original...")
                    return

            if origen_texto == "NORTH DATA":
                es_error_north = (
                    "NO SE HAN ENCONTRADO DATOS" in texto_grupo or 
                    "NOT FOUND DATA" in texto_grupo or 
                    "NO SE ENCONTRÓ" in texto_grupo or
                    "NO SE ENCONTRO" in texto_grupo or
                    "NO SE HALLARON" in texto_grupo or
                    "ERROR" in texto_grupo or 
                    "NO EXISTE" in texto_grupo
                )
                
                if es_error_north:
                    print(f"❌ [NORTH DATA] Reportó falta de datos para {placa_detectada}. Reenviando alerta...")
                    
                    texto_original = event.message.text
                    lineas = texto_original.split('\n')
                    lineas_limpias = []
                    for linea in lineas:
                        if "CONSULTADO POR" in linea.upper() or "CREDITOS" in linea.upper(): break
                        lineas_limpias.append(linea)
                    reporte_recortado = "\n".join(lineas_limpias).strip()
                    if not reporte_recortado: reporte_recortado = texto_original.strip()
                    
                    bot.send_message(chat_id_hugo, f"📢 **Respuesta de [{origen_texto}]:**\n🏁 Placa/Partida: `{placa_detectada}`\n\n{reporte_recortado}")
                    
                    if comando_origen == "TIVE" and not north_respondido_exito.get(op_encontrada):
                        print(f"⏱️ [NORTH DATA] Primer intento fallido en ráfaga /tive. Manteniendo operación viva para el reintento...")
                    else:
                        verificar_y_marcar_respuesta(op_encontrada, origen_texto)
                    return
                else:
                    print(f"🤫 Texto intermedio de North Data recibido para {placa_detectada}. Esperando...")
                    return

            texto_original = event.message.text
            lineas = texto_original.split('\n')
            lineas_limpias = []
            for linea in lineas:
                if "CONSULTADO POR" in linea.upper() or "CREDITOS" in linea.upper(): break
                lineas_limpias.append(linea)
            reporte_recortado = "\n".join(lineas_limpias).strip()
            if not reporte_recortado: reporte_recortado = texto_original.strip()

            bot.send_message(chat_id_hugo, f"📢 **Respuesta de [{origen_texto}]:**\n🏁 Placa/Partida: `{placa_detectada}`\n\n{reporte_recortado}")
            verificar_y_marcar_respuesta(op_encontrada, origen_texto)

    print("🚀 [SISTEMA ULTRA-ESTABLE ONLINE] Extracción prioritaria activa sin OCR.")
    await client.run_until_disconnected()

if __name__ == '__main__':
    print("Iniciando sistema multimotor seguro...")
    threading.Thread(target=arrancar_bot_padre, daemon=True).start()
    asyncio.run(main())