import pandas as pd
import json
import os
from sklearn.linear_model import LogisticRegression
from base_model import BaseModel
from random_forest_model import RandomForestBaseline
from xgboost_model import XGBoostBaseline

# --- Modelo Simple adicional para Baseline extremo ---
class LogisticRegressionBaseline(BaseModel):
    def __init__(self, random_state: int = 42):
        super().__init__(model_name="Logistic_Regression")
        self.model = LogisticRegression(random_state=random_state, max_iter=1000)

    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        print(f"Entrenando {self.model_name}...")
        self.model.fit(X_train, y_train)

    def predict(self, X_test: pd.DataFrame) -> pd.Series:
        return self.model.predict(X_test)


def run_experiment(train_path: str, test_path: str, output_metrics_path: str):
    """
    Carga los datos preprocesados, instancia los modelos, 
    los entrena y guarda sus métricas.
    """
    target_col = 'isFraud' # Ajustar si tu columna se llama distinto

    print(f"[{'='*40}]")
    print("Iniciando Pipeline de Experimentación (Batch Baseline)")
    print(f"[{'='*40}]\n")

    # 1. Cargar Datos
    print("Cargando datasets procesados...")
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)

    X_train = train_df.drop(columns=[target_col])
    y_train = train_df[target_col]
    X_test = test_df.drop(columns=[target_col])
    y_test = test_df[target_col]

    # 2. Instanciar Modelos
    models = [
        LogisticRegressionBaseline(),
        RandomForestBaseline(),
        XGBoostBaseline()
    ]

    # 3. Entrenamiento y Evaluación Secuencial
    all_metrics = []
    
    for model in models:
        model.train(X_train, y_train)
        
        # Inferencia
        print(f"Generando predicciones con {model.model_name} sobre Test Set...")
        y_pred = model.predict(X_test)
        
        # Evaluación
        metrics = model.evaluate(y_test, y_pred)
        all_metrics.append(metrics)

    # 4. Guardar Resultados
    os.makedirs(os.path.dirname(output_metrics_path) or ".", exist_ok=True)
    with open(output_metrics_path, "w") as f:
        json.dump(all_metrics, f, indent=4)

    print(f"\n✅ Experimentación finalizada. Métricas guardadas en {output_metrics_path}")


if __name__ == "__main__":
    TRAIN_PATH = "../../data/processed/train_smote.csv"
    TEST_PATH = "../../data/processed/test_resampled.csv"
    METRICS_PATH = "metrics.json"

    # Si los datos no existen, podríamos llamar a prep_data aquí,
    # pero asumimos que se corrió data_preprocessing.py primero.
    if not os.path.exists(TRAIN_PATH) or not os.path.exists(TEST_PATH):
        print("Datos procesados no encontrados. Ejecuta data_preprocessing.py primero.")
    else:
        run_experiment(TRAIN_PATH, TEST_PATH, METRICS_PATH)
