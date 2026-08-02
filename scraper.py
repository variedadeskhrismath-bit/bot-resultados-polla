
           import json
from bs4 import BeautifulSoup
import requests

FIREBASE_URL = (
    "https://polla-la-fortuna00-8bd4a-default-rtdb.firebaseio.com/polla_data"
)


def ejecutar_scraper_y_aciertos():
  # 1. Extraer resultados
  url = "https://loteriadehoy.com/animalitos/lotto-activo/"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
      )
  }

  try:
    res = requests.get(url, headers=headers, timeout=10)
    resultados = {}

    if res.status_code == 200:
      soup = BeautifulSoup(res.text, "html.parser")
      for fila in soup.find_all("tr"):
        celdas = fila.find_all("td")
        if len(celdas) >= 2:
          hora = celdas[0].text.strip()
          num_limpio = "".join(filter(str.isdigit, celdas[1].text.strip()))
          if hora and num_limpio:
            resultados[hora] = num_limpio.zfill(2)

      # Guardar resultados en Firebase
      if resultados:
        requests.patch(
            f"{FIREBASE_URL}/resultados.json", data=json.dumps(resultados)
        )
        print("✅ Resultados de Loteriadehoy actualizados.")

    # 2. Calcular aciertos de los participantes
    r_res = requests.get(f"{FIREBASE_URL}/resultados.json").json() or {}
    ganadores = set(r_res.values())

    r_part = requests.get(f"{FIREBASE_URL}/participantes.json").json() or {}

    if r_part:
      if isinstance(r_part, dict):
        for clave, jugador in r_part.items():
          jugadas = set(jugador.get("jugadas", []))
          aciertos = len(jugadas.intersection(ganadores))
          requests.patch(
              f"{FIREBASE_URL}/participantes/{clave}.json",
              data=json.dumps({"aciertos": aciertos}),
          )
      elif isinstance(r_part, list):
        for i, jugador in enumerate(r_part):
          if jugador:
            jugadas = set(jugador.get("jugadas", []))
            aciertos = len(jugadas.intersection(ganadores))
            requests.patch(
                f"{FIREBASE_URL}/participantes/{i}.json",
                data=json.dumps({"aciertos": aciertos}),
            )
      print("🎯 Aciertos calculados exitosamente.")

  except Exception as e:
    print(f"❌ Error en el proceso: {e}")


# Si se ejecuta directamente el archivo
if __name__ == "__main__":
  ejecutar_scraper_y_aciertos()

