from urllib.parse import urljoin
from urllib.parse import urlparse, urlunsplit
from bs4 import BeautifulSoup
from fastapi import APIRouter, Body, HTTPException, status
from fastapi.encoders import jsonable_encoder
from models import LinkRequest, HTMLResponse, FetchLinksPageResponse, FetchLinksPageRequest
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

def extraer_links_page_request(url,prefixes):
    urls = {}
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        enlaces = soup.find_all('a')
        for enlace in enlaces:
            url = enlace.get('href')
            if url != None and url.startswith('http') == False:
                url = urljoin(response.url,url)
            elif url == None:
                url = ""
            enlace_limpiado = limpiar_url(url)
            urls = agregar_url(urls,enlace_limpiado) if filtrar_link(enlace_limpiado,prefixes) == True else urls
    except Exception as e:
        print(f"ERROR en {enlace}: {e}")
        pass
    return urls

def limpiar_url(url):
    cleaned_url = urlunsplit((*(urlparse(url)[:3]), '', ''))
    return cleaned_url

def agregar_url(unique_links, url):
    unique_links.setdefault(url, "")
    return unique_links

def url_comienza_con(url, lista) -> bool:
    """
    Verifica si la URL comienza con alguno de los strings en la lista, sin usar startswith()
    """
    url = url.lower()
    for inicio in lista:
        if url[:len(inicio)].lower() == inicio.lower():
            return True
    return False

def filtrar_link(url,prefixes):
    if url_comienza_con(url, prefixes) and url not in prefixes:
        return True
    return False


@router.get("/fetch_html", response_model=HTMLResponse, response_description="Consultar el html de un link", status_code=status.HTTP_200_OK)
def fetch_html(link_request: LinkRequest = Body(...)):
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

@router.get("/fetch_links_page", response_model=FetchLinksPageResponse, response_description="Extrae los links de una pagina web", status_code=status.HTTP_200_OK)
def fetch_links_page(fetch_links_page_request: FetchLinksPageRequest = Body(...)):
    try:
        urls = {}
        # Convertir el modelo de petición a un formato JSON serializable
        fetch_links_page_request_json = jsonable_encoder(fetch_links_page_request)

        link = fetch_links_page_request_json["link"]
        prefixes = fetch_links_page_request_json["prefixes"]
        metodo = fetch_links_page_request_json["metodo"]

        # Llamar a la función de extracción según el metodo especificado
        if metodo == "selenium":
            html_content, response_detail = fetch_html_selenium(link)
        elif metodo == "requests":
            html_content, response_detail = fetch_html_requests(link)
        else:
            return "", "Metodo solicitado no encontrado"

        soup = BeautifulSoup(html_content, 'html.parser')
        enlaces = soup.find_all('a')
        for enlace in enlaces:
            url = enlace.get('href')
            if url is not None and url.startswith('http') == False:
                url = urljoin(link, url)
            elif url is None:
                url = ""
            enlace_limpiado = limpiar_url(url)
            urls = agregar_url(urls, enlace_limpiado) if filtrar_link(enlace_limpiado, prefixes) == True else urls
        # Retornar el contenido HTML extraído y un mensaje de éxito
        return {"links": list(urls), "detail": response_detail}
    except ValueError as e:
        # Manejar errores y retornar un mensaje de error
        raise HTTPException(status_code=400, detail=f"Error de datos: {str(e)}")