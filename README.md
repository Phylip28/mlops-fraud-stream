# Sistema de Detección de Fraude Financiero en Tiempo Real

Sistema de detección de fraude basado en Stream Learning (Aprendizaje Incremental) con Arquitectura Hexagonal. Este proyecto contempla un pipeline experimental MLOps progresivo, iniciando desde una **Fase 0** en Batch hasta llegar al despliegue en tiempo real (**Stream Learning**).

## 🏗️ Arquitectura y Fases

### Fase 0: Experimentación y Benchmarks (Batch)
Se implementa un Grid de algoritmia clásica (Logistic Regression, Random Forest, XGBoost, LightGBM, CatBoost) aplicando estrategias de desbalanceo (SMOTE) con separación estricta para evitar Data Leakage. Se incluye simulación de Data Drift mediante el test de Kolmogorov-Smirnov.

### Fase 1: Stream Learning (Arquitectura Hexagonal)
Este proyecto adopta **Arquitectura Hexagonal (Puertos y Adaptadores)** para garantizar:
- ✅ Desacoplamiento del dominio ML (core).
- ✅ Testabilidad nativa de la lógica de detección.
- ✅ Flexibilidad de infraestructura (Kafka / Redpanda, Bases de datos en memoria).
- ✅ Mantenibilidad y escalabilidad.

Ver documentación de la Fase 1 en [`ARCHITECTURE.md`](ARCHITECTURE.md).

## 📋 Requisitos Previos

- Python 3.10+
- Poetry (gestor de dependencias para el microservicio base)
- Pip (gestor de dependencias para la experimentación)
- Docker & Docker Compose (para servicios de infraestructura en Fases avanzadas)

## 🚀 Instalación y Ejecución con un Solo Comando (Fase 0)

Hemos empaquetado toda la Fase de experimentación (Preprocesamiento, Entrenamiento de Modelos y Dashboard Streamlit) en un solo script de PowerShell para que puedas evaluar la línea base del modelo de detección de fraude fácilmente.

En tu terminal de Windows ejecuta:
```powershell
.\run_pipeline.ps1
```
Este script:
1. Instalará automáticamente todas las dependencias listadas en `requirements.txt`.
2. Generará/pre-procesará los datos con estratificación y balanceo sintético (SMOTE).
3. Entrenará el Grid completo de modelos Baseline.
4. Levantará de forma automática el **Dashboard Analítico** en tu navegador.
5. Ejecutará paralelamente una corrida de detección estadística de Data Drift (KS Test).

---

### (Opcional) Instalación del CORE Hexagonal con Poetry (Fases Stream)
Si deseas trabajar directamente con la lógica de Stream Learning del modelo en vivo (`fraud-engine`):

```bash
cd services/fraud-engine
# 1. Instalar dependencias con Poetry
poetry install
# 2. Activar entorno virtual
poetry shell
```

## 📦 Estructura General

```text
.
├── data/
│   ├── raw/                 # Datasets crudos (Ignorados en Git)
│   └── processed/           # Datasets pre-procesados (Ignorados en Git)
├── experiments/
│   └── baselines/           # FASE 0: Baseline Batch Models y Dashboards
│       ├── data_preprocessing.py
│       ├── base_model.py                # Clase base abstracta SOLID
│       ├── *_model.py                   # Algoritmos específicos instanciados
│       ├── steps.py                     # Pipeline de Orquestacion Batch
│       ├── data_drift_simulation.py     # Drift detector estadistico (MLOps)
│       └── dashboard.py                 # UX y UX analitica (Streamlit)
├── services/
│   └── fraud-engine/        # FASE 1: Core de Detección (Stream Learning Hexagonal)
│       ├── src/domain/      # Lógica de negocio (Entidades, Excepciones)
│       ├── application/     # Casos de uso
│       └── infrastructure/  # Redpanda, Redis, APIs e integracion ML
├── run_pipeline.ps1         # Script unificado de instalación y ejecución MLOps
├── requirements.txt         # Entorno librerías Data Science Fase 0
└── README.md
```

## 🧪 Testing y Linting (Core Aplicativo)

Para los tests unitarios del área de microservicios:

```bash
cd services/fraud-engine
poetry run pytest --cov=src --cov-report=html
poetry run black src/
poetry run ruff check src/
```
