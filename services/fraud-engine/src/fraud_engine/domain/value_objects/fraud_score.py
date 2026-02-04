"""Value Object para score de fraude con invariantes."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FraudScore:
    """
    Score de probabilidad de fraude.

    Garantiza invariantes: score entre 0.0 y 1.0.

    Attributes:
        value: Probabilidad de fraude entre 0.0 (no fraude) y 1.0 (fraude seguro).

    Raises:
        ValueError: Si el score está fuera del rango [0.0, 1.0].
    """

    value: float

    def __post_init__(self) -> None:
        """Valida que el score esté en el rango válido."""
        if not 0.0 <= self.value <= 1.0:
            raise ValueError(f"FraudScore debe estar entre 0.0 y 1.0, recibido: {self.value}")

    def __str__(self) -> str:
        return f"{self.value:.4f}"

    def __repr__(self) -> str:
        return f"FraudScore(value={self.value})"

    def __float__(self) -> float:
        return self.value

    def is_high_risk(self, threshold: float = 0.8) -> bool:
        """
        Determina si el score indica alto riesgo de fraude.

        Args:
            threshold: Umbral de decisión (default: 0.8).

        Returns:
            True si el score supera el umbral.
        """
        return self.value >= threshold

    def is_medium_risk(self, low: float = 0.5, high: float = 0.8) -> bool:
        """
        Determina si el score indica riesgo medio.

        Args:
            low: Umbral inferior (default: 0.5).
            high: Umbral superior (default: 0.8).

        Returns:
            True si el score está en el rango medio.
        """
        return low <= self.value < high

    def is_low_risk(self, threshold: float = 0.5) -> bool:
        """
        Determina si el score indica bajo riesgo.

        Args:
            threshold: Umbral de decisión (default: 0.5).

        Returns:
            True si el score está por debajo del umbral.
        """
        return self.value < threshold

    @classmethod
    def from_model_output(cls, raw_score: float) -> "FraudScore":
        """
        Factory method para crear FraudScore desde salida del modelo.

        Args:
            raw_score: Score crudo del modelo (puede estar fuera de rango).

        Returns:
            FraudScore normalizado entre 0.0 y 1.0.
        """
        # Normalizar si está fuera de rango
        normalized = max(0.0, min(1.0, raw_score))
        return cls(value=normalized)
