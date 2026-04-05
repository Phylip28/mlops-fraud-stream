import os
from typing import Tuple, Dict, Any

import mlflow
from mlflow.tracking import MlflowClient
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

class AutoMLOrchestrator:
    """
    Orquestador AutÃ³nomo MLOps.
    Se encarga de recibir un dataset, entrenar mÃºltiples modelos,
    identificar el ganador y registrarlo como 'champion' en MLflow.
    """
    def __init__(self, tracking_uri: str = "http://localhost:5000", s3_endpoint: str = "http://localhost:9000"):
        self.tracking_uri = tracking_uri
        
        # ConfiguraciÃ³n de credenciales AWS S3 (MinIO)
        os.environ["MLFLOW_S3_ENDPOINT_URL"] = s3_endpoint
        os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID", "minio_user")
        os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY", "minio_password")
        
        mlflow.set_tracking_uri(self.tracking_uri)
        self.client = MlflowClient()

    def _prepare_data(self, dataset_path: str, target_col: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Carga y divide el dataset."""
        df = pd.read_csv(dataset_path)
        if target_col not in df.columns:
            raise ValueError(f"Columna objetivo '{target_col}' no encontrada en el dataset.")
        
        X = df.drop(columns=[target_col])
        y = df[target_col]
        return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    def run_automl(self, dataset_path: str, target_col: str, experiment_name: str, registered_model_name: str) -> Dict[str, Any]:
        """
        Ejecuta el ciclo de AutoML, determina el mejor modelo y lo promociona a 'champion'.
        """
        mlflow.set_experiment(experiment_name)
        
        X_train, X_test, y_train, y_test = self._prepare_data(dataset_path, target_col)
        
        models = {
            "RandomForest": RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42),
            "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42)
        }
        
        best_f1 = -1.0
        best_run_id = None
        best_model_name = None
        
        # 1. Entrenar MÃºltiples Modelos
        for model_name, model in models.items():
            with mlflow.start_run(run_name=f"Automl_{model_name}") as run:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                
                acc = accuracy_score(y_test, y_pred)
                # Evaluamos F1-Score (macro para soportar binario o multiclase)
                f1 = f1_score(y_test, y_pred, average='macro')
                
                mlflow.log_param("model_type", model_name)
                mlflow.log_metric("accuracy", acc)
                mlflow.log_metric("f1_score", f1)
                
                # Guardar el modelo fÃsicamente en MinIO (S3)
                mlflow.sklearn.log_model(
                    sk_model=model,
                    artifact_path="model"
                )
                
                print(f"ðŸ§ª Entrenado {model_name} | Acc: {acc:.4f} | F1: {f1:.4f}")
                
                # Identificamos el mejor modelo del run
                if f1 > best_f1:
                    best_f1 = f1
                    best_run_id = run.info.run_id
                    best_model_name = model_name
                    
        # 2. Registrar el Mejor Modelo como 'champion'
        print(f"\nðŸ† Mejor modelo: {best_model_name} con F1: {best_f1:.4f}")
        
        # Creamos una versiÃ³n del modelo en el Model Registry conectada al run ganador
        model_version = mlflow.register_model(
            model_uri=f"runs:/{best_run_id}/model",
            name=registered_model_name
        )
        
        # Asignamos el alias 'champion' a esta nueva versiÃ³n usando el cliente de MLflow
        self.client.set_registered_model_alias(
            name=registered_model_name,
            alias="champion",
            version=model_version.version
        )
        
        print(f"âœ… Modelo {registered_model_name} (v{model_version.version}) promovido a 'champion'.")
        
        return {
            "winner_model": best_model_name,
            "f1_score": best_f1,
            "run_id": best_run_id,
            "model_version": model_version.version,
            "alias_assigned": "champion"
        }
