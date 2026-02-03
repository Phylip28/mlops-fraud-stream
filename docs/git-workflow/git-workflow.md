# Guía de Contribución y Flujo de Trabajo (MLOps - Fraud Detection)

Este documento define los estándares de colaboración para el sistema de detección de fraude financiero en tiempo real.
El objetivo es mantener la integridad de la **Arquitectura Hexagonal**, facilitar el **Entrenamiento Continuo (CT)** y asegurar la trazabilidad de los modelos.

## 1. Estrategia de Branching (GitHub Flow)

Utilizamos **GitHub Flow**. La rama `main` es la fuente de verdad y siempre debe ser estable y desplegable.

**Reglas Críticas:**

- **Rama `main` Protegida:** Prohibido hacer commits directos. Todo cambio llega vía Pull Request (PR).
- **CI Obligatorio:** Ninguna rama se fusiona si no pasan los tests unitarios y de integración.

## 2. Convención de Nombres de Ramas

Todas las ramas parten de `main` y siguen el formato:
`categoria/descripcion-kebab-case`

### Prefijos Permitidos (Categorías)

| Prefijo  | Uso en este Proyecto                                                             | Ejemplo                                                     |
| :------- | :------------------------------------------------------------------------------- | :---------------------------------------------------------- |
| `feat/`  | Nueva funcionalidad en Dominio, Aplicación o API.                                | `feat/regla-geo-velocidad`, `feat/endpoint-inference`       |
| `fix/`   | Corrección de bugs en código o lógica de negocio.                                | `fix/ajuste-umbral-precision`, `fix/race-condition-redis`   |
| `mlops/` | **Modelos y Pipelines:** Cambios en `river`, métricas o lógica de entrenamiento. | `mlops/hoeffding-tree-params`, `mlops/drift-detection`      |
| `infra/` | **Infraestructura:** Docker, K8s, Terraform, Kafka, Redis.                       | `infra/redis-persistence`, `infra/docker-compose-gpu`       |
| `data/`  | **Feature Store & Schemas:** Definición de features o validación de datos.       | `data/feature-monto-promedio`, `data/schema-transaccion-v2` |
| `exp/`   | **Experimentos:** Notebooks o pruebas de concepto (no siempre se fusionan).      | `exp/prueba-isolation-forest`, `exp/analisis-latencia`      |
| `docs/`  | Documentación (Architecture decisions, Readme).                                  | `docs/adr-redis-vs-memcached`                               |
| `chore/` | Mantenimiento, dependencias, scripts de limpieza.                                | `chore/update-poetry-lock`, `chore/linter-rules`            |

---

## 3. Convención de Commits (Conventional Commits)

Los mensajes deben ser semánticos para facilitar la lectura del historial y la generación de changelogs.

### Estructura

```
tipo(alcance): descripción breve
```

**Componentes:**

- **`tipo`**: Coincide con el prefijo de la rama (`feat`, `fix`, `mlops`, `infra`, etc.).
- **`(alcance)`**: Define qué capa de la arquitectura se modificó:
  - **`domain`** - Núcleo: Entidades, reglas de negocio y puertos.
  - **`app`** - Casos de uso y servicios de aplicación.
  - **`adapter`** - Implementaciones técnicas: Repositorios Redis/SQL, Clientes S3.
  - **`api`** - Controladores REST, Schemas de Pydantic de entrada/salida.
  - **`ui`** - Dashboards, Streamlit o interfaz visual.
  - **`infra`** - Docker, CI/CD, Terraform.
  - **`tests`** - Unitarios, Integración, E2E.
  - **`model`** - Artefactos de ML, definición del pipeline River.
- **`descripción`**: Imperativo, claro y conciso.

### Ejemplos Válidos para este Proyecto

#### Backend (Arquitectura Hexagonal)

```
feat(domain): agregar regla de negocio para bloqueo preventivo
feat(app): implementar caso de uso DetectarFraude
feat(api): crear endpoint POST /v1/predict
fix(adapter): corregir timeout en conexión a Redis
```

> **Nota:** `api` reemplaza lo que antes era "back" en el alcance.

#### Frontend / Visualización

```
feat(ui): agregar gráfico de tasa de fraude en tiempo real
```

> **Nota:** `ui` reemplaza lo que antes era "front" en el alcance.

#### MLOps & Infra

```
mlops(model): reentrenar modelo con dataset de noviembre
infra(k8s): aumentar memoria en pod de inferencia
```

---

## 4. Flujo de Pull Requests (PR)

1.  **Crear PR:** Apunta siempre a `main`. Usa la plantilla de PR del repositorio.
2.  **Validación Automática:** El CI correrá:
    - Linter (`ruff` / `black`).
    - Tests Unitarios (Lógica de Dominio).
    - Tests de Integración (Conexión a Redis/API simulada).
3.  **Revisión (Code Review):**
    - **Arquitectura:** Verificar que no se violen capas (ej. Dominio no debe importar Redis).
    - **MLOps:** Verificar que los cambios en el modelo no introduzcan latencia excesiva.
4.  **Merge:** Squash & Merge recomendado para mantener lineal el historial.

---

## 5. Estándares de Código (Python)

- **Type Hinting:** Obligatorio en todo el código (`def predict(x: Transaction) -> float:`).
- **Docstrings:** Estilo Google o NumPy para clases y funciones complejas.
- **Gestión de Dependencias:** Usar siempre `poetry add` (nunca editar requirements.txt a mano).
