"""Excepciones de dominio del sistema de detección de fraude."""


class DomainException(Exception):
    """Excepción base para errores del dominio."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class InvalidTransactionException(DomainException):
    """Se lanza cuando una transacción no cumple con las reglas de negocio."""

    pass


class ModelNotReadyException(DomainException):
    """Se lanza cuando el modelo ML no está inicializado o listo para inferencia."""

    pass


class FeatureMissingException(DomainException):
    """Se lanza cuando faltan features críticas para la predicción."""

    def __init__(self, feature_names: list[str]) -> None:
        self.feature_names = feature_names
        message = f"Features faltantes: {', '.join(feature_names)}"
        super().__init__(message)


class PredictionNotFoundException(DomainException):
    """Se lanza cuando no se encuentra una predicción en el repositorio."""

    pass
