"""Entidad FraudLabel - Representa una label confirmada (delayed label)."""

from dataclasses import dataclass
from datetime import datetime

from ..value_objects import TransactionId


@dataclass
class FraudLabel:
    """
    Entidad que representa una label de fraude confirmada.

    Esta entidad encapsula las delayed labels que llegan tiempo después
    de la transacción original, provenientes de revisiones manuales,
    disputas de clientes, o confirmaciones automáticas.

    Attributes:
        transaction_id: ID de la transacción original.
        is_fraud: True si se confirmó como fraude, False si es legítima.
        confidence: Nivel de confianza de la label (0.0 - 1.0).
        source: Fuente de la label (manual_review, api, customer_dispute, etc.).
        reviewed_by: ID del analista o sistema que confirmó (opcional).
        timestamp: Momento en que se confirmó la label.
        notes: Notas adicionales sobre la confirmación.

    Invariantes:
        - confidence debe estar entre 0.0 y 1.0
        - source no puede estar vacío
    """

    transaction_id: TransactionId
    is_fraud: bool
    confidence: float
    source: str
    timestamp: datetime
    reviewed_by: str | None = None
    notes: str | None = None

    def __post_init__(self) -> None:
        """Valida invariantes de la label."""
        self._validate()

    def _validate(self) -> None:
        """
        Valida reglas de negocio de la label.

        Raises:
            ValueError: Si alguna invariante se viola.
        """
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                f"Confidence debe estar entre 0.0 y 1.0, recibido: {self.confidence}"
            )

        if not self.source or not self.source.strip():
            raise ValueError("Source no puede estar vacío")

        valid_sources = {
            "manual_review",
            "api",
            "customer_dispute",
            "automated_confirmation",
            "chargeback",
        }
        if self.source not in valid_sources:
            raise ValueError(
                f"Source inválido: {self.source}. Debe ser uno de {valid_sources}"
            )

    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """
        Determina si la label tiene alta confianza.

        Args:
            threshold: Umbral de confianza (default: 0.8).

        Returns:
            True si la confianza supera el umbral.
        """
        return self.confidence >= threshold

    def is_from_manual_review(self) -> bool:
        """
        Determina si la label proviene de revisión manual.

        Returns:
            True si fue revisada manualmente por un analista.
        """
        return self.source == "manual_review"

    def __repr__(self) -> str:
        fraud_str = "FRAUD" if self.is_fraud else "LEGIT"
        return (
            f"FraudLabel(transaction={self.transaction_id}, "
            f"{fraud_str}, "
            f"confidence={self.confidence:.2f}, "
            f"source={self.source})"
        )
