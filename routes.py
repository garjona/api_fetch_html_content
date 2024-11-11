from fastapi import APIRouter, Body, HTTPException, status
from fastapi.encoders import jsonable_encoder
from models import LinkRequest, HTMLResponse
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

router = APIRouter() # Crear el enrutador para gestionar las rutas

def abrir_navegador(disable_javascript = False):
    """
    Configura y abre un navegador en modo headless usando Selenium.
    Si disable_javascript es True, se deshabilita JavaScript en el navegador.
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Ejecutar sin interfaz gráfica
    chrome_options.add_argument('--no-sandbox')  # Requerido para entornos sin privilegios elevados
    chrome_options.page_load_strategy = 'eager'  # Estrategia de carga rápida para la página
    if disable_javascript:
        # Deshabilitar JavaScript en el navegador para una carga más rápida si se solicita
        prefs = {"webkit.webprefs.javascript_enabled": False,
                 "profile.content_settings.exceptions.javascript.*.setting": 2,
                 "profile.default_content_setting_values.javascript": 2,
                 "profile.managed_default_content_settings.javascript": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument('--disable-javascript')
    chrome_options.headless = True  # Asegura que el navegador esté en modo sin interfaz
    wd = webdriver.Chrome(options=chrome_options)
    return wd

def fetch_html_selenium(link):
    """
    Extrae el código HTML de una página web utilizando Selenium.
    Argumentos:
        link (str): URL de la página web.
    Retorna:
        str: Contenido HTML de la página.
    """
    wd = abrir_navegador(True)  # Abre el navegador con JavaScript deshabilitado
    wd.get(link)
    time.sleep(3)  # Espera para asegurar que la página esté completamente cargada
    html = wd.page_source
    wd.close()  # Cierra el navegador

    return html,"html extraido por metodo selenium"

def fetch_html_requests(link):
    """
    Extrae el código HTML de una página web utilizando la biblioteca requests.
    Argumentos:
        link (str): URL de la página web.
    Retorna:
        str: Contenido HTML de la página.
    """
    response = requests.get(link)
    response.encoding = "utf-8"  # Configura la codificación a UTF-8
    html = response.content.decode('utf-8')  # Decodifica el contenido en texto HTML
    return html, "html extraido por metodo request"


@router.get("/api_fetch_html_content", response_model=HTMLResponse, response_description="Consultar el html de un link", status_code=status.HTTP_200_OK)
def upsert_new(link_request: LinkRequest = Body(...)):
    """
    Endpoint para obtener el HTML de una página web.
    Argumentos:
        link_request (LinkRequest): Objeto que contiene el link y el metodo de extracción.
    Retorna:
        dict: HTML extraído y mensaje de éxito o error.
    """
    try:
        # Convertir el modelo de petición a un formato JSON serializable
        link_request_json = jsonable_encoder(link_request)

        # Extrae el link y el metodo de extracción del cuerpo de la petición
        link = link_request_json["link"]
        metodo = link_request_json["metodo"]

        # Llamar a la función de extracción según el metodo especificado
        if metodo == "selenium" :
            html_content,response_detail = fetch_html_selenium(link)
        elif metodo == "requests":
            html_content,response_detail = fetch_html_requests(link)
        else:
            html_content, response_detail = ("","Metodo solicitado no encontrado")

        # Retornar el contenido HTML extraído y un mensaje de éxito
        return {"html": html_content, "detail": response_detail}
    except ValueError as e:
        # Manejar errores y retornar un mensaje de error
        raise HTTPException(status_code=400, detail=f"Error de datos: {str(e)}")