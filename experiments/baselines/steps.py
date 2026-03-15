import pandas as pd
import json
import os

from logistic_regression_model import LogisticRegressionModel
from random_forest_model import RandomForestModel
from xgboost_model import XGBoostModel
from lightgbm_model import LightGBMModel
from catboost_model import CatBoostModel

def run_pipeline(train_path: str, test_path: str, output_path: str):
    """
    Instancia la suite de modelos, entrena, evalúa y exporta métricas.
    """
    target_col = 'isFraud'
    
    print("\n" + "="*50)
    print("🚀 INICIANDO FASE 0: EVALUACIÓN DE BASELINES BATCH")
    print("="*50 + "\n")
    
    if not os.path.exists(train_path) or not os.path.exists(test_path):
        raise FileNotFoundError("Primero ejecuta data_preprocessing.py")
        
    print("1. Cargando datasets procesados...")
    X_train = pd.read_csv(train_path)
    y_train = X_train.pop(target_col)
    
    X_test = pd.read_csv(test_path)
    y_test = X_test.pop(target_col)
    
    print("\n2. Instanciando Suite de Modelos...")
    suite = [
        LogisticRegressionModel(),
        RandomForestModel(),
        XGBoostModel(),
        LightGBMModel(),
        CatBoostModel()
    ]
    
    print("\n3. Entrenamiento y Evaluación Secuencial...")
    resultados = []
    
    for model in suite:
        print(f"\n--- Evaluando: {model.model_name} ---")
        model.train(X_train, y_train)
        y_pred = model.predict(X_test)
        metrics = model.evaluate(y_test, y_pred)
        resultados.append(metrics)
        
    print("\n4. Exportando métricas consolidadas...")
    with open(output_path, "w") as f:
        json.dump(resultados, f, indent=4)
        
    print(f"\n✅ Pipeline finalizado. Resultados exportados a '{output_path}'.")

if __name__ == "__main__":
    TRAIN_CSV = "../../data/processed/train_smote.csv"
    TEST_CSV = "../../data/processed/test_resampled.csv"
    OUTPUT_JSON = "metrics.json"
    
    run_pipeline(TRAIN_CSV, TEST_CSV, OUTPUT_JSON)
