from datetime import datetime
import requests

# 1. Configuración de tu Realtime Database (usando REST API)
# Añadimos /polla_data.json al final para apuntar al nodo correcto
DATABASE_URL = (
    'https://polla-la-fortuna002-default-rtdb.firebaseio.com/polla_data.json'
)


def actualizar_datos_polla():
  """Función principal para hacer scraping e ingerir los datos en Firebase."""
  hoy = datetime.now().strftime('%Y-%m-%d')
  print(f'Iniciando actualización para la fecha: {hoy}...')

  # AQUÍ IRÁ TU LÓGICA DE SCRAPING
  # Ejemplo de datos a enviar:
  datos_a_enviar = {
      'fecha_actualizacion': hoy,
      'resultados': {
          'Lotto Activo': {'09:00 AM': '04', '10:00 AM': '12'},
          'La Granjita': {'09:00 AM': '25'},
      },
  }

  try:
    # Usamos PATCH para actualizar/fusionar datos sin borrar lo que ya existe
    response = requests.patch(DATABASE_URL, json=datos_a_enviar)

    if response.status_code == 200:
      print('¡ÉXITO! Datos enviados e integrados correctamente en Firebase.')
    else:
      print(
          f'Error al guardar en Firebase: Status {response.status_code} -'
          f' {response.text}'
      )

  except Exception as e:
    print(f'Ocurrió un error en la conexión: {e}')


if __name__ == '__main__':
  actualizar_datos_polla()

