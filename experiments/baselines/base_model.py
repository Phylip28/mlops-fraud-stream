from abc import ABC, abstractmethod
import pandas as pd
import time
from typing import Dict, Any
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

class BaseModel(ABC):
    """
    Clase abstracta basada en principios SOLID (Open/Closed, Liskov).
    Define el contrato para cualquier modelo predictivo implementado en Phase 0.
    """
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.train_time_sec = 0.0
        self.infer_time_sec = 0.0

    @abstractmethod
    def _train_logic(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        """Lógica interna de entrenamiento específica de la librería implementada."""
        pass

    @abstractmethod
    def _predict_logic(self, X_test: pd.DataFrame) -> pd.Series:
        """Lógica interna de inferencia."""
        pass

    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        """Envoltorio base para controlar la ejecución y medir el tiempo de entrenamiento."""
        print(f"Entrenando {self.model_name}...")
        start_time = time.time()
        self._train_logic(X_train, y_train)
        self.train_time_sec = time.time() - start_time
        print(f"|> Tiempo de entrenamiento: {self.train_time_sec:.2f}s")

    def predict(self, X_test: pd.DataFrame) -> pd.Series:
        """Envoltorio base para controlar la ejecución y medir el tiempo de inferencia."""
        start_time = time.time()
        preds = self._predict_logic(X_test)
        self.infer_time_sec = time.time() - start_time
        return preds

    def evaluate(self, y_true: pd.Series, y_pred: pd.Series) -> Dict[str, Any]:
        """
        Calcula las métricas de rendimiento del modelo e incluye 
        las latencias medidas previamente.
        """
        cm = confusion_matrix(y_true, y_pred)
        
        metrics = {
            "model_name": self.model_name,
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, zero_division=0),
            "recall": recall_score(y_true, y_pred, zero_division=0),
            "f1_score": f1_score(y_true, y_pred, zero_division=0),
            "train_time_sec": self.train_time_sec,
            "infer_time_sec": self.infer_time_sec,
            "confusion_matrix": cm.tolist()
        }
        
        print(f"|> Métricas: F1={metrics['f1_score']:.4f} | Recall={metrics['recall']:.4f} | Prec={metrics['precision']:.4f}")
        return metrics
