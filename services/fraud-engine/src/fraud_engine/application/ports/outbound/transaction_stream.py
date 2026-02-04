"""Puerto outbound para consumo de stream de transacciones."""

from abc import ABC, abstractmethod
from typing import AsyncIterator

from src.domain.entities import Transaction


class TransactionStream(ABC):
    """
    Puerto outbound para consumo de transacciones desde stream.

    Este puerto abstrae la lectura de transacciones desde un sistema
    de streaming (Kafka, Kinesis, RabbitMQ).

    Contrato:
    ---------
    - Consumir transacciones en orden (si partición única) o paralelo (multi-partición).
    - Manejar backpressure (no colapsar si procesamiento es lento).
    - Garantizar at-least-once delivery (idempotencia del lado del consumer).

    Implementaciones:
    ----------------
    - KafkaTransactionStreamAdapter: Consume de Kafka.
    - KinesisTransactionStreamAdapter: Consume de AWS Kinesis.
    - RabbitMQTransactionStreamAdapter: Consume de RabbitMQ.

    Manejo de Errores:
    -----------------
    - Transacción inválida → Loguear + enviar a DLQ + continuar.
    - Error de red → Reintentar con backoff exponencial.
    - Error de deserialización → Loguear + enviar a DLQ + continuar.

    Particionamiento:
    ----------------
    Para escalar, las transacciones se particionan por customer_id
    o merchant_id, garantizando orden por cliente/comerciante.
    """

    @abstractmethod
    async def consume(self) -> AsyncIterator[Transaction]:
        """
        Consume transacciones del stream.

        Yields:
            Transaction: Entidad validada del dominio.

        Examples:
            >>> async for transaction in stream.consume():
            ...     prediction = await fraud_detector.detect(transaction)
            ...     print(f"Score: {prediction.fraud_score}")
        """
        pass

    @abstractmethod
    async def commit_offset(self, transaction: Transaction) -> None:
        """
        Confirma el procesamiento exitoso de una transacción.

        Esto permite que el consumer avance el offset en el stream,
        garantizando at-least-once semantics.

        Args:
            transaction: Transacción procesada exitosamente.

        Examples:
            >>> async for transaction in stream.consume():
            ...     try:
            ...         prediction = await fraud_detector.detect(transaction)
            ...         await stream.commit_offset(transaction)
            ...     except Exception as e:
            ...         logger.error(f"Error: {e}")
            ...         # No commitear offset → reintento en siguiente poll
        """
        pass
