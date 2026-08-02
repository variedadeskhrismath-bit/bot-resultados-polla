import time
import requests
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

FIREBASE_URL = "https://polla-la-fortuna00-8bd4a-default-rtdb.firebaseio.com/polla_data"

def guardar_participante_firebase(nombre, telefono, jugadas):
    """ Agrega un nuevo participante a la lista en Firebase """
    try:
        # 1. Obtener participantes actuales
        res = requests.get(f"{FIREBASE_URL}/participantes.json")
        participantes = res.json() if res.status_code == 200 and res.json() else []
        
        # Si Firebase devuelve un dict en lugar de lista, lo adaptamos
        if isinstance(participantes, dict):
            participantes = list(participantes.values())

        # 2. Crear el nuevo registro
        nuevo_jugador = {
            "nombre": nombre,
            "telefono": telefono,
            "jugadas": jugadas, # Lista de números/animalitos (ej: ["01", "12", "05"])
            "aciertos": 0
        }

        participantes.append(nuevo_jugador)

        # 3. Guardar en Firebase
        requests.put(f"{FIREBASE_URL}/participantes.json", data=json.dumps(participantes))
        return True
    except Exception as e:
        print(f"❌ Error guardando participante: {e}")
        return False

@app.route("/webhook", methods=["POST"])
def webhook():
    """ Recibe las alertas de mensajes desde el conector de WhatsApp """
    data = request.json
    
    if not data:
        return jsonify({"status": "no data"}), 400

    # Extraer el mensaje y remitente
    mensaje = data.get("message", "").strip()
    remitente = data.get("from", "") # Número de teléfono
    
    print(f"📩 Mensaje recibido de {remitente}: {mensaje}")

    # Lógica básica de respuesta
    if mensaje.lower() in ["hola", "buenas", "inicio", "menu"]:
        respuesta = (
            "🤖 *¡Bienvenido a Polla La Fortuna!* 🍀\n\n"
            "Para registrar tu jugada, envía tu mensaje con el siguiente formato:\n\n"
            "*REGISTRO* / Tu Nombre / Tus 10 Animalitos o Números separados por coma.\n\n"
            "📌 *Ejemplo:*\n"
            "REGISTRO / Maria Perez / 01, 05, 12, 18, 20, 22, 25, 30, 33, 36"
        )
        return jsonify({"reply": respuesta})

    elif mensaje.upper().startswith("REGISTRO"):
        try:
            partes = mensaje.split("/")
            if len(partes) >= 3:
                nombre = partes[1].strip()
                jugadas_raw = partes[2].strip().split(",")
                jugadas = [j.strip() for j in jugadas_raw if j.strip()]

                if len(jugadas) > 0:
                    exito = guardar_participante_firebase(nombre, remitente, jugadas)
                    if exito:
                        respuesta = (
                            f"✅ *¡Registro Exitoso, {nombre}!*\n\n"
                            f"🎮 *Jugadas:* {', '.join(jugadas)}\n"
                            f"📊 Ya puedes consultar tu posición en vivo en la página web."
                        )
                    else:
                        respuesta = "⚠️ Hubo un detalle guardando tu jugada. Intenta de nuevo en unos minutos."
                else:
                    respuesta = "⚠️ Debes incluir tus números o animalitos de jugada."
            else:
                respuesta = "⚠️ Formato incorrecto. Recuerda usar: *REGISTRO / Nombre / Números*"
        except Exception as e:
            respuesta = "⚠️ Ocurrió un error al procesar tu registro."

        return jsonify({"reply": respuesta})

    return jsonify({"status": "ignored"})

if __name__ == "__main__":
    # Servidor local para recibir peticiones
    app.run(host="0.0.0.0", port=5000)

