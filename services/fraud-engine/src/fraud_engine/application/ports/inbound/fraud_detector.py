"""Puerto inbound para detección de fraude."""

from abc import ABC, abstractmethod

from src.domain.entities import Prediction, Transaction


class FraudDetector(ABC):
    """
    Puerto inbound para detección de fraude en transacciones.

    Este puerto define el contrato para el caso de uso de detección de fraude.
    Los adaptadores inbound (API REST, Kafka Consumer) implementarán llamadas
    a este puerto.

    Contrato:
    ---------
    - Recibe una transacción validada.
    - Retorna una predicción con score de fraude (0-1).
    - Debe ser idempotente: misma transacción → mismo resultado en ventana temporal.
    - Latencia objetivo: P99 < 50ms.

    Invariantes:
    -----------
    - La transacción debe estar validada antes de llamar a detect().
    - El modelo debe estar inicializado y listo.
    - Las features deben estar disponibles en el Feature Store.

    Excepciones:
    -----------
    - ModelNotReadyException: Si el modelo no está inicializado.
    - FeatureMissingException: Si faltan features críticas.
    - InvalidTransactionException: Si la transacción es inválida.
    """

    @abstractmethod
    async def detect(self, transaction: Transaction) -> Prediction:
        """
        Detecta fraude en una transacción.

        Este método orquesta:
        1. Extracción de features desde Feature Store.
        2. Inferencia del modelo ML.
        3. Aplicación de reglas de negocio.
        4. Persistencia de la predicción.
        5. Publicación de eventos si score > umbral.

        Args:
            transaction: Entidad Transaction validada del dominio.

        Returns:
            Prediction: Predicción con fraud_score, model_version, features_used.

        Raises:
            ModelNotReadyException: Si el modelo no está inicializado.
            FeatureMissingException: Si faltan features críticas.
            InvalidTransactionException: Si la transacción viola reglas de negocio.

        Examples:
            >>> detector = DetectFraudUseCase(...)
            >>> transaction = Transaction(...)
            >>> prediction = await detector.detect(transaction)
            >>> print(prediction.fraud_score)
            FraudScore(value=0.85)
        """
        pass
