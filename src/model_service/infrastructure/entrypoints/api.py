import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import mlflow
import pandas as pd
from fastapi import FastAPI, HTTPException

from model_service.application.dto.prediction_dto import (
    PredictionRequestDTO,
    PredictionResponseDTO,
)

# Usar un .env para producción
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://localhost:9000"
os.environ["AWS_ACCESS_KEY_ID"] = "minio_user"
os.environ["AWS_SECRET_ACCESS_KEY"] = "minio_password"
mlflow.set_tracking_uri("http://localhost:5000")

# Variable donde vivirá nuestro modelo en memoria
model_cache: dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Ciclo de vida de FastAPI.
    Todo lo que está antes del 'yield' se ejecuta al prender el servidor.
    """
    print("Iniciando API... Conectando con MLflow...")
    model_name = "GenericModel"
    model_alias = "latest"  # o una versión específica como "1"

    try:
        # URI mágica de MLflow para descargar modelos registrados
        model_uri = f"models:/{model_name}/{model_alias}"
        print(f"Descargando modelo desde: {model_uri}")

        # Va a Postgres, averigua dónde está en MinIO, lo descarga y lo carga en memoria
        loaded_model = mlflow.pyfunc.load_model(model_uri)

        # Lo guardamos en caché
        model_cache["predictor"] = loaded_model
        model_cache["version"] = model_alias
        print("¡Modelo cargado en memoria exitosamente!")
    except Exception as e:
        print(f"Error cargando el modelo: {e}")
        # En una plantilla base real, evitamos que la API crashee si no hay modelo,

    yield  # Aquí el servidor está vivo y recibiendo peticiones

    # Lo que está después del yield se ejecuta al apagar el servidor
    print("Apagando API y liberando memoria...")
    model_cache.clear()


# Crear la app usando el lifespan
app = FastAPI(
    title="MLOps Generic Serving API",
    description="Plantilla base conectada a MLflow",
    version="0.1.0",
    lifespan=lifespan,
)


# Health check básico para monitoreo
@app.get("/health")
def health_check() -> dict[str, str]:
    status = "healthy" if "predictor" in model_cache else "degraded - no model"
    return {"status": status}


# Endpoint de inferencia
@app.post("/predict", response_model=PredictionResponseDTO)
def predict(request: PredictionRequestDTO) -> PredictionResponseDTO:
    """Endpoint principal de inferencia ejecutando el modelo real."""
    if "predictor" not in model_cache:
        raise HTTPException(status_code=503, detail="Modelo no cargado en el servidor")

    # 1. Extraer los datos del request
    # scikit-learn espera un formato tabular (DataFrame) de 2D
    data = pd.DataFrame([request.features])

    try:
        # 2. Hacer la predicción con el modelo de MLflow
        model = model_cache["predictor"]
        prediction = model.predict(data)

        # 3. Formatear la respuesta
        return PredictionResponseDTO(
            prediction=int(prediction[0]), model_version=model_cache["version"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en inferencia: {str(e)}")
