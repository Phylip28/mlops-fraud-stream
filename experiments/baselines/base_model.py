from abc import ABC, abstractmethod
import pandas as pd
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score
from typing import Dict, Any

class BaseModel(ABC):
    """
    Clase base abstracta para todos los modelos baseline.
    Garantiza que todos implementen la misma interfaz.
    """
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None

    @abstractmethod
    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        """Entrena el modelo con los datos proporcionados."""
        pass

    @abstractmethod
    def predict(self, X_test: pd.DataFrame) -> pd.Series:
        """Genera predicciones (clases) para los datos."""
        pass
    
    def predict_proba(self, X_test: pd.DataFrame) -> pd.DataFrame:
        """Genera probabilidades (opcional, útil para AUC-ROC). Por defecto asume que el modelo tiene predict_proba."""
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X_test)
        raise NotImplementedError(f"[{self.model_name}] no implementa predict_proba.")

    def evaluate(self, y_true: pd.Series, y_pred: pd.Series) -> Dict[str, Any]:
        """
        Calcula las métricas principales y retorna un diccionario.
        """
        metrics = {
            "model_name": self.model_name,
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, zero_division=0),
            "recall": recall_score(y_true, y_pred, zero_division=0),
            "f1_score": f1_score(y_true, y_pred, zero_division=0)
        }
        
        print(f"\n--- Evaluación: {self.model_name} ---")
        print(classification_report(y_true, y_pred, zero_division=0))
        
        return metrics
