import os

import mlflow
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier

# Configurar credenciales para conectar MLflow con MinIO
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://localhost:9000"
os.environ["AWS_ACCESS_KEY_ID"] = "minio_user"
os.environ["AWS_SECRET_ACCESS_KEY"] = "minio_password"

# Apuntar al servidor de MLflow
mlflow.set_tracking_uri("http://localhost:5000")


def run_training() -> None:
    """Entrena un modelo dummy y lo registra en MLflow."""
    # Crear o usar un experimento genérico
    mlflow.set_experiment("mlops_base_experiment")

    with mlflow.start_run():
        print("Entrenando modelo...")
        # Generar datos falsos (4 features)
        X, y = make_classification(n_samples=100, n_features=4, random_state=42)

        # Entrenar un modelo básico
        clf = RandomForestClassifier(max_depth=2, random_state=42)
        clf.fit(X, y)

        # Loguear hiperparámetros y métricas en PostgreSQL
        mlflow.log_param("max_depth", 2)
        mlflow.log_param("model_type", "RandomForest")
        mlflow.log_metric("dummy_accuracy", clf.score(X, y))

        # Loguear y registrar el modelo físico en MinIO
        mlflow.sklearn.log_model(
            sk_model=clf, artifact_path="model", registered_model_name="GenericModel"
        )
        print("¡Modelo entrenado y registrado en MLflow con éxito!")


if __name__ == "__main__":
    run_training()
