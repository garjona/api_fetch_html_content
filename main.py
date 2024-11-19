from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import dotenv_values
import uvicorn
import logging
from routes import router, inicializar_navegadores, cerrar_navegadores  # Importa el router desde routes.py

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,  # Nivel de log mínimo (INFO, WARNING, ERROR, DEBUG)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Escribir logs en un archivo
        logging.StreamHandler()  # Mostrar logs en consola
    ]
)

logger = logging.getLogger("MainApp")  # Logger principal

# Cargar las variables de entorno desde el archivo .env
config = dotenv_values(".env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código de inicio de la aplicación
    await inicializar_navegadores()

    yield # Deja que la aplicación siga ejecutándose

    await cerrar_navegadores()

    # Código de cierre para liberar recursos, como cerrar conexiones o limpiar cachés


# Inicialización de la aplicación FastAPI con el ciclo de vida configurado
app = FastAPI(lifespan=lifespan)

# Agregar las rutas definidas en routes.py al aplicativo principal
app.include_router(router)

# Punto de entrada para ejecutar la aplicación FastAPI con Uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host=config["API_HOST"], port=int(config["API_PORT"]))