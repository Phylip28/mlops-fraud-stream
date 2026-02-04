"""Entidad Transaction - Representa una transacción financiera."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ..exceptions import InvalidTransactionException
from ..value_objects import Amount, MerchantCategory, TransactionId


@dataclass
class Transaction:
    """
    Entidad que representa una transacción financiera.

    Esta es la entidad principal sobre la que se realiza la detección de fraude.

    Attributes:
        transaction_id: Identificador único de la transacción.
        timestamp: Momento en que ocurrió la transacción.
        amount: Monto de la transacción.
        merchant_id: ID del comerciante.
        merchant_category: Categoría del comerciante.
        customer_id: ID del cliente que realizó la transacción.
        location: Ubicación geográfica (ej. código de país).
        channel: Canal de transacción (online, pos, atm).
        device_id: ID del dispositivo usado (opcional).
        additional_data: Datos adicionales específicos del negocio.

    Raises:
        InvalidTransactionException: Si la transacción no cumple reglas de negocio.
    """

    transaction_id: TransactionId
    timestamp: datetime
    amount: Amount
    merchant_id: str
    merchant_category: MerchantCategory
    customer_id: str
    location: str = "US"
    channel: str = "online"
    device_id: str | None = None
    additional_data: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Valida la transacción según reglas de negocio."""
        self._validate()

    def _validate(self) -> None:
        """
        Valida reglas de negocio de la transacción.

        Raises:
            InvalidTransactionException: Si alguna regla se viola.
        """
        # Validar IDs no vacíos
        if not self.merchant_id or not self.merchant_id.strip():
            raise InvalidTransactionException("Merchant ID no puede estar vacío")

        if not self.customer_id or not self.customer_id.strip():
            raise InvalidTransactionException("Customer ID no puede estar vacío")

        # Validar timestamp no futuro
        if self.timestamp > datetime.now():
            raise InvalidTransactionException(
                f"Timestamp de transacción no puede ser futuro: {self.timestamp}"
            )

        # Validar canal
        valid_channels = {"online", "pos", "atm", "mobile"}
        if self.channel not in valid_channels:
            raise InvalidTransactionException(
                f"Canal inválido: {self.channel}. Debe ser uno de {valid_channels}"
            )

        # Validar ubicación
        if not self.location or len(self.location) != 2:
            raise InvalidTransactionException(
                f"Location debe ser código de país ISO 3166-1 alpha-2: {self.location}"
            )

    def is_suspicious(self) -> bool:
        """
        Aplica reglas heurísticas básicas para detectar transacciones sospechosas.

        Esta es una validación preliminar. El modelo ML realizará el análisis completo.

        Returns:
            True si la transacción es sospechosa según reglas de negocio.
        """
        # Regla 1: Monto sospechoso
        if self.amount.is_suspicious():
            return True

        # Regla 2: Categoría de alto riesgo
        if self.merchant_category.is_high_risk():
            return True

        # Regla 3: Transacciones nocturnas (fuera de horario típico)
        hour = self.timestamp.hour
        if hour < 6 or hour > 23:
            return True

        return False

    def to_feature_dict(self) -> dict[str, Any]:
        """
        Convierte la transacción a un diccionario de features para el modelo ML.

        Returns:
            Diccionario con features extraídas de la transacción.
        """
        return {
            "transaction_id": str(self.transaction_id),
            "amount": float(self.amount.value),
            "currency": self.amount.currency,
            "merchant_category_code": self.merchant_category.code.value,
            "is_high_risk_category": self.merchant_category.is_high_risk(),
            "hour_of_day": self.timestamp.hour,
            "day_of_week": self.timestamp.weekday(),
            "is_weekend": self.timestamp.weekday() >= 5,
            "channel": self.channel,
            "location": self.location,
            "has_device_id": self.device_id is not None,
            "timestamp": self.timestamp.isoformat(),
        }

    def __repr__(self) -> str:
        return (
            f"Transaction(id={self.transaction_id}, "
            f"amount={self.amount}, "
            f"merchant={self.merchant_id}, "
            f"timestamp={self.timestamp.isoformat()})"
        )
