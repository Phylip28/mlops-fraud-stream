"""Puerto outbound para consumo de stream de labels confirmadas."""

from abc import ABC, abstractmethod
from typing import AsyncIterator

from src.domain.entities import FraudLabel


class LabelStream(ABC):
    """
    Puerto outbound para consumo de labels confirmadas (delayed labels).

    Este puerto abstrae la lectura de labels que llegan tiempo después
    de la transacción original (T+n), provenientes de revisiones manuales,
    disputas de clientes, o confirmaciones automáticas.

    Contrato:
    ---------
    - Consumir labels que llegan tiempo después de la transacción.
    - Unir label con predicción original (join por transaction_id).
    - Manejar labels que llegan fuera de orden.

    Flujo de Delayed Labels:
    -----------------------
    1. T+0: Transacción → Predicción (score: 0.85) → Guardar en PredictionRepository.
    2. T+24h: Label confirmada (is_fraud: True) → Llega al LabelStream.
    3. Label Joiner: Busca predicción original en PredictionRepository.
    4. Extrae features originales (point-in-time correctness).
    5. Actualiza modelo: model.learn_one(features, label).
    6. Calcula métrica retrospectiva: ¿era correcta la predicción?

    Implementaciones:
    ----------------
    - KafkaLabelStreamAdapter: Consume de tópico Kafka "fraud-labels".
    - KinesisLabelStreamAdapter: Consume de stream AWS Kinesis.

    Manejo de Labels Fuera de TTL:
    ------------------------------
    Si una label llega después del TTL de PredictionRepository:
    - Loguear el evento (SLA de labels).
    - NO actualizar el modelo (contexto no disponible).
    - Incrementar métrica late_labels_count.
    """

    @abstractmethod
    async def consume(self) -> AsyncIterator[FraudLabel]:
        """
        Consume labels confirmadas del stream.

        Yields:
            FraudLabel: Label con transaction_id, is_fraud, confidence, source.

        Examples:
            >>> async for label in label_stream.consume():
            ...     metadata = await model_trainer.update_with_label(
            ...         label.transaction_id,
            ...         label
            ...     )
            ...     print(f"Modelo actualizado: {metadata.version}")
        """
        pass

    @abstractmethod
    async def commit_offset(self, label: FraudLabel) -> None:
        """
        Confirma el procesamiento exitoso de una label.

        Args:
            label: Label procesada exitosamente.

        Examples:
            >>> async for label in label_stream.consume():
            ...     try:
            ...         await model_trainer.update_with_label(label.transaction_id, label)
            ...         await label_stream.commit_offset(label)
            ...     except PredictionNotFoundException:
            ...         logger.warning(f"Predicción no encontrada: {label.transaction_id}")
            ...         await label_stream.commit_offset(label)  # Commitear igual
        """
        pass
