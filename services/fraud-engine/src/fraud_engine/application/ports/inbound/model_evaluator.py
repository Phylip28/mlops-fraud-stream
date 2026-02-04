"""Puerto inbound para evaluación del modelo."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TimeWindow:
    """Ventana temporal para evaluación."""

    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.end <= self.start:
            raise ValueError("end debe ser posterior a start")


@dataclass
class ModelMetrics:
    """Métricas de evaluación del modelo."""

    precision: float
    recall: float
    f1_score: float
    auc_roc: float | None = None
    total_predictions: int = 0
    correct_predictions: int = 0
    false_positives: int = 0
    false_negatives: int = 0

    @property
    def accuracy(self) -> float:
        """Calcula accuracy."""
        if self.total_predictions == 0:
            return 0.0
        return self.correct_predictions / self.total_predictions


class ModelEvaluator(ABC):
    """
    Puerto inbound para evaluación del modelo en ventanas temporales.

    Este puerto permite calcular métricas retrospectivas del modelo
    comparando predicciones con labels confirmadas.

    Contrato:
    ---------
    - Recibe una ventana temporal.
    - Recupera predicciones y labels en esa ventana.
    - Calcula métricas (precision, recall, F1, AUC-ROC).
    - Retorna ModelMetrics.

    Casos de uso:
    ------------
    - Monitoreo continuo de performance del modelo.
    - Detección de degradación (concept drift).
    - A/B testing entre versiones del modelo.
    - Generación de reportes de calidad.

    Invariantes:
    -----------
    - La ventana temporal debe ser válida (end > start).
    - Solo se consideran predicciones con labels confirmadas.
    """

    @abstractmethod
    async def evaluate(self, window: TimeWindow) -> ModelMetrics:
        """
        Evalúa el modelo en una ventana temporal.

        Args:
            window: Ventana temporal para evaluación.

        Returns:
            ModelMetrics: Métricas calculadas (precision, recall, F1, etc.).

        Examples:
            >>> evaluator = EvaluateModelUseCase(...)
            >>> window = TimeWindow(start=yesterday, end=now)
            >>> metrics = await evaluator.evaluate(window)
            >>> print(f"F1-Score: {metrics.f1_score:.3f}")
            F1-Score: 0.872
        """
        pass

    @abstractmethod
    async def evaluate_current_model(self, last_n_predictions: int = 1000) -> ModelMetrics:
        """
        Evalúa el modelo actual sobre las últimas N predicciones.

        Args:
            last_n_predictions: Número de predicciones recientes a evaluar.

        Returns:
            ModelMetrics: Métricas del modelo actual.

        Examples:
            >>> metrics = await evaluator.evaluate_current_model(last_n_predictions=500)
            >>> if metrics.f1_score < 0.7:
            ...     print("⚠️ Modelo degradado, considerar rollback")
        """
        pass
