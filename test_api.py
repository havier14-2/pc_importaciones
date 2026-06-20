import requests
import pandas as pd

def probar_api_dolar():
    print("Iniciando conexión a Mindicador.cl...")
    
    # Endpoint gratuito para el Dólar en Chile
    url = "https://mindicador.cl/api/dolar"
    
    try:
        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status() # Verifica que la web no esté caída
        
        datos = respuesta.json()
        serie_dolar = datos['serie']
        
        # Convertimos la respuesta a un DataFrame de Pandas
        df = pd.DataFrame(serie_dolar)
        
        # Limpiamos las fechas para que sean legibles
        df['fecha'] = pd.to_datetime(df['fecha']).dt.date
        
        print("\n¡ÉXITO! La API está funcionando y entregando datos históricos diarios.")
        print(f"Se extrajeron {len(df)} días de cotización del Dólar.\n")
        
        # Mostramos los primeros 10 días para comprobar la calidad de los datos
        print(df.head(10).to_string(index=False))
        
    except Exception as e:
        print(f"Error al conectar con la API: {e}")

if __name__ == "__main__":
    probar_api_dolar()