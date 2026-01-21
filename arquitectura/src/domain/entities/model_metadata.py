"""Entidad ModelMetadata - Metadatos del modelo ML."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ModelMetadata:
    """
    Metadatos del modelo de Machine Learning.

    Encapsula información sobre la versión, performance y estado del modelo.

    Attributes:
        version: Versión del modelo (ej. "v1.2.3" o timestamp).
        created_at: Momento de creación/actualización del modelo.
        training_samples_count: Número de ejemplos de entrenamiento procesados.
        metrics: Diccionario con métricas del modelo (precision, recall, F1, AUC-ROC).
        drift_score: Score de concept drift (0.0 = sin drift, 1.0 = drift completo).
        is_active: Indica si esta es la versión activa en producción.
        checkpoint_path: Ruta al archivo de checkpoint (opcional).
        additional_info: Información adicional del modelo.

    Invariantes:
        - training_samples_count >= 0
        - drift_score entre 0.0 y 1.0
    """

    version: str
    created_at: datetime
    training_samples_count: int = 0
    metrics: dict[str, float] = field(default_factory=dict)
    drift_score: float = 0.0
    is_active: bool = True
    checkpoint_path: str | None = None
    additional_info: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Valida invariantes de los metadatos."""
        self._validate()

    def _validate(self) -> None:
        """
        Valida reglas de negocio de los metadatos.

        Raises:
            ValueError: Si alguna invariante se viola.
        """
        if not self.version or not self.version.strip():
            raise ValueError("Version no puede estar vacía")

        if self.training_samples_count < 0:
            raise ValueError(
                f"training_samples_count no puede ser negativo: {self.training_samples_count}"
            )

        if not 0.0 <= self.drift_score <= 1.0:
            raise ValueError(
                f"drift_score debe estar entre 0.0 y 1.0, recibido: {self.drift_score}"
            )

    def get_metric(self, metric_name: str, default: float = 0.0) -> float:
        """
        Obtiene una métrica específica del modelo.

        Args:
            metric_name: Nombre de la métrica (ej. 'precision', 'recall', 'f1').
            default: Valor por defecto si la métrica no existe.

        Returns:
            Valor de la métrica.
        """
        return self.metrics.get(metric_name, default)

    def update_metrics(self, new_metrics: dict[str, float]) -> None:
        """
        Actualiza las métricas del modelo.

        Args:
            new_metrics: Diccionario con las nuevas métricas.
        """
        self.metrics.update(new_metrics)

    def increment_samples(self, count: int = 1) -> None:
        """
        Incrementa el contador de ejemplos de entrenamiento.

        Args:
            count: Número de ejemplos a agregar (default: 1).

        Raises:
            ValueError: Si count es negativo.
        """
        if count < 0:
            raise ValueError(f"count no puede ser negativo: {count}")
        self.training_samples_count += count

    def has_good_performance(
        self,
        min_f1: float = 0.7,
        max_drift: float = 0.3,
    ) -> bool:
        """
        Determina si el modelo tiene buen performance.

        Args:
            min_f1: Umbral mínimo de F1-score.
            max_drift: Umbral máximo de drift.

        Returns:
            True si el modelo cumple los umbrales de calidad.
        """
        f1_score = self.get_metric("f1", 0.0)
        return f1_score >= min_f1 and self.drift_score <= max_drift

    def should_trigger_alert(
        self,
        min_f1: float = 0.5,
        max_drift: float = 0.5,
    ) -> bool:
        """
        Determina si se debe disparar una alerta por degradación del modelo.

        Args:
            min_f1: Umbral crítico de F1-score.
            max_drift: Umbral crítico de drift.

        Returns:
            True si se debe alertar.
        """
        f1_score = self.get_metric("f1", 0.0)
        return f1_score < min_f1 or self.drift_score > max_drift

    def __repr__(self) -> str:
        f1 = self.get_metric("f1", 0.0)
        return (
            f"ModelMetadata(version={self.version}, "
            f"samples={self.training_samples_count}, "
            f"f1={f1:.3f}, "
            f"drift={self.drift_score:.3f}, "
            f"active={self.is_active})"
        )
