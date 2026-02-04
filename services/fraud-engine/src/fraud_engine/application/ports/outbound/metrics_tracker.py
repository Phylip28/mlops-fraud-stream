"""Puerto outbound para tracking de métricas."""

from abc import ABC, abstractmethod


class MetricsTracker(ABC):
    """
    Puerto outbound para tracking de métricas.

    Este puerto abstrae el sistema de observabilidad (Prometheus, DataDog, etc.).

    Contrato:
    ---------
    - Rastrear métricas de latencia (P50, P95, P99).
    - Rastrear métricas de ML (precision, recall, F1, AUC-ROC).
    - Rastrear métricas de negocio (fraudes detectados, falsos positivos).
    - Integración con Prometheus/Grafana.

    Métricas Críticas:
    -----------------
    **Operacionales:**
    - fraud_detection_latency_ms (histogram): Latencia de inferencia.
    - fraud_detection_total (counter): Total de predicciones.
    - model_update_count (counter): Actualizaciones del modelo.

    **ML:**
    - fraud_detection_score (gauge): Distribución de scores.
    - model_f1_score (gauge): F1-score del modelo.
    - model_drift_score (gauge): Nivel de concept drift.

    **Negocio:**
    - fraud_amount_blocked (counter): Monto $ bloqueado.
    - false_positives_count (counter): Transacciones legítimas bloqueadas.
    - label_lag_seconds (histogram): Lag de labels confirmadas.

    Implementaciones:
    ----------------
    - PrometheusMetricsAdapter: Expone métricas en formato Prometheus.
    - DataDogMetricsAdapter: Envía métricas a DataDog.
    - CloudWatchMetricsAdapter: Envía métricas a AWS CloudWatch.
    """

    @abstractmethod
    async def track_latency(self, operation: str, latency_ms: float) -> None:
        """
        Registra la latencia de una operación.

        Args:
            operation: Nombre de la operación (fraud_detection, model_update, etc.).
            latency_ms: Latencia en milisegundos.

        Examples:
            >>> start = time.time()
            >>> prediction = await fraud_detector.detect(transaction)
            >>> latency_ms = (time.time() - start) * 1000
            >>> await metrics_tracker.track_latency("fraud_detection", latency_ms)
        """
        pass

    @abstractmethod
    async def track_prediction(
        self,
        score: float,
        actual_label: bool | None = None,
    ) -> None:
        """
        Registra una predicción (y opcionalmente su label real).

        Args:
            score: Score de fraude (0-1).
            actual_label: Label real (None si aún no está disponible).

        Examples:
            >>> await metrics_tracker.track_prediction(score=0.85, actual_label=None)
            >>>
            >>> # Cuando llega la label:
            >>> await metrics_tracker.track_prediction(score=0.85, actual_label=True)
        """
        pass

    @abstractmethod
    async def track_model_metrics(self, metrics: dict[str, float]) -> None:
        """
        Registra métricas del modelo (precision, recall, F1).

        Args:
            metrics: Diccionario con métricas calculadas.

        Examples:
            >>> metrics = {
            ...     "precision": 0.87,
            ...     "recall": 0.91,
            ...     "f1": 0.89,
            ...     "auc_roc": 0.94,
            ... }
            >>> await metrics_tracker.track_model_metrics(metrics)
        """
        pass

    @abstractmethod
    async def increment_counter(self, metric_name: str, value: int = 1) -> None:
        """
        Incrementa un contador.

        Args:
            metric_name: Nombre de la métrica.
            value: Valor a incrementar (default: 1).

        Examples:
            >>> await metrics_tracker.increment_counter("model_updates_total")
            >>> await metrics_tracker.increment_counter("fraud_amount_blocked", value=1500)
        """
        pass

    @abstractmethod
    async def set_gauge(self, metric_name: str, value: float) -> None:
        """
        Establece el valor de un gauge.

        Args:
            metric_name: Nombre de la métrica.
            value: Valor actual.

        Examples:
            >>> await metrics_tracker.set_gauge("model_f1_score", 0.89)
            >>> await metrics_tracker.set_gauge("model_drift_score", 0.15)
        """
        pass
