"""Puerto outbound para persistencia de predicciones."""

from abc import ABC, abstractmethod

from src.domain.entities import Prediction
from src.domain.value_objects import TransactionId


class PredictionRepository(ABC):
    """
    Puerto outbound para persistencia de predicciones.

    Este puerto abstrae el almacenamiento de predicciones para permitir
    la unión con delayed labels en el futuro.

    Contrato:
    ---------
    - Guardar predicciones con TTL (para unir con delayed labels).
    - Búsqueda eficiente por transaction_id.
    - Retención configurable según SLA de labels (7-30 días).

    Casos de uso:
    ------------
    1. Almacenar predicción en tiempo T.
    2. Recuperar predicción en tiempo T+n cuando llega la label.
    3. Calcular métricas retrospectivas (precision, recall).
    4. Audit trail de predicciones.

    Estrategia de TTL:
    -----------------
    - Labels rápidas (auto-confirmadas): 48 horas.
    - Labels manuales (revisión analistas): 7 días.
    - Disputas legales: 30 días.

    Optimizaciones:
    --------------
    - Particionamiento por timestamp (PostgreSQL).
    - Índices en transaction_id y timestamp.
    - Compresión de features (JSON → JSONB → comprimido).
    """

    @abstractmethod
    async def save(self, prediction: Prediction) -> None:
        """
        Persiste una predicción.

        Args:
            prediction: Entidad Prediction con score, features, timestamp.

        Raises:
            IOError: Si falla la persistencia.

        Examples:
            >>> prediction = Prediction(...)
            >>> await repo.save(prediction)
        """
        pass

    @abstractmethod
    async def find_by_transaction_id(
        self,
        transaction_id: TransactionId,
    ) -> Prediction | None:
        """
        Recupera una predicción por ID de transacción.

        Returns:
            Prediction si existe y no ha expirado, None si no se encuentra.

        Examples:
            >>> prediction = await repo.find_by_transaction_id(
            ...     TransactionId("txn_123")
            ... )
            >>> if prediction:
            ...     print(prediction.fraud_score)
        """
        pass

    @abstractmethod
    async def find_unlabeled(self, limit: int = 100) -> list[Prediction]:
        """
        Encuentra predicciones que aún no tienen label confirmada.

        Útil para:
        - Métricas de lag de labels.
        - Notificar al equipo de revisión manual.
        - Priorizar revisiones (predicciones con score alto sin label).

        Args:
            limit: Número máximo de predicciones a retornar.

        Returns:
            Lista de predicciones sin label.

        Examples:
            >>> unlabeled = await repo.find_unlabeled(limit=50)
            >>> for pred in unlabeled:
            ...     if pred.fraud_score.is_high_risk():
            ...         print(f"⚠️ Revisar: {pred.transaction_id}")
        """
        pass

    @abstractmethod
    async def update_with_label(
        self,
        prediction: Prediction,
    ) -> None:
        """
        Actualiza una predicción con su label confirmada.

        Args:
            prediction: Predicción con label actualizada.

        Raises:
            PredictionNotFoundException: Si la predicción no existe.

        Examples:
            >>> prediction = await repo.find_by_transaction_id(txn_id)
            >>> prediction.add_label(is_fraud=True, timestamp=now, source="manual_review")
            >>> await repo.update_with_label(prediction)
        """
        pass
