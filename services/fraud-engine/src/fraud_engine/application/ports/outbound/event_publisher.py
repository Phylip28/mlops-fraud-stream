"""Puerto outbound para publicación de eventos de dominio."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class DomainEvent:
    """
    Evento de dominio base.

    Attributes:
        event_id: Identificador único del evento.
        event_type: Tipo de evento (fraud_detected, model_updated, etc.).
        timestamp: Momento en que ocurrió el evento.
        payload: Datos del evento.
    """

    event_id: str
    event_type: str
    timestamp: datetime
    payload: dict[str, Any]


class EventPublisher(ABC):
    """
    Puerto outbound para publicación de eventos de dominio.

    Este puerto permite desacoplar componentes mediante eventos asíncronos.

    Contrato:
    ---------
    - Publicar eventos de forma asíncrona.
    - Garantizar at-least-once delivery.
    - Soportar schemas (Avro, Protobuf) para versionado.

    Casos de uso:
    ------------
    - FraudDetected (score > 0.8) → Notificar equipo de seguridad.
    - ModelUpdated → Actualizar dashboard de métricas.
    - LabelConfirmed → Audit trail de confirmaciones.
    - DriftDetected → Alertar sobre degradación del modelo.

    Implementaciones:
    ----------------
    - KafkaEventPublisher: Publica a tópico Kafka "domain-events".
    - SnsEventPublisher: Publica a AWS SNS.
    - RabbitMQEventPublisher: Publica a exchange RabbitMQ.

    Schema Registry:
    ---------------
    Los eventos deben seguir schemas registrados (Avro/Protobuf)
    para garantizar compatibilidad entre productores y consumidores.
    """

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """
        Publica un evento de dominio.

        Args:
            event: Evento del dominio (FraudDetected, ModelUpdated, etc.).

        Raises:
            IOError: Si falla la publicación.

        Examples:
            >>> event = DomainEvent(
            ...     event_id="evt_123",
            ...     event_type="fraud_detected",
            ...     timestamp=datetime.now(),
            ...     payload={"transaction_id": "txn_123", "score": 0.95}
            ... )
            >>> await event_publisher.publish(event)
        """
        pass

    @abstractmethod
    async def publish_batch(self, events: list[DomainEvent]) -> None:
        """
        Publica múltiples eventos en batch (más eficiente).

        Args:
            events: Lista de eventos a publicar.

        Examples:
            >>> events = [
            ...     DomainEvent(...),
            ...     DomainEvent(...),
            ... ]
            >>> await event_publisher.publish_batch(events)
        """
        pass
