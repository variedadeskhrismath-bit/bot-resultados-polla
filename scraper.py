import json
from bs4 import BeautifulSoup
import requests

FIREBASE_URL = (
    "https://polla-la-fortuna00-8bd4a-default-rtdb.firebaseio.com/polla_data"
)


def ejecutar_scraper_y_aciertos():
  url = "https://loteriadehoy.com/animalitos/lotto-activo/"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }

  try:
    print("🔎 Intentando conectar con Loteriadehoy...")
    res = requests.get(url, headers=headers, timeout=15)
    print(f"Respuesta HTTP: {res.status_code}")

    resultados = {}
    if res.status_code == 200:
      soup = BeautifulSoup(res.text, "html.parser")
      filas = soup.find_all("tr")

      for fila in filas:
        celdas = fila.find_all("td")
        if len(celdas) >= 2:
          hora = celdas[0].text.strip()
          num_limpio = "".join(filter(str.isdigit, celdas[1].text.strip()))
          if hora and num_limpio:
            resultados[hora] = num_limpio.zfill(2)

      print(f"📊 Resultados encontrados: {resultados}")

      if resultados:
        requests.patch(
            f"{FIREBASE_URL}/resultados.json", data=json.dumps(resultados)
        )
        print("✅ Resultados guardados en Firebase.")

    # 2. Re-calcular aciertos
    print("🔄 Recalculando aciertos...")
    res_sorteos = requests.get(f"{FIREBASE_URL}/resultados.json")
    r_res = res_sorteos.json() if res_sorteos.status_code == 200 else {}
    ganadores = set(r_res.values()) if isinstance(r_res, dict) else set()

    res_part = requests.get(f"{FIREBASE_URL}/participantes.json")
    r_part = res_part.json() if res_part.status_code == 200 else {}

    if r_part:
      if isinstance(r_part, dict):
        for clave, jugador in r_part.items():
          if isinstance(jugador, dict):
            jugadas = set(jugador.get("jugadas", []))
            aciertos = len(jugadas.intersection(ganadores))
            requests.patch(
                f"{FIREBASE_URL}/participantes/{clave}.json",
                data=json.dumps({"aciertos": aciertos}),
            )
      elif isinstance(r_part, list):
        for i, jugador in enumerate(r_part):
          if isinstance(jugador, dict):
            jugadas = set(jugador.get("jugadas", []))
            aciertos = len(jugadas.intersection(ganadores))
            requests.patch(
                f"{FIREBASE_URL}/participantes/{i}.json",
                data=json.dumps({"aciertos": aciertos}),
            )

      print("🎯 Aciertos calculados con éxito.")

  except Exception as e:
    print(f"❌ Error durante el proceso: {e}")


if __name__ == "__main__":
  ejecutar_scraper_y_aciertos()

 
 
   
