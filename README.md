# api_fetch_html_content

## Descripción

Esta API permite extraer el código HTML de una página web específica utilizando dos métodos diferentes: Selenium y Requests. La API está construida con **FastAPI** y es ideal para aplicaciones que necesitan capturar contenido de sitios web en formato HTML para su procesamiento posterior.

## Características

- **Extracción de HTML**: Permite obtener el código HTML de cualquier página web pública.
- **Método de Extracción**: Soporta dos métodos:
  - **Selenium**: Para páginas web que requieren ejecución de JavaScript.
  - **Requests**: Para páginas estáticas y rápidas de procesar.
- **Selección Automática de Método**: Los usuarios pueden especificar el método, lo que permite mayor control en función del tipo de página.
- **Validación de Entrada**: Los parámetros de entrada son validados para asegurar que sean correctos antes de ejecutar la extracción.

## Endpoints

- **GET /api_fetch_html_content**: Permite enviar un enlace y un método de extracción, y devuelve el HTML de la página solicitada.
  - **Parámetros de entrada**: 
    - `link` (str): URL de la página que deseas extraer.
    - `metodo` (str): Método de extracción ("selenium" o "requests").

## Requisitos

- **Python** 3.11+
- **FastAPI** para la gestión de la API

## Instalación

1. Clonar este repositorio:

   ```bash
   git clone https://github.com/usuario/001_api_data_ingestor.git
   cd 001_api_data_ingestor

2. Crear un entorno virtual:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # En Windows, usar `venv\Scripts\activate`
   
3. Instalar las dependencias::

   ```bash
   pip install -r requirements.txt
   
4. Configurar las variables de entorno creando un archivo .env en el directorio principal:

   ```bash
   API_HOST=<tu_host_api>
   API_PORT=<puerto_api>