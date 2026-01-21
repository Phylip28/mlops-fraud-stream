# 💥 TRABAJO DE GRADO 💥🔜🔜🔜

# mlops-fraud-stream
Implementación de MLOps para detección de fraude financiero en tiempo real usando Stream Learning y Arquitectura Hexagonal


# 🗺️ Roadmap de Implementación: Sistema de Detección de Fraude (Stream Learning)

Este documento detalla el plan de implementación progresiva del sistema, estructurado en 3 fases lógicas para asegurar la calidad del código, el desacoplamiento de componentes (Arquitectura Hexagonal) y la estabilidad del modelo de ML.

---

## 🏗️ Fase 1: El Núcleo (Dominio y Abstracciones)
**Objetivo:** Definir las reglas de negocio, entidades y contratos (interfaces) sin depender de ninguna tecnología externa (ni bases de datos, ni frameworks web).

*En esta fase se construye la "verdad" del negocio.*

- [ ] **Estructura del Proyecto:** Configuración de carpetas, `pyproject.toml` y entorno virtual.
- [ ] **Entidades de Dominio:** Definición de `Transaction`, `FraudPrediction` y `FraudLabel` (usando Pydantic/Dataclasses).
- [ ] **Puertos (Interfaces):** Creación de clases abstractas (ABC) para:
    - `ModelRepository` (Guardar/Cargar modelo).
    - `FeatureStore` (Recuperar variables históricas).
    - `EventPublisher` (Publicar alertas).
- [ ] **Servicios de Dominio:** Lógica pura de detección (`FraudDetectionService`) y reglas de validación.
- [ ] **Tests Unitarios del Dominio:** Pruebas aisladas para garantizar que la lógica funciona (usando Mocks).

---

## 🔌 Fase 2: Infraestructura y Adaptadores
**Objetivo:** Conectar el núcleo con el mundo real. Implementar las tecnologías específicas para persistencia, ML y manejo de estado.

*En esta fase decidimos "cómo" se guardan y procesan los datos.*

- [ ] **Adaptador de ML (River):** Implementación de `RiverModelWrapper` que usa la librería `river` para aprender incrementalmente.
- [ ] **Gestión de Estado (Redis):** Implementación de `RedisModelRepository` para guardar/cargar el estado del modelo en milisegundos.
- [ ] **Manejo de "Delayed Labels":** Implementación de la lógica para unir una predicción antigua con una etiqueta de fraude reciente (Join temporal).
- [ ] **Feature Store:** Conexión simulada o real (ej. Feast/Redis) para enriquecer las transacciones.
- [ ] **Tests de Integración:** Verificar que el modelo se guarda y recupera correctamente de Redis.

---

## 🚀 Fase 3: Despliegue, API y Orquestación
**Objetivo:** Exponer el sistema al mundo, manejar la concurrencia y preparar el entorno productivo.

*En esta fase el sistema cobra vida y empieza a recibir tráfico.*

- [ ] **API Rest (FastAPI):** Endpoint `/predict` para recibir transacciones en tiempo real.
- [ ] **Consumidor de Eventos (Kafka/FastStream):** Servicio para procesar etiquetas de fraude asíncronas (`/feedback`).
- [ ] **Contenedores (Docker):** Creación de `Dockerfile` y `docker-compose.yml` para levantar todo el stack (App + Redis + Kafka).
- [ ] **Observabilidad:** Configuración básica de métricas (Prometheus) para monitorear el *Data Drift*.
- [ ] **Pipeline CI/CD:** Configuración de GitHub Actions para linter y tests automáticos.

---

### 📌 Notas de Arquitectura
Este proyecto sigue estrictamente la **Arquitectura Hexagonal**.
- **`src/domain`**: No tiene dependencias externas.
- **`src/adapters`**: Contiene las implementaciones de Redis, River, Kafka, etc.
- **`src/entrypoints`**: Contiene la API y los CLI.
