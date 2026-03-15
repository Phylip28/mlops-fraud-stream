Write-Host "=============================================" -ForegroundColor Green
Write-Host "🚀 INICIANDO EL PIPELINE MLOPS DE FRAUDE (FASE 0)" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""

# 1. Instalar requerimientos
Write-Host "[1/5] Verificando e Instalando Dependencias..." -ForegroundColor Cyan
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error instalando las dependencias. Saliendo..." -ForegroundColor Red
    exit 1
}

# 2. Navegar a la carpeta de experimentos
$ExperimentsPath = "experiments/baselines"
if (Test-Path $ExperimentsPath) {
    Set-Location $ExperimentsPath
} else {
    Write-Host "El directorio $ExperimentsPath no existe. Ejecuta este script desde la raiz del proyecto." -ForegroundColor Red
    exit 1
}

# 3. Preprocesar datos
Write-Host "`n[2/5] Ejecutando Pre-procesamiento de Datos (Muestreo y SMOTE)..." -ForegroundColor Cyan
python data_preprocessing.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error en la preparacion de datos." -ForegroundColor Red
    exit 1
}

# 4. Entrenar y evaluar Modelos
Write-Host "`n[3/5] Entrenando Grid de Modelos Baseline..." -ForegroundColor Cyan
python steps.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error durante el entrenamiento de modelos." -ForegroundColor Red
    exit 1
}

# 5. Simulacion Data Drift
Write-Host "`n[4/5] Simulando escenario MLOps de Data Drift..." -ForegroundColor Cyan
python data_drift_simulation.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Hubo un error en la simulacion del Drift, pero el dashboard principal seguira." -ForegroundColor Yellow
}

# 6. Levantar Streamlit
Write-Host "`n[5/5] Levantando el Dashboard Analitico de Streamlit..." -ForegroundColor Green
Write-Host "NOTA: El sistema quedara corriendo. Presiona Ctrl + C en esta terminal para detener el Dashboard en cualquier momento.`n" -ForegroundColor Yellow
streamlit run dashboard.py
