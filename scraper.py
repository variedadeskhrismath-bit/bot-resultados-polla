import os
import requests
from bs4 import BeautifulSoup
import json

# URL de tu base de datos Firebase
FIREBASE_URL = "https://polla-la-fortuna00-8bd4a-default-rtdb.firebaseio.com/polla_data"

# Mapeo de loterías
LOTERIAS = {
    "LOTTO ACTIVO": "lotto-activo",
    "GRANJITA": "la-granjita",
    "SELVA PLUS": "selva-plus"
}

def obtener_datos_firebase():
    """ Lee los datos actuales de la Polla desde Firebase """
    response = requests.get(f"{FIREBASE_URL}.json")
    if response.status_code == 200:
        return response.json()
    return None

def guardar_resultados_firebase(resultados):
    """ Guarda los resultados extraídos en Firebase """
    url = f"{FIREBASE_URL}/resultados.json"
    requests.put(url, data=json.dumps(resultados))

def guardar_participantes_firebase(participantes):
    """ Guarda la lista de participantes reordenada """
    url = f"{FIREBASE_URL}/participantes.json"
    requests.put(url, data=json.dumps(participantes))

def extraer_resultados_web():
    """ Extrae los resultados del día desde loteriadehoy.com """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    nuevos_resultados = {}
    
    try:
        url = "https://loteriadehoy.com"
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar tarjetas o bloques de resultados
            # Extrae la información de números/animalitos publicados
            print("🌐 Lectura exitosa de Loteriadehoy.com")
        else:
            print(f"⚠️ Error al conectar a Loteriadehoy: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error durante la extracción web: {e}")
        
    return nuevos_resultados

def ejecutar_recuento_aciertos():
    data = obtener_datos_firebase()
    if not data:
        print("No se encontraron datos en Firebase.")
        return
    
    resultados = data.get('resultados', {})
    participantes = data.get('participantes', [])

    # Obtener lista de todos los animales/números ganadores registrados
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

        # Guardar tabla actualizada
        guardar_participantes_firebase(participantes)
        print("🏆 Tabla de posiciones reordenada exitosamente.")
    else:
        print("No hay participantes para calcular.")

if __name__ == "__main__":
    print("🚀 Iniciando ejecucion del bot Polla La Fortuna...")
    extraer_resultados_web()
    ejecutar_recuento_aciertos()

