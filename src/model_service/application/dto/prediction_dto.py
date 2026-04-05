from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class PredictionRequestDTO(BaseModel):
    """Objeto gen茅rico para recibir datos de inferencia."""

    features: Dict[str, Any] = Field(
        ..., description="Diccionario de caracter铆sticas din谩micas para el modelo"
    )


class PredictionResponseDTO(BaseModel):
    """Objeto gen茅rico para devolver la predicci贸n."""

    prediction: Any = Field(
        ..., description="El resultado de la predicci贸n (clase o valor)"
    )
    probability: Optional[float] = Field(
        default=None, description="Probabilidad (si aplica)"
    )
    model_version: str = Field(
        ..., description="Versi贸n del modelo que atendi贸 la petici贸n"
    )


class TrainRequestDTO(BaseModel):
    """Objeto para recibir datos de entrenamiento del AutoML."""

    dataset_path: str = Field(
        ..., description="Ruta f胹ica o URI del dataset CSV a procesar"
    )
    target_column: str = Field(
        default="target", description="Nombre de la columna a predecir"
    )
    experiment_name: str = Field(
        default="automl_experiment", description="Nombre del experimento de MLflow"
    )
    model_name: str = Field(
        default="ChampionModel", description="Nombre del modelo a registrar"
    )

