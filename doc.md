Para verificar que todo se está ejecutando de manera correcta y conocer el paso a paso, aquí tienes la guía completa:

### 🕵️‍♂️ Cómo verificar que todo funciona correctamente

1. **Revisar los contenedores de Docker:**
   Puedes abrir tu terminal y ejecutar `docker ps`. Deberías ver tres contenedores en estado `Up` (o `healthy`):
   - `mlops_postgres` (Base de datos en el puerto 5432)
   - `mlops_minio` (Almacenamiento de artefactos en los puertos 9000 y 9001)
   - `mlops_mlflow` (Servidor de MLflow en el puerto 5000)

2. **Verificar el servidor de MLflow (Tracking & Model Registry):**
   - Abre tu navegador y ve a: [http://localhost:5000](http://localhost:5000)
   - Deberías ver un experimento (por ejemplo, `mlops_base_experiment`) con al menos un run/ejecución.
   - En la pestaña de "Models" (Modelos) arriba a la derecha, deberías ver registrado un modelo (como `GenericModel`) con el alias `champion`.

3. **Verificar MinIO (Almacenamiento del modelo en la nube/S3 local):**
   - Ve a: [http://localhost:9001](http://localhost:9001)
   - Inicia sesión con las credenciales que están en tú docker-compose.yaml (Usuario: `minio_user` / Contraseña: `minio_password`).
   - Podrás ver los archivos físicos `.pkl` o de Scikit-learn que MLflow guardó.

4. **Verificar el servicio de FastAPI:**
   - Ve a la interfaz interactiva de Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Allí verás los endpoints disponibles (por ejemplo de `/predict/). Puedes enviar una petición de prueba directamente desde el navegador haciendo clic en *"Try it out"*.

---

### 📝 Paso a paso para realizar la ejecución desde cero

Si en algún momento necesitas parar la ejecución, limpiar el entorno y volver a empezar, realiza estos pasos desde tu terminal (PowerShell) estando en la carpeta raíz mlops-base-template:

**Paso 1: Levantar la Infraestructura (Docker)**
Inicia los servicios en segundo plano:
```powershell
docker-compose up -d
```

**Paso 2: Activar el entorno virtual**
Activa el entorno donde instalaste las dependencias ( Poetry / uv / pip ):
```powershell
.\.venv\Scripts\Activate.ps1
```

**Paso 3: Generar los Datos**
Crea los datasets sintéticos crudos que se guardarán en la capeta `data/raw/`:
```powershell
python scripts/generate_data.py
```

**Paso 4: Entrenar el Modelo Base**
Esto orquestará el entrenamiento, guardará las métricas en PostgreSQL (vía MLflow) y subirá el modelo a MinIO (como si fuera AWS S3):
```powershell
python scripts/train_dummy.py
```

**Paso 5: Levantar la API para exponer el modelo**
Ponte en la carpeta del código fuente (`src`) y arranca el servidor `uvicorn` (FastAPI):
```powershell
cd src
$env:PYTHONPATH="."
uvicorn model_service.infrastructure.entrypoints.api:app --host 0.0.0.0 --port 8000 --reload
```
Al hacer esto, la aplicación se conectará a MLflow, descargará dinámicamente el modelo marcado como *champion* a la memoria RAM e iniciará el servidor para recibir peticiones HTTP en el puerto `8000`.