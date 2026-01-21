"""Puerto outbound para persistencia del modelo ML."""

from abc import ABC, abstractmethod

from src.domain.entities import ModelMetadata


class ModelRepository(ABC):
    """
    Puerto outbound para persistencia del modelo de river.

    Este puerto abstrae la persistencia del estado del modelo ML,
    permitiendo diferentes implementaciones (Redis, S3, PostgreSQL).

    Contrato:
    ---------
    - Guardar/Cargar el estado completo del modelo (pesos, estadísticas internas).
    - Soportar versionado (rollback si modelo nuevo degrada).
    - Operaciones atómicas (no estados parciales).

    Implementaciones:
    ----------------
    - RedisModelRepository: Estado en memoria (baja latencia < 10ms).
    - S3ModelSnapshotRepository: Snapshots periódicos (disaster recovery).
    - PostgresModelRepository: Metadata + referencia a S3.

    Estrategia Multi-Tier:
    ---------------------
    Tier 1 (Redis): Checkpoint cada 100 updates, TTL 24h.
    Tier 2 (S3): Snapshot cada 1000 updates, versionado completo.
    Tier 3 (PostgreSQL): Metadata y audit trail.

    Thread Safety:
    -------------
    Las implementaciones DEBEN ser thread-safe para soportar
    actualizaciones concurrentes del modelo.
    """

    @abstractmethod
    async def save(self, model: object, metadata: ModelMetadata) -> None:
        """
        Persiste el estado del modelo.

        El modelo es serializado (pickle/cloudpickle) y guardado junto
        con sus metadatos.

        Args:
            model: Instancia del modelo de river (será serializado).
            metadata: Metadatos (versión, métricas, timestamp, samples_count).

        Raises:
            IOError: Si falla la persistencia.
            ValueError: Si el modelo o metadata son inválidos.

        Examples:
            >>> repo = RedisModelRepository(redis_client)
            >>> metadata = ModelMetadata(version="v1.2.3", ...)
            >>> await repo.save(river_model, metadata)
        """
        pass

    @abstractmethod
    async def load(self, version: str | None = None) -> tuple[object, ModelMetadata]:
        """
        Carga el estado del modelo.

        Args:
            version: Versión específica a cargar (None = última versión activa).

        Returns:
            Tupla (modelo_deserializado, metadata).

        Raises:
            ModelNotFoundException: Si no existe la versión solicitada.
            IOError: Si falla la carga o deserialización.

        Examples:
            >>> model, metadata = await repo.load()  # Última versión
            >>> print(metadata.version)
            'v1.2.3'
            >>>
            >>> # Cargar versión específica (rollback)
            >>> model, metadata = await repo.load(version="v1.2.0")
        """
        pass

    @abstractmethod
    async def list_versions(self, limit: int = 10) -> list[ModelMetadata]:
        """
        Lista las últimas versiones del modelo disponibles.

        Útil para:
        - Auditoría de versiones.
        - Selección de versión para rollback.
        - Análisis de evolución del modelo.

        Args:
            limit: Número máximo de versiones a retornar.

        Returns:
            Lista de ModelMetadata ordenada por created_at descendente.

        Examples:
            >>> versions = await repo.list_versions(limit=5)
            >>> for metadata in versions:
            ...     print(f"{metadata.version}: F1={metadata.get_metric('f1'):.3f}")
            v1.2.3: F1=0.872
            v1.2.2: F1=0.865
            v1.2.1: F1=0.891
        """
        pass

    @abstractmethod
    async def delete_version(self, version: str) -> None:
        """
        Elimina una versión específica del modelo.

        Args:
            version: Versión a eliminar.

        Raises:
            ModelNotFoundException: Si la versión no existe.
            ValueError: Si se intenta eliminar la versión activa.

        Examples:
            >>> await repo.delete_version("v1.0.0")  # Limpiar versiones antiguas
        """
        pass
