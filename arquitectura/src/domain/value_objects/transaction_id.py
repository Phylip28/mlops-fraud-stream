"""Value Object para identificador de transacción."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TransactionId:
    """
    Identificador único de transacción.

    Inmutable para garantizar la integridad referencial.

    Attributes:
        value: String con el ID de la transacción.

    Raises:
        ValueError: Si el ID está vacío o es inválido.
    """

    value: str

    def __post_init__(self) -> None:
        """Valida el ID de transacción."""
        if not self.value or not self.value.strip():
            raise ValueError("Transaction ID no puede estar vacío")
        if len(self.value) > 100:
            raise ValueError("Transaction ID no puede exceder 100 caracteres")

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"TransactionId(value='{self.value}')"
