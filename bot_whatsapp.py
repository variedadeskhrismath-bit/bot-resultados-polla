import json
import os
import time
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

FIREBASE_URL = (
    "https://polla-la-fortuna00-8bd4a-default-rtdb.firebaseio.com/polla_data"
)


# --- FUNCIÓN PARA ENVIAR MENSAJES A TRAVÉS DE ULTRAMSG ---
def enviar_ultramsg(destino, texto):
  """Envía un mensaje a un chat privado o a un GRUPO de WhatsApp."""
  instance_id = os.getenv("ULTRAMSG_INSTANCE", "instance187157")
  token = os.getenv("ULTRAMSG_TOKEN", "TU_TOKEN_AQUI")

  url = f"https://api.ultramsg.com/{instance_id}/messages/chat"
  payload = {"token": token, "to": destino, "body": texto}
  headers = {"content-type": "application/x-www-form-urlencoded"}

  try:
    response = requests.post(url, data=payload, headers=headers)
    print(f"📩 Respuesta API UltraMsg: {response.text}")
    return response.json()
  except Exception as e:
    print(f"❌ Error enviando a UltraMsg: {e}")
    return None


def guardar_participante_firebase(nombre, telefono, jugadas):
  """Agrega un nuevo participante a la lista en Firebase."""
  try:
    # 1. Obtener participantes actuales
    res = requests.get(f"{FIREBASE_URL}/participantes.json")
    participantes = (
        res.json() if res.status_code == 200 and res.json() else []
    )

    if isinstance(participantes, dict):
      participantes = list(participantes.values())

    # 2. Crear el nuevo registro
    nuevo_jugador = {
        "nombre": nombre,
        "telefono": telefono,
        "jugadas": jugadas,  # Lista de números/animalitos
        "aciertos": 0,
    }

    participantes.append(nuevo_jugador)

    # 3. Guardar en Firebase
    requests.put(
        f"{FIREBASE_URL}/participantes.json", data=json.dumps(participantes)
    )
    return True
  except Exception as e:
    print(f"❌ Error guardando participante en Firebase: {e}")
    return False


@app.route("/webhook", methods=["POST"])
def webhook():
  """Recibe las alertas de mensajes desde UltraMsg (Grupos y Chats)."""
  data = request.json

  if not data:
    return jsonify({"status": "no data"}), 400

  data_payload = data.get("data", data)

  # Ignorar mensajes enviados por el propio bot para evitar bucles infinitos
  if data_payload.get("fromMe") is True:
    return jsonify({"status": "ignored self message"}), 200

  mensaje = data_payload.get("body", "").strip()

  # 'chat_id' es el ID del Grupo o Chat (a donde responderá el bot)
  chat_id = data_payload.get("from", "")

  # 'remitente_real' es el número exacto del usuario dentro del grupo
  remitente_real = data_payload.get("author", data_payload.get("from", ""))

  print(
      f"📩 Mensaje recibido en {chat_id} de {remitente_real}:"
      f" {mensaje}"
  )

  if not mensaje or not chat_id:
    return jsonify({"status": "ignored"}), 200

  # --- LÓGICA DE RESPUESTA Y REGISTRO ---

  # 1. Comando Hola / Menu
  if mensaje.lower() in ["hola", "buenas", "inicio", "menu"]:
    respuesta = (
        "🤖 *¡Bienvenido a Polla La Fortuna!* 🍀\n\n"
        "Para registrar tu jugada en este grupo, envía un mensaje con el"
        " siguiente formato:\n\n"
        "*REGISTRO* / Tu Nombre / Tus 10 Animalitos o Números separados por"
        " coma.\n\n"
        "📌 *Ejemplo:*\n"
        '"REGISTRO / Maria Perez / 01, 05, 12, 18, 20, 22, 25, 30, 33, 36"'
    )
    enviar_ultramsg(chat_id, respuesta)
    return jsonify({"status": "success"}), 200

  # 2. Comando REGISTRO
  elif mensaje.upper().startswith("REGISTRO"):
    try:
      partes = mensaje.split("/")
      if len(partes) >= 3:
        nombre = partes[1].strip()
        jugadas_raw = partes[2].strip().split(",")
        jugadas = [j.strip() for j in jugadas_raw if j.strip()]

        if len(jugadas) > 0:
          # Guardamos en Firebase usando el número real del participante
          exito = guardar_participante_firebase(
              nombre, remitente_real, jugadas
          )
          if exito:
            respuesta = (
                f"✅ *¡Registro Exitoso, {nombre}!*\n\n"
                f"🎮 *Jugadas registradas:* {', '.join(jugadas)}\n"
                "📊 Ya puedes consultar la tabla general en la página web."
            )
          else:
            respuesta = (
                "⚠️ Hubo un detalle guardando tu jugada en el sistema. Intenta"
                " de nuevo."
            )
        else:
          respuesta = (
              "⚠️ Debes incluir tus números o animalitos de jugada."
          )
      else:
        respuesta = (
            "⚠️ Formato incorrecto. Usa: *REGISTRO / Nombre / Números*"
        )
    except Exception as e:
      respuesta = "⚠️ Ocurrió un error al procesar tu registro."

    enviar_ultramsg(chat_id, respuesta)
    return jsonify({"status": "success"}), 200

  return jsonify({"status": "ignored"}), 200


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)

