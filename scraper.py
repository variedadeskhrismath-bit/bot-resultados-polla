import os
import requests
import json

# URL de tu base de datos Firebase
FIREBASE_URL = "https://polla-la-fortuna00-8bd4a-default-rtdb.firebaseio.com/polla_data"

def obtener_datos_firebase():
    """ Lee los datos actuales de la Polla desde Firebase """
    response = requests.get(f"{FIREBASE_URL}.json")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error al leer Firebase: {response.status_code}")
        return None

def guardar_participantes_firebase(participantes):
    """ Guarda la lista de participantes actualizada """
    url = f"{FIREBASE_URL}/participantes.json"
    response = requests.put(url, data=json.dumps(participantes))
    if response.status_code == 200:
        print("🏆 Tabla de posiciones reordenada exitosamente en Firebase.")
    else:
        print(f"Error al guardar en Firebase: {response.status_code}")

def ejecutar_recuento_aciertos():
    data = obtener_datos_firebase()
    if not data:
        print("No se encontraron datos en la base de datos.")
        return
    
    resultados = data.get('resultados', {})
    participantes = data.get('participantes', [])

    # Obtener lista de todos los animales/números que han salido
    ganadores = set()
    if isinstance(resultados, dict):
        for lot, horas in resultados.items():
            if isinstance(horas, dict):
                for h, num in horas.items():
                    if num and str(num).strip() != "":
                        ganadores.add(str(num).strip())

    # Recalcular aciertos de cada jugador
    if participantes and isinstance(participantes, list):
        for p in participantes:
            jugadas = p.get('jugadas', [])
            aciertos = sum(1 for j in jugadas if str(j).strip() in ganadores)
            p['aciertos'] = aciertos

        # Ordenar de mayor a menor aciertos
        participantes.sort(key=lambda x: x.get('aciertos', 0), reverse=True)

        # Guardar en Firebase
        guardar_participantes_firebase(participantes)
    else:
        print("No hay participantes registrados para calcular.")

if __name__ == "__main__":
    print("🚀 Iniciando ejecucion del bot Polla La Fortuna...")
    ejecutar_recuento_aciertos()

