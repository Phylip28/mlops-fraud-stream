"""Domain Service para lógica de detección de fraude."""

from typing import Any

from ..entities import Prediction, Transaction
from ..exceptions import FeatureMissingException, ModelNotReadyException
from ..value_objects import FraudScore


class FraudDetectionService:
    """
    Domain Service que orquesta la detección de fraude.

    Este servicio encapsula la lógica de negocio para detectar fraude,
    combinando el modelo ML con reglas heurísticas de negocio.

    Responsabilidades:
    -----------------
    - Aplicar reglas de negocio (umbrales, listas negras, patrones sospechosos).
    - Coordinar la inferencia del modelo ML.
    - Combinar score del modelo con reglas heurísticas.
    - Generar la predicción final con metadata.

    Principio SOLID:
    ---------------
    Single Responsibility: Este servicio solo detecta fraude.
    NO persiste predicciones, NO publica eventos, NO extrae features.
    Esas responsabilidades corresponden al Application Layer (Use Cases).
    """

    def __init__(
        self,
        model: Any,  # Tipo genérico para no depender de river directamente
        high_risk_threshold: float = 0.8,
        medium_risk_threshold: float = 0.5,
    ) -> None:
        """
        Inicializa el servicio de detección de fraude.

        Args:
            model: Modelo ML (ej. pipeline de river).
            high_risk_threshold: Umbral para clasificar como alto riesgo.
            medium_risk_threshold: Umbral para clasificar como riesgo medio.

        Raises:
            ValueError: Si los umbrales son inválidos.
        """
        if not 0.0 < medium_risk_threshold < high_risk_threshold <= 1.0:
            raise ValueError(
                f"Umbrales inválidos: medium={medium_risk_threshold}, high={high_risk_threshold}"
            )

        self.model = model
        self.high_risk_threshold = high_risk_threshold
        self.medium_risk_threshold = medium_risk_threshold
        self._is_ready = model is not None

    def detect(
        self,
        transaction: Transaction,
        features: dict[str, Any],
        model_version: str,
    ) -> Prediction:
        """
        Detecta fraude en una transacción.

        Aplica reglas de negocio y ejecuta la inferencia del modelo.

        Args:
            transaction: Transacción a evaluar.
            features: Features extraídas para el modelo.
            model_version: Versión del modelo utilizado.

        Returns:
            Prediction con score de fraude y metadata.

        Raises:
            ModelNotReadyException: Si el modelo no está inicializado.
            FeatureMissingException: Si faltan features críticas.

        Examples:
            >>> service = FraudDetectionService(model=river_model)
            >>> prediction = service.detect(transaction, features, "v1.2.3")
            >>> print(prediction.fraud_score)
            FraudScore(value=0.85)
        """
        if not self._is_ready:
            raise ModelNotReadyException("El modelo no está inicializado")

        # Validar features críticas
        self._validate_features(features)

        # Aplicar reglas heurísticas pre-modelo
        if self._apply_business_rules(transaction):
            # Transacción bloqueada por reglas de negocio (sin consultar modelo)
            fraud_score = FraudScore(value=1.0)
            return self._create_prediction(
                transaction, fraud_score, features, model_version, ruled_by="business_rule"
            )

        # Inferencia del modelo ML
        try:
            raw_score = self._predict_with_model(features)
            fraud_score = FraudScore.from_model_output(raw_score)
        except Exception as e:
            # Si el modelo falla, usar score conservador
            fraud_score = FraudScore(value=0.5)
            # En producción, esto debería loguearse y monitorearse

        # Aplicar reglas post-modelo (ajustes basados en contexto)
        adjusted_score = self._adjust_score_with_context(fraud_score, transaction)

        return self._create_prediction(
            transaction, adjusted_score, features, model_version
        )

    def _validate_features(self, features: dict[str, Any]) -> None:
        """
        Valida que todas las features críticas estén presentes.

        Args:
            features: Diccionario de features.

        Raises:
            FeatureMissingException: Si faltan features críticas.
        """
        required_features = ["amount", "merchant_category_code", "hour_of_day"]
        missing = [f for f in required_features if f not in features]

        if missing:
            raise FeatureMissingException(missing)

    def _apply_business_rules(self, transaction: Transaction) -> bool:
        """
        Aplica reglas de negocio heurísticas.

        Returns:
            True si la transacción debe ser bloqueada automáticamente.
        """
        # Regla 1: Montos extremadamente altos
        if transaction.amount.value > 50000:
            return True

        # Regla 2: Categorías prohibidas
        # (ejemplo: si detectamos ciertos MCCs en lista negra)
        # Este es un placeholder - en producción vendría de una BD/config

        # Regla 3: Múltiples banderas rojas simultáneas
        red_flags = sum([
            transaction.amount.is_suspicious(),
            transaction.merchant_category.is_high_risk(),
            transaction.is_suspicious(),  # Heurísticas de Transaction
        ])

        return red_flags >= 3  # 3 o más red flags → bloqueo automático

    def _predict_with_model(self, features: dict[str, Any]) -> float:
        """
        Ejecuta la inferencia del modelo ML.

        Args:
            features: Features para el modelo.

        Returns:
            Score crudo del modelo (puede estar fuera del rango 0-1).
        """
        # En producción, esto sería algo como:
        # score = self.model.predict_proba_one(features)
        # Por ahora, placeholder para mantener desacoplamiento
        # (el wrapper de river se implementará en infrastructure)

        # Placeholder: simular predicción
        # En realidad, llamarías a self.model.predict_proba_one(features)
        if hasattr(self.model, "predict_proba_one"):
            proba = self.model.predict_proba_one(features)
            # river retorna dict {False: 0.3, True: 0.7}
            return proba.get(True, 0.0)
        else:
            # Fallback si no hay modelo real (para tests)
            return 0.5

    def _adjust_score_with_context(
        self,
        score: FraudScore,
        transaction: Transaction,
    ) -> FraudScore:
        """
        Ajusta el score basándose en contexto adicional.

        Args:
            score: Score original del modelo.
            transaction: Transacción evaluada.

        Returns:
            FraudScore ajustado.
        """
        adjusted_value = score.value

        # Ajuste 1: Aumentar score para categorías de alto riesgo
        if transaction.merchant_category.is_high_risk():
            adjusted_value = min(1.0, adjusted_value * 1.2)

        # Ajuste 2: Reducir score para transacciones pequeñas
        if transaction.amount.value < 10:
            adjusted_value = adjusted_value * 0.8

        return FraudScore.from_model_output(adjusted_value)

    def _create_prediction(
        self,
        transaction: Transaction,
        fraud_score: FraudScore,
        features: dict[str, Any],
        model_version: str,
        ruled_by: str | None = None,
    ) -> Prediction:
        """
        Crea la entidad Prediction con metadata completa.

        Args:
            transaction: Transacción evaluada.
            fraud_score: Score de fraude calculado.
            features: Features utilizadas.
            model_version: Versión del modelo.
            ruled_by: Indica si fue decidido por regla de negocio (opcional).

        Returns:
            Entidad Prediction completa.
        """
        return Prediction(
            prediction_id=str(transaction.transaction_id),
            transaction_id=transaction.transaction_id,
            fraud_score=fraud_score,
            model_version=model_version,
            timestamp=transaction.timestamp,
            features_used=features.copy(),  # Snapshot de features (point-in-time)
        )
