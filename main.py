from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import dotenv_values
import uvicorn
from routes import router  # Importa el router desde routes.py

# Cargar las variables de entorno desde el archivo .env
config = dotenv_values(".env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código de inicio de la aplicación
    # Aquí se pueden agregar inicializaciones como abrir conexiones a bases de datos o cargar configuraciones

    yield # Deja que la aplicación siga ejecutándose

    # Código de cierre para liberar recursos, como cerrar conexiones o limpiar cachés


# Inicialización de la aplicación FastAPI con el ciclo de vida configurado
app = FastAPI(lifespan=lifespan)

# Agregar las rutas definidas en routes.py al aplicativo principal
app.include_router(router)

# Punto de entrada para ejecutar la aplicación FastAPI con Uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host=config["API_HOST"], port=int(config["API_PORT"]))