from fastapi import FastAPI

from model_service.application.dto.prediction_dto import (
    PredictionRequestDTO,
    PredictionResponseDTO,
)

app = FastAPI(
    title="MLOps Generic Serving API",
    description="Plantilla base para despliegue de modelos",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Endpoint de monitoreo básico para Kubernetes/Docker."""
    return {"status": "healthy"}


@app.post("/predict", response_model=PredictionResponseDTO)
def predict(request: PredictionRequestDTO) -> PredictionResponseDTO:
    """
    Endpoint principal de inferencia.
    En el futuro, esto llamará a un Use Case genérico.
    """
    # TODO: Conectar con el Use Case y MLflow
    return PredictionResponseDTO(
        prediction=1,  # Dummy prediction
        probability=0.99,
        model_version="dummy-v1",
    )
