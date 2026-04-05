***

# 📖 Documentación del Pipeline de Entrenamiento (Fase 0)

Este documento describe el flujo automatizado actual del pipeline MLOps para la generación de datos, entrenamiento del modelo base y su exposición a través de una API REST.

## ⚙️ ¿Qué realiza el programa?

1. **Generación de Datos (generate_data.py):** 
   Crea de manera sintética (usando `scikit-learn`) datasets balanceados para resolver problemas de clasificación. Los archivos resultantes se guardan de forma física en la ruta `data/raw/`.
   - `balanced_binary_dataset.csv` (1000 registros, 12 variables).
   - `balanced_multiclass_dataset.csv` (1500 registros, 15 variables).

2. **Entrenamiento Automatizado (train_dummy.py):**
   - **Ingesta:** Lee automáticamente el dataset generado `balanced_binary_dataset.csv` desde la carpeta `data/raw/`.
   - **Preprocesamiento:** Separa los datos en conjunto de entrenamiento (80%) y prueba (20%).
   - **Modelado:** Entrena un modelo `RandomForestClassifier` (max_depth=5).
   - **Registro (Tracking):** Se conecta con **MLflow** para guardar métricas importantes (ej. `accuracy`), hiperparámetros (`max_depth`) y guarda el modelo físico en un almacenamiento de objetos (**MinIO**).

3. **Exposición del Modelo (api.py):**
   Levanta un servicio web con **FastAPI** que, en el momento de iniciar, se conecta a MLflow, busca el modelo registrado, lo descarga en memoria RAM y provee endpoints para realizar predicciones.

---

## 🚀 Guía de Ejecución Paso a Paso

Asegúrate de estar posicionado en la carpeta raíz del proyecto (mlops-base-template) y con tu entorno virtual de Python activo.

### 1. Iniciar los servicios de Infraestructura
Levanta PostgreSQL (Base de datos de MLflow), MinIO (Artefactos) y el servidor de MLflow utilizando Docker.
```powershell
docker-compose up -d
```

### 2. Generar los datos
Genera los archivos CSV necesarios dentro de `data/raw/`.
```powershell
python scripts/generate_data.py
```

### 3. Ejecutar el Entrenamiento
Corre el script que toma los datos generados, entrena el modelo de Random Forest y lo registra en MLflow.
```powershell
python scripts/train_dummy.py
```
*(Puedes ver las métricas generadas y el modelo guardado abriendo `http://localhost:5000` en tu navegador).*

### 4. Lanzar la API del Modelo
Levanta el servicio de FastAPI para que el modelo entrenado pueda recibir requests en tiempo real.
```powershell
cd src
$env:PYTHONPATH="."
uvicorn model_service.infrastructure.entrypoints.api:app --host 0.0.0.0 --port 8000 --reload
```
*(Puedes interactuar con la API abriendo la interfaz de Swagger UI en `http://localhost:8000/docs`).*