"""Domain Service para lógica de aprendizaje incremental."""

from datetime import datetime, timedelta
from typing import Any

from ..entities import ModelMetadata
from ..exceptions import ModelNotReadyException


class IncrementalLearningService:
    """
    Domain Service que decide cuándo y cómo actualizar el modelo.

    Este servicio encapsula la lógica de negocio para el stream learning,
    determinando políticas de re-entrenamiento y checkpoint.

    Responsabilidades:
    -----------------
    - Decidir cuándo actualizar el modelo (cada N transacciones, cada X tiempo).
    - Decidir cuándo hacer checkpoint (persistir estado).
    - Aplicar políticas de learning rate decay.
    - Detectar cuándo el modelo debe ser congelado (modo inference-only).

    Principio SOLID:
    ---------------
    Single Responsibility: Este servicio solo decide estrategias de learning.
    NO actualiza el modelo directamente, NO persiste, NO publica eventos.
    """

    def __init__(
        self,
        checkpoint_frequency: int = 100,
        snapshot_frequency: int = 1000,
        checkpoint_time_interval: timedelta = timedelta(minutes=5),
        drift_threshold: float = 0.3,
    ) -> None:
        """
        Inicializa el servicio de aprendizaje incremental.

        Args:
            checkpoint_frequency: Checkpoint cada N updates (Redis).
            snapshot_frequency: Snapshot cada N updates (S3).
            checkpoint_time_interval: Checkpoint cada X tiempo.
            drift_threshold: Umbral de drift para checkpoint forzado.
        """
        self.checkpoint_frequency = checkpoint_frequency
        self.snapshot_frequency = snapshot_frequency
        self.checkpoint_time_interval = checkpoint_time_interval
        self.drift_threshold = drift_threshold

        self._updates_since_last_checkpoint = 0
        self._updates_since_last_snapshot = 0
        self._last_checkpoint_time = datetime.now()

    def should_update_model(
        self,
        label_confidence: float,
        model_metadata: ModelMetadata,
    ) -> bool:
        """
        Determina si el modelo debe ser actualizado con esta label.

        Políticas:
        ---------
        - Solo actualizar si confidence > 0.7 (labels de alta confianza).
        - No actualizar si el modelo está en modo "frozen".
        - No actualizar si drift_score > umbral crítico.

        Args:
            label_confidence: Confianza de la label (0.0 - 1.0).
            model_metadata: Metadatos actuales del modelo.

        Returns:
            True si se debe actualizar el modelo.

        Examples:
            >>> service = IncrementalLearningService()
            >>> if service.should_update_model(label_confidence=0.95, metadata=metadata):
            ...     model.learn_one(features, label)
        """
        # Política 1: Solo labels de alta confianza
        if label_confidence < 0.7:
            return False

        # Política 2: No actualizar si el modelo está muy degradado
        if model_metadata.drift_score > 0.5:
            return False

        # Política 3: No actualizar si el modelo está "frozen"
        if not model_metadata.is_active:
            return False

        return True

    def should_trigger_checkpoint(
        self,
        force: bool = False,
    ) -> bool:
        """
        Determina si debe hacerse checkpoint del modelo.

        Triggers:
        --------
        1. Cada checkpoint_frequency updates (ej. cada 100).
        2. Cada checkpoint_time_interval (ej. cada 5 minutos).
        3. Si force=True (checkpoint manual).

        Args:
            force: Forzar checkpoint independiente de las políticas.

        Returns:
            True si se debe hacer checkpoint.

        Examples:
            >>> service = IncrementalLearningService(checkpoint_frequency=100)
            >>> # Después de 100 updates:
            >>> if service.should_trigger_checkpoint():
            ...     await model_repository.save(model, metadata)
            ...     service.mark_checkpoint_done()
        """
        if force:
            return True

        # Trigger 1: Frecuencia de updates
        if self._updates_since_last_checkpoint >= self.checkpoint_frequency:
            return True

        # Trigger 2: Intervalo de tiempo
        time_since_checkpoint = datetime.now() - self._last_checkpoint_time
        if time_since_checkpoint >= self.checkpoint_time_interval:
            return True

        return False

    def should_trigger_snapshot(self) -> bool:
        """
        Determina si debe hacerse snapshot completo del modelo (S3).

        Returns:
            True si se debe hacer snapshot.

        Examples:
            >>> # Después de 1000 updates:
            >>> if service.should_trigger_snapshot():
            ...     await s3_repository.save_snapshot(model, metadata)
            ...     service.mark_snapshot_done()
        """
        return self._updates_since_last_snapshot >= self.snapshot_frequency

    def mark_update_done(self) -> None:
        """
        Registra que se completó una actualización del modelo.

        Debe llamarse después de cada learn_one().
        """
        self._updates_since_last_checkpoint += 1
        self._updates_since_last_snapshot += 1

    def mark_checkpoint_done(self) -> None:
        """
        Registra que se completó un checkpoint.

        Debe llamarse después de guardar en Redis.
        """
        self._updates_since_last_checkpoint = 0
        self._last_checkpoint_time = datetime.now()

    def mark_snapshot_done(self) -> None:
        """
        Registra que se completó un snapshot.

        Debe llamarse después de guardar en S3.
        """
        self._updates_since_last_snapshot = 0

    def get_learning_rate(
        self,
        model_metadata: ModelMetadata,
        base_learning_rate: float = 0.01,
    ) -> float:
        """
        Calcula el learning rate adaptativo basado en el estado del modelo.

        Política:
        --------
        - Learning rate decae con el tiempo (modelo más estable → updates más conservadores).
        - Si drift_score > umbral, aumentar learning rate (adaptarse más rápido).

        Args:
            model_metadata: Metadatos del modelo.
            base_learning_rate: Learning rate base.

        Returns:
            Learning rate ajustado.

        Examples:
            >>> lr = service.get_learning_rate(metadata)
            >>> # Usar lr para configurar el modelo (si el modelo lo soporta)
        """
        # Decay basado en número de samples
        decay_factor = 1.0 / (1.0 + 0.0001 * model_metadata.training_samples_count)

        # Ajuste por drift
        drift_multiplier = 1.0
        if model_metadata.drift_score > self.drift_threshold:
            drift_multiplier = 1.5  # Aprender más rápido cuando hay drift

        return base_learning_rate * decay_factor * drift_multiplier

    def should_freeze_model(self, model_metadata: ModelMetadata) -> bool:
        """
        Determina si el modelo debe ser congelado (modo inference-only).

        Casos:
        -----
        - Drift score > umbral crítico → Congelar y alertar.
        - F1-score < umbral mínimo → Congelar y revertir a versión anterior.

        Args:
            model_metadata: Metadatos del modelo.

        Returns:
            True si el modelo debe ser congelado.

        Examples:
            >>> if service.should_freeze_model(metadata):
            ...     logger.alert("⚠️ Modelo congelado por degradación")
            ...     await model_repository.load(version="previous_stable")
        """
        # Condición 1: Drift crítico
        if model_metadata.drift_score > 0.5:
            return True

        # Condición 2: Performance degradado
        f1_score = model_metadata.get_metric("f1", 0.0)
        if f1_score < 0.5:
            return True

        return False
