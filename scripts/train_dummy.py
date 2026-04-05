import os

import mlflow
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Configurar credenciales para conectar MLflow con MinIO
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://localhost:9000"
os.environ["AWS_ACCESS_KEY_ID"] = "minio_user"
os.environ["AWS_SECRET_ACCESS_KEY"] = "minio_password"

# Apuntar al servidor de MLflow
mlflow.set_tracking_uri("http://localhost:5000")


def run_training() -> None:
    """Entrena un modelo con el dataset generado y lo registra en MLflow."""
    # Crear o usar un experimento genérico
    mlflow.set_experiment("mlops_base_experiment")

    with mlflow.start_run():
        print("Cargando dataset...")
        df = pd.read_csv("data/raw/balanced_binary_dataset.csv")
        X = df.drop(columns=["target"])
        y = df["target"]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        print("Entrenando modelo...")
        # Entrenar un modelo básico
        clf = RandomForestClassifier(max_depth=5, random_state=42)
        clf.fit(X_train, y_train)

        accuracy = clf.score(X_test, y_test)

        # Loguear hiperparámetros y métricas en PostgreSQL
        mlflow.log_param("max_depth", 5)
        mlflow.log_param("model_type", "RandomForest")
        mlflow.log_metric("accuracy", accuracy)

        # Loguear y registrar el modelo físico en MinIO
        mlflow.sklearn.log_model(
            sk_model=clf, artifact_path="model", registered_model_name="GenericModel"
        )
        print(f"¡Modelo entrenado y registrado en MLflow con éxito! Exactitud: {accuracy:.4f}")


if __name__ == "__main__":
    run_training()
