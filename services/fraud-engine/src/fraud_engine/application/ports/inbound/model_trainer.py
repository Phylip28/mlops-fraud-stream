"""Puerto inbound para entrenamiento incremental del modelo."""

from abc import ABC, abstractmethod

from src.domain.entities import FraudLabel, ModelMetadata
from src.domain.value_objects import TransactionId


class ModelTrainer(ABC):
    """
    Puerto inbound para entrenamiento incremental del modelo.

    Este puerto define el contrato para actualizar el modelo con delayed labels.

    Contrato:
    ---------
    - Recibe una label confirmada (delayed label).
    - Actualiza el modelo incrementalmente con river.learn_one().
    - Retorna metadatos actualizados del modelo.
    - Thread-safe: Múltiples labels pueden llegar concurrentemente.

    Flujo:
    ------
    1. Llega FraudLabel desde el stream de labels.
    2. Se busca la predicción original en PredictionRepository.
    3. Se extraen las features originales (point-in-time correctness).
    4. Se actualiza el modelo con learn_one(features, label).
    5. Se calcula métrica retrospectiva (¿era correcta la predicción?).
    6. Se decide si hacer checkpoint del modelo.
    7. Se retorna ModelMetadata actualizado.

    Invariantes:
    -----------
    - La predicción original debe existir en PredictionRepository.
    - Las features usadas en la predicción deben estar disponibles.
    - El modelo debe estar en modo "learning" (no congelado).

    Excepciones:
    -----------
    - PredictionNotFoundException: Si no se encuentra la predicción original.
    - ModelNotReadyException: Si el modelo no está inicializado.
    """

    @abstractmethod
    async def update_with_label(
        self,
        transaction_id: TransactionId,
        label: FraudLabel,
    ) -> ModelMetadata:
        """
        Actualiza el modelo con una label confirmada.

        Args:
            transaction_id: ID de la transacción original.
            label: Label confirmada (is_fraud, confidence, source).

        Returns:
            ModelMetadata: Metadatos actualizados (versión, métricas, samples_count).

        Raises:
            PredictionNotFoundException: Si no se encuentra la predicción original.
            ModelNotReadyException: Si el modelo no está inicializado.

        Examples:
            >>> trainer = UpdateModelUseCase(...)
            >>> label = FraudLabel(transaction_id=..., is_fraud=True, ...)
            >>> metadata = await trainer.update_with_label(transaction_id, label)
            >>> print(metadata.training_samples_count)
            1523
        """
        pass

    @abstractmethod
    async def should_trigger_checkpoint(self) -> bool:
        """
        Determina si debe persistirse el estado del modelo.

        Lógica de negocio:
        - Cada 100 updates → Checkpoint ligero (Redis).
        - Cada 1000 updates → Snapshot pesado (S3).
        - Cada X minutos (ej. cada 5 minutos).
        - Cuando drift_score > threshold.

        Returns:
            True si se debe hacer checkpoint del modelo.

        Examples:
            >>> trainer = UpdateModelUseCase(...)
            >>> if await trainer.should_trigger_checkpoint():
            ...     await model_repository.save(model, metadata)
        """
        pass
