from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class PredictionRequestDTO(BaseModel):
    """Objeto genérico para recibir datos de inferencia."""
    
    features: Dict[str, Any] = Field(
        ..., 
        description="Diccionario de características dinámicas para el modelo"
    )


class PredictionResponseDTO(BaseModel):
    """Objeto genérico para devolver la predicción."""
    
    prediction: Any = Field(
        ...,
        description="El resultado de la predicción (clase o valor)"
    )
    probability: Optional[float] = Field(
        default=None,
        description="Probabilidad (si aplica)"
    )
    model_version: str = Field(
        ...,
        description="Versión del modelo que atendió la petición"
    )
