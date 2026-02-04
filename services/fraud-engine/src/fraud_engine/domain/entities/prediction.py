"""Entidad Prediction - Representa una predicción de fraude."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ..value_objects import FraudScore, TransactionId


@dataclass
class Prediction:
    """
    Entidad que representa una predicción de fraude sobre una transacción.

    Almacena el resultado de la inferencia del modelo, incluyendo metadata
    necesaria para el posterior re-entrenamiento con delayed labels.

    Attributes:
        prediction_id: Identificador único de la predicción (puede ser igual al transaction_id).
        transaction_id: ID de la transacción sobre la que se predijo.
        fraud_score: Score de probabilidad de fraude (0.0 - 1.0).
        model_version: Versión del modelo que generó la predicción.
        timestamp: Momento en que se realizó la predicción.
        features_used: Features que se usaron para la predicción (para point-in-time correctness).
        label: Label confirmada (None si aún no ha llegado).
        label_timestamp: Momento en que se confirmó la label.
        label_source: Fuente de la label (manual_review, api, customer_dispute).

    Invariantes:
        - fraud_score debe estar entre 0.0 y 1.0
        - Si label no es None, label_timestamp debe estar definido
        - label_timestamp debe ser posterior a timestamp
    """

    prediction_id: str
    transaction_id: TransactionId
    fraud_score: FraudScore
    model_version: str
    timestamp: datetime
    features_used: dict[str, Any] = field(default_factory=dict)
    label: bool | None = None
    label_timestamp: datetime | None = None
    label_source: str | None = None

    def __post_init__(self) -> None:
        """Valida invariantes de la predicción."""
        self._validate()

    def _validate(self) -> None:
        """
        Valida reglas de negocio de la predicción.

        Raises:
            ValueError: Si alguna invariante se viola.
        """
        if not self.prediction_id or not self.prediction_id.strip():
            raise ValueError("Prediction ID no puede estar vacío")

        if not self.model_version or not self.model_version.strip():
            raise ValueError("Model version no puede estar vacía")

        # Si hay label, debe haber timestamp
        if self.label is not None and self.label_timestamp is None:
            raise ValueError("Si hay label, debe haber label_timestamp")

        # Label timestamp debe ser posterior a prediction timestamp
        if self.label_timestamp and self.label_timestamp < self.timestamp:
            raise ValueError("label_timestamp debe ser posterior a timestamp de predicción")

    def is_labeled(self) -> bool:
        """
        Determina si la predicción ya tiene una label confirmada.

        Returns:
            True si la predicción ha sido etiquetada.
        """
        return self.label is not None

    def add_label(
        self,
        label: bool,
        label_timestamp: datetime,
        source: str = "manual_review",
    ) -> None:
        """
        Agrega una label confirmada a la predicción.

        Este método se invoca cuando llega una delayed label desde el stream.

        Args:
            label: True si es fraude, False si no lo es.
            label_timestamp: Momento en que se confirmó la label.
            source: Fuente de la label (manual_review, api, customer_dispute).

        Raises:
            ValueError: Si la predicción ya tiene label o si el timestamp es inválido.
        """
        if self.is_labeled():
            raise ValueError(
                f"Predicción {self.prediction_id} ya tiene label: {self.label}"
            )

        if label_timestamp < self.timestamp:
            raise ValueError("label_timestamp debe ser posterior a timestamp de predicción")

        self.label = label
        self.label_timestamp = label_timestamp
        self.label_source = source

    def was_correct(self, threshold: float = 0.5) -> bool | None:
        """
        Determina si la predicción fue correcta.

        Args:
            threshold: Umbral de decisión para clasificar como fraude.

        Returns:
            True si la predicción fue correcta, False si fue incorrecta,
            None si aún no hay label confirmada.
        """
        if not self.is_labeled():
            return None

        predicted_fraud = self.fraud_score.value >= threshold
        return predicted_fraud == self.label

    def get_label_lag_seconds(self) -> float | None:
        """
        Calcula el lag (retraso) entre la predicción y la label en segundos.

        Útil para métricas de SLA de labels.

        Returns:
            Lag en segundos, o None si no hay label.
        """
        if not self.is_labeled() or self.label_timestamp is None:
            return None

        lag = self.label_timestamp - self.timestamp
        return lag.total_seconds()

    def to_training_example(self) -> tuple[dict[str, Any], bool]:
        """
        Convierte la predicción en un ejemplo de entrenamiento.

        Returns:
            Tupla (features, label) para entrenar el modelo.

        Raises:
            ValueError: Si la predicción no tiene label.
        """
        if not self.is_labeled() or self.label is None:
            raise ValueError(
                f"No se puede crear ejemplo de entrenamiento sin label: {self.prediction_id}"
            )

        return (self.features_used, self.label)

    def __repr__(self) -> str:
        label_str = f"label={self.label}" if self.is_labeled() else "unlabeled"
        return (
            f"Prediction(id={self.prediction_id}, "
            f"transaction={self.transaction_id}, "
            f"score={self.fraud_score}, "
            f"model={self.model_version}, "
            f"{label_str})"
        )
