from pydantic import BaseModel

class LinkRequest(BaseModel):
    """
    Modelo de datos para representar la solicitud de html de un link
    Proporciona los campos obligatorios y su estructura para la validación.
    """
    link: str  # Enlace de la noticia a consultar
    metodo: str  # Metodo de búsqueda a utilizar (por ejemplo, 'selenium' o 'requests')


    class Config:
        # Configuración adicional para el modelo de datos
        populate_by_name = True   # Permite acceder a los campos usando sus nombres originales
        json_schema_extra = {
            "example": {
                "link": "www.latercera.com la-tercera-domingo noticia hegemonia-a-sangre-y-fuego-la-caida-de-los-trinitarios-la-banda-que-domino-la-toma-mas-grande-de-santiago OREVKTXEFBGHRKRFSGX36DPR5M",
                "metodo": "selenium"
            }
        }

class HTMLResponse(BaseModel):
    """
    Modelo de datos para representar la respuesta con el contenido HTML extraído.
    """
    html: str
    detail: str