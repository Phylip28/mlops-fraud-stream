"""Value Object para monto monetario con validaciones de negocio."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Amount:
    """
    Monto monetario de una transacción.

    Garantiza que los montos sean válidos según reglas de negocio.

    Attributes:
        value: Monto en formato Decimal para precisión.
        currency: Código de moneda ISO 4217 (ej. 'USD', 'EUR').

    Raises:
        ValueError: Si el monto es negativo o la moneda es inválida.
    """

    value: Decimal
    currency: str = "USD"

    def __post_init__(self) -> None:
        """Valida el monto y la moneda."""
        if self.value < Decimal("0"):
            raise ValueError(f"Amount no puede ser negativo: {self.value}")

        if self.value > Decimal("1000000000"):  # 1 billón
            raise ValueError(f"Amount excede el límite máximo: {self.value}")

        if not self.currency or len(self.currency) != 3:
            raise ValueError(f"Currency debe ser código ISO 4217 de 3 letras: {self.currency}")

        # Validar que sea mayúsculas
        object.__setattr__(self, "currency", self.currency.upper())

    def __str__(self) -> str:
        return f"{self.currency} {self.value:.2f}"

    def __repr__(self) -> str:
        return f"Amount(value={self.value}, currency='{self.currency}')"

    def is_suspicious(self) -> bool:
        """
        Determina si el monto es sospechoso según reglas de negocio.

        Returns:
            True si el monto está en rango sospechoso (ej. > $10,000).
        """
        return self.value > Decimal("10000")
