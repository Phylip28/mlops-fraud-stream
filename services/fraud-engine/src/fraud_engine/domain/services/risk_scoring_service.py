"""Domain Service para combinación de múltiples señales de riesgo."""

from ..entities import Transaction
from ..value_objects import FraudScore


class RiskScoringService:
    """
    Domain Service que combina múltiples señales para calcular riesgo final.

    Este servicio encapsula la lógica de negocio para combinar:
    - Score del modelo ML.
    - Reglas heurísticas de negocio.
    - Señales externas (listas negras, reputación, etc.).

    Responsabilidades:
    -----------------
    - Combinar score del modelo ML con reglas de negocio.
    - Aplicar ponderaciones según contexto.
    - Determinar nivel de riesgo (bajo, medio, alto, crítico).
    - Generar explicación del score (para auditoría).

    Principio SOLID:
    ---------------
    Single Responsibility: Este servicio solo combina señales de riesgo.
    NO hace inferencia ML, NO persiste datos, NO publica eventos.
    """

    def __init__(
        self,
        ml_weight: float = 0.7,
        heuristic_weight: float = 0.3,
    ) -> None:
        """
        Inicializa el servicio de scoring de riesgo.

        Args:
            ml_weight: Peso del score del modelo ML (0.0 - 1.0).
            heuristic_weight: Peso de las reglas heurísticas (0.0 - 1.0).

        Raises:
            ValueError: Si los pesos no suman 1.0.
        """
        if not abs((ml_weight + heuristic_weight) - 1.0) < 1e-6:
            raise ValueError(f"Pesos deben sumar 1.0: ml={ml_weight}, heuristic={heuristic_weight}")

        self.ml_weight = ml_weight
        self.heuristic_weight = heuristic_weight

    def combine_scores(
        self,
        ml_score: FraudScore,
        transaction: Transaction,
    ) -> FraudScore:
        """
        Combina el score del modelo ML con heurísticas de negocio.

        Args:
            ml_score: Score del modelo ML.
            transaction: Transacción evaluada.

        Returns:
            FraudScore combinado final.

        Examples:
            >>> service = RiskScoringService(ml_weight=0.7, heuristic_weight=0.3)
            >>> ml_score = FraudScore(value=0.85)
            >>> final_score = service.combine_scores(ml_score, transaction)
            >>> print(final_score)
            FraudScore(value=0.87)
        """
        heuristic_score = self._calculate_heuristic_score(transaction)

        # Combinación ponderada
        combined_value = (
            self.ml_weight * ml_score.value +
            self.heuristic_weight * heuristic_score.value
        )

        return FraudScore.from_model_output(combined_value)

    def _calculate_heuristic_score(self, transaction: Transaction) -> FraudScore:
        """
        Calcula score basado en reglas heurísticas.

        Returns:
            FraudScore heurístico.
        """
        score = 0.0

        # Heurística 1: Monto sospechoso
        if transaction.amount.is_suspicious():
            score += 0.3

        # Heurística 2: Categoría de alto riesgo
        if transaction.merchant_category.is_high_risk():
            score += 0.4

        # Heurística 3: Hora sospechosa (nocturno)
        hour = transaction.timestamp.hour
        if hour < 6 or hour > 23:
            score += 0.2

        # Heurística 4: Canal de alto riesgo
        if transaction.channel == "online":
            score += 0.1

        return FraudScore.from_model_output(min(1.0, score))

    def get_risk_level(self, score: FraudScore) -> str:
        """
        Determina el nivel de riesgo categórico.

        Args:
            score: Score de fraude.

        Returns:
            Nivel de riesgo: "low", "medium", "high", "critical".

        Examples:
            >>> level = service.get_risk_level(FraudScore(0.95))
            >>> print(level)
            "critical"
        """
        if score.value >= 0.9:
            return "critical"
        elif score.value >= 0.8:
            return "high"
        elif score.value >= 0.5:
            return "medium"
        else:
            return "low"

    def generate_explanation(
        self,
        ml_score: FraudScore,
        transaction: Transaction,
        final_score: FraudScore,
    ) -> dict[str, str | float]:
        """
        Genera explicación del score para auditoría.

        Args:
            ml_score: Score del modelo ML.
            transaction: Transacción evaluada.
            final_score: Score final combinado.

        Returns:
            Diccionario con explicación de los factores.

        Examples:
            >>> explanation = service.generate_explanation(ml_score, transaction, final_score)
            >>> print(explanation["risk_factors"])
            ["high_risk_category", "suspicious_amount", "night_transaction"]
        """
        risk_factors = []

        if transaction.amount.is_suspicious():
            risk_factors.append("suspicious_amount")

        if transaction.merchant_category.is_high_risk():
            risk_factors.append("high_risk_category")

        if transaction.is_suspicious():
            risk_factors.append("suspicious_transaction")

        return {
            "ml_score": float(ml_score.value),
            "heuristic_contribution": self.heuristic_weight * float(ml_score.value),
            "final_score": float(final_score.value),
            "risk_level": self.get_risk_level(final_score),
            "risk_factors": risk_factors,
        }
