# Sistema de Detección de Fraude Financiero en Tiempo Real

Sistema de detección de fraude basado en Stream Learning (Aprendizaje Incremental) con Arquitectura Hexagonal.

## 🏗️ Arquitectura

Este proyecto implementa **Arquitectura Hexagonal (Puertos y Adaptadores)** para garantizar:
- ✅ Desacoplamiento del dominio ML
- ✅ Testabilidad nativa
- ✅ Flexibilidad de infraestructura
- ✅ Mantenibilidad y escalabilidad

Ver documentación completa en [`ARCHITECTURE.md`](ARCHITECTURE.md).

## 📋 Requisitos

- Python 3.10+
- Poetry (gestor de dependencias)
- Docker & Docker Compose (para servicios de infraestructura)

## 🚀 Instalación

```bash
# 1. Instalar dependencias con Poetry
poetry install

# 2. Activar entorno virtual
poetry shell

# 3. (Opcional) Instalar dependencias de desarrollo
poetry install --with dev
```

## 📦 Estructura del Proyecto

```
src/
├── domain/              # Lógica de negocio pura
│   ├── entities/        # Transaction, Prediction, FraudLabel, ModelMetadata
│   ├── value_objects/   # TransactionId, Amount, FraudScore, MerchantCategory
│   ├── services/        # FraudDetectionService, IncrementalLearningService
│   └── exceptions/      # Excepciones de dominio
│
├── application/         # Casos de uso y puertos
│   ├── ports/
│   │   ├── inbound/     # FraudDetector, ModelTrainer, ModelEvaluator
│   │   └── outbound/    # ModelRepository, FeatureStore, EventPublisher
│   ├── use_cases/       # (FASE 2 - No implementado aún)
│   └── dto/             # (FASE 2 - No implementado aún)
│
└── infrastructure/      # (FASE 3 - No implementado aún)
    ├── adapters/
    ├── ml/
    └── persistence/
```

## 🧪 Testing

```bash
# Ejecutar tests unitarios
poetry run pytest

# Con cobertura
poetry run pytest --cov=src --cov-report=html

# Solo tests de dominio
poetry run pytest tests/unit/domain/
```

## 🔍 Linting y Formateo

```bash
# Formatear código con Black
poetry run black src/

# Ordenar imports con isort
poetry run isort src/

# Linting con Ruff
poetry run ruff check src/

# Type checking con mypy
poetry run mypy src/
```

## 📝 FASE 1 - Completado ✅

Esta FASE 1 incluye:

### ✅ Estructura del Proyecto
- [x] Árbol de carpetas completo
- [x] Archivos `__init__.py` en todos los paquetes
- [x] `pyproject.toml` con Poetry

### ✅ Capa de Dominio (`src/domain/`)

#### Entidades
- [x] `Transaction` - Transacción financiera
- [x] `Prediction` - Predicción de fraude
- [x] `FraudLabel` - Label confirmada (delayed label)
- [x] `ModelMetadata` - Metadatos del modelo ML

#### Value Objects
- [x] `TransactionId` - ID único de transacción
- [x] `Amount` - Monto monetario con validaciones
- [x] `FraudScore` - Score de fraude (0.0 - 1.0)
- [x] `MerchantCategory` - Categoría de comerciante (MCC)

#### Servicios de Dominio
- [x] `FraudDetectionService` - Lógica de detección de fraude
- [x] `IncrementalLearningService` - Políticas de stream learning
- [x] `RiskScoringService` - Combinación de señales de riesgo

#### Excepciones
- [x] `InvalidTransactionException`
- [x] `ModelNotReadyException`
- [x] `FeatureMissingException`
- [x] `PredictionNotFoundException`

### ✅ Puertos (Interfaces) (`src/application/ports/`)

#### Inbound Ports
- [x] `FraudDetector` - Puerto de detección de fraude
- [x] `ModelTrainer` - Puerto de entrenamiento incremental
- [x] `ModelEvaluator` - Puerto de evaluación del modelo

#### Outbound Ports
- [x] `ModelRepository` - Persistencia del modelo
- [x] `PredictionRepository` - Persistencia de predicciones
- [x] `FeatureStore` - Feature Store
- [x] `TransactionStream` - Stream de transacciones
- [x] `LabelStream` - Stream de labels
- [x] `EventPublisher` - Publicación de eventos
- [x] `MetricsTracker` - Tracking de métricas

## 🔜 Próximos Pasos (FASE 2)

- [ ] Implementar Use Cases (DetectFraudUseCase, UpdateModelUseCase)
- [ ] Implementar DTOs
- [ ] Implementar adaptadores de infraestructura (Kafka, Redis, PostgreSQL)
- [ ] Implementar wrapper de river
- [ ] Tests de integración

## 📚 Documentación

- [`ARCHITECTURE.md`](ARCHITECTURE.md) - Arquitectura detallada del sistema
- Docstrings en cada clase y método
- Type hints estrictos (Python 3.10+)

## 🛡️ Principios SOLID Aplicados

- **SRP**: Cada clase tiene una única responsabilidad
- **OCP**: Abierto para extensión, cerrado para modificación
- **LSP**: Implementaciones intercambiables de puertos
- **ISP**: Interfaces segregadas y específicas
- **DIP**: Dependencia de abstracciones, no de concreciones

## 📄 Licencia

[Especificar licencia]

## 👥 Autores

[Especificar autores]
