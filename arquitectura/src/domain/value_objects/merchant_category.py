"""Value Object para categoría de comerciante."""

from dataclasses import dataclass
from enum import Enum


class MerchantCategoryCode(str, Enum):
    """
    Códigos MCC (Merchant Category Code) estándar de la industria.

    Basado en ISO 18245.
    """

    RETAIL = "5411"  # Tiendas de abarrotes
    RESTAURANTS = "5812"  # Restaurantes
    GAS_STATIONS = "5541"  # Gasolineras
    HOTELS = "7011"  # Hoteles
    AIRLINES = "4511"  # Aerolíneas
    ONLINE_RETAIL = "5964"  # Comercio electrónico
    ATM_CASH = "6011"  # Cajeros automáticos
    CRYPTOCURRENCY = "6051"  # Criptomonedas (alto riesgo)
    GAMBLING = "7995"  # Apuestas (alto riesgo)
    UNKNOWN = "0000"  # Categoría desconocida


@dataclass(frozen=True)
class MerchantCategory:
    """
    Categoría de comerciante con nivel de riesgo.

    Attributes:
        code: Código MCC.
        name: Nombre descriptivo de la categoría.

    Raises:
        ValueError: Si el código MCC es inválido.
    """

    code: MerchantCategoryCode
    name: str = ""

    def __post_init__(self) -> None:
        """Inicializa el nombre si no se provee."""
        if not self.name:
            object.__setattr__(self, "name", self._get_name_from_code())

    def _get_name_from_code(self) -> str:
        """Obtiene el nombre descriptivo del código MCC."""
        mapping = {
            MerchantCategoryCode.RETAIL: "Retail/Abarrotes",
            MerchantCategoryCode.RESTAURANTS: "Restaurantes",
            MerchantCategoryCode.GAS_STATIONS: "Gasolineras",
            MerchantCategoryCode.HOTELS: "Hoteles",
            MerchantCategoryCode.AIRLINES: "Aerolíneas",
            MerchantCategoryCode.ONLINE_RETAIL: "Comercio Electrónico",
            MerchantCategoryCode.ATM_CASH: "Cajero Automático",
            MerchantCategoryCode.CRYPTOCURRENCY: "Criptomonedas",
            MerchantCategoryCode.GAMBLING: "Apuestas",
            MerchantCategoryCode.UNKNOWN: "Desconocido",
        }
        return mapping.get(self.code, "Otra Categoría")

    def is_high_risk(self) -> bool:
        """
        Determina si la categoría es de alto riesgo para fraude.

        Returns:
            True si la categoría tiene alto riesgo de fraude.
        """
        high_risk_categories = {
            MerchantCategoryCode.CRYPTOCURRENCY,
            MerchantCategoryCode.GAMBLING,
            MerchantCategoryCode.ONLINE_RETAIL,
            MerchantCategoryCode.UNKNOWN,
        }
        return self.code in high_risk_categories

    def __str__(self) -> str:
        return f"{self.name} ({self.code.value})"

    def __repr__(self) -> str:
        return f"MerchantCategory(code={self.code}, name='{self.name}')"
