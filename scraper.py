from datetime import datetime
import re
from bs4 import BeautifulSoup
import requests

# URL de tu Firebase Realtime Database
DATABASE_URL = (
    'https://polla-la-fortuna002-default-rtdb.firebaseio.com/polla_data.json'
)

# Header para simular un navegador real y evitar bloqueos de la página
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,'
        ' like Gecko) Chrome/115.0.0.0 Safari/537.36'
    )
}


def obtener_resultados_loteria():
  """Hace scraping a loteriadehoy.com para extraer los resultados de los animalitos."""
  url = 'https://www.loteriadehoy.com/'
  resultados = {'Lotto Activo': {}, 'La Granjita': {}, 'Selva Plus': {}}

  try:
    response = requests.get(url, headers=HEADERS, timeout=15)
    if response.status_code != 200:
      print(f'Error al acceder a la página: Status {response.status_code}')
      return resultados

    soup = BeautifulSoup(response.text, 'html.parser')

    # Buscamos los bloques o contenedores de cada lotería en la página
    # (Adaptado a la estructura típica de loteriadehoy.com)
    for juego in ['Lotto Activo', 'La Granjita', 'Selva Plus']:
      # Intentamos ubicar la sección del juego por su texto/encabezado
      seccion_juego = soup.find(
          lambda tag: tag.name in ['h2', 'h3', 'div', 'a']
          and juego.lower() in tag.text.lower()
      )

      if seccion_juego:
        # Buscamos el contenedor padre o cercano que agrupa las horas y resultados
        contenedor = seccion_juego.find_parent(
            ['div', 'section', 'article']
        ) or seccion_juego.find_next_sibling(['div'])

        if contenedor:
          # Extraemos elementos con texto que tengan formato de hora y número/animal
          elementos = contenedor.find_all(['div', 'li', 'tr', 'p'])
          for elem in elementos:
            texto = elem.get_text(strip=True)
            # Busca patrones comunes como "09:00 AM - 04" o "09:00 AM 04-DELFIN"
            match = re.search(
                r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))\s*[-:]?\s*(\d{1,2})', texto
            )
            if match:
              hora = match.group(1).upper()
              numero = match.group(2).zfill(
                  2
              )  # Asegura 2 dígitos (ej: "04")
              resultados[juego][hora] = numero

  except Exception as e:
    print(f'Error durante el scraping: {e}')

  return resultados


def actualizar_firebase():
  """Envía los resultados obtenidos a Firebase Realtime Database."""
  hoy = datetime.now().strftime('%Y-%m-%d')
  print(f'Iniciando scraping automático para la fecha: {hoy}...')

  resultados_obtenidos = obtener_resultados_loteria()

  datos_a_enviar = {
      'fecha_actualizacion': hoy,
      'ultima_ejecucion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
      'resultados': resultados_obtenidos,
  }

  try:
    response = requests.patch(DATABASE_URL, json=datos_a_enviar)
    if response.status_code == 200:
      print('¡ÉXITO! Resultados reales guardados en Firebase correctamente.')
    else:
      print(
          f'Error al guardar en Firebase: Status {response.status_code} -'
          f' {response.text}'
      )
  except Exception as e:
    print(f'Error al conectar con Firebase: {e}')


if __name__ == '__main__':
  actualizar_firebase()



