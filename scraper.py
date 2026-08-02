import time
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, db

# CONEXIÓN A TU BASE DE DATOS
FIREBASE_DATABASE_URL = "https://polla-la-fortuna00-8bd4a-default-rtdb.firebaseio.com"

if not firebase_admin._apps:
    cred = credentials.Anonymous()
    firebase_admin.initialize_app(options={
        'databaseURL': FIREBASE_DATABASE_URL
    })

ref_polla = db.reference('polla_data')

def ejecutar_recuento_aciertos():
    data = ref_polla.get()
    if not data:
        return
    
    resultados = data.get('resultados', {})
    participantes = data.get('participantes', [])

    ganadores = set()
    for lot, horas in resultados.items():
        for h, num in horas.items():
            if num and str(num).strip() != "":
                ganadores.add(str(num).strip())

    if participantes:
        for p in participantes:
            jugadas = p.get('jugadas', [])
            aciertos = sum(1 for j in jugadas if str(j).strip() in ganadores)
            p['aciertos'] = aciertos

        participantes.sort(key=lambda x: x.get('aciertos', 0), reverse=True)
        db.reference('polla_data/participantes').set(participantes)
        print("🏆 Tabla de posiciones reordenada automáticamente.")

if __name__ == "__main__":
    print("🚀 Iniciando proceso automático...")
    ejecutar_recuento_aciertos()

