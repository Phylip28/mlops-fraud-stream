"""Puerto outbound para Feature Store."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from src.domain.value_objects import TransactionId


class FeatureStore(ABC):
    """
    Puerto outbound para Feature Store.

    Garantiza consistencia entre features de entrenamiento e inferencia
    mediante point-in-time correctness.

    Contrato:
    ---------
    - Garantizar consistencia entre features de entrenamiento e inferencia.
    - Soportar features de ventana temporal (ej. "transacciones últimas 24h").
    - Point-in-time correctness: features al momento T, no futuras.

    Implementaciones:
    ----------------
    - FeastFeatureStoreAdapter: Integración con Feast.
    - RedisFeatureStoreAdapter: Cache in-memory (online features).
    - PostgresFeatureStoreAdapter: Features batch para análisis.

    Tipos de Features:
    -----------------
    1. **Online Features**: Pre-computadas en Redis para inferencia rápida.
       Ejemplo: merchant_avg_amount_7d, customer_transaction_count_24h.

    2. **Batch Features**: Calculadas offline para re-training.
       Ejemplo: merchant_fraud_rate_30d (histórico).

    3. **Real-time Features**: Calculadas on-the-fly desde el stream.
       Ejemplo: transaction_velocity (transacciones/minuto).

    Point-in-Time Correctness:
    -------------------------
    Cuando se recuperan features para training, deben ser las features
    disponibles en el momento T de la predicción original, NO features
    futuras que causarían data leakage.
    """

    @abstractmethod
    async def get_online_features(
        self,
        transaction_id: TransactionId,
        feature_names: list[str],
        timestamp: datetime,
    ) -> dict[str, Any]:
        """
        Obtiene features para inferencia online.

        Args:
            transaction_id: ID de la transacción.
            feature_names: Lista de features a recuperar.
            timestamp: Timestamp de la transacción (point-in-time).

        Returns:
            Diccionario {feature_name: value}.

        Raises:
            FeatureMissingException: Si falta una feature crítica.
            ValueError: Si el timestamp es inválido.

        Examples:
            >>> features = await feature_store.get_online_features(
            ...     transaction_id=TransactionId("txn_123"),
            ...     feature_names=["merchant_avg_amount_7d", "customer_transaction_count_24h"],
            ...     timestamp=datetime.now(),
            ... )
            >>> print(features)
            {
                "merchant_avg_amount_7d": 150.50,
                "customer_transaction_count_24h": 12
            }
        """
        pass

    @abstractmethod
    async def write_features(
        self,
        transaction_id: TransactionId,
        features: dict[str, Any],
        timestamp: datetime,
    ) -> None:
        """
        Escribe features al store.

        Args:
            transaction_id: ID de la transacción.
            features: Diccionario de features.
            timestamp: Timestamp de creación.

        Examples:
            >>> await feature_store.write_features(
            ...     transaction_id=TransactionId("txn_123"),
            ...     features={"merchant_avg_amount_7d": 150.50},
            ...     timestamp=datetime.now(),
            ... )
        """
        pass

    @abstractmethod
    async def get_feature_statistics(
        self,
        feature_name: str,
        window: str,  # "1h", "24h", "7d"
    ) -> dict[str, float]:
        """
        Retorna estadísticas de una feature (mean, std, min, max).

        Útil para:
        - Detección de drift.
        - Normalización dinámica.
        - Alertas de anomalías en features.

        Args:
            feature_name: Nombre de la feature.
            window: Ventana temporal ("1h", "24h", "7d").

        Returns:
            Diccionario con estadísticas {"mean": ..., "std": ..., "min": ..., "max": ...}.

        Examples:
            >>> stats = await feature_store.get_feature_statistics(
            ...     feature_name="transaction_amount",
            ...     window="24h",
            ... )
            >>> print(stats)
            {"mean": 125.50, "std": 45.20, "min": 10.00, "max": 500.00}
        """
        pass
