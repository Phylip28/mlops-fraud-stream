import pandas as pd
import xgboost as xgb
from base_model import BaseModel

class XGBoostBaseline(BaseModel):
    def __init__(self, random_state: int = 42, use_label_encoder: bool = False):
        super().__init__(model_name="XGBoost")
        self.model = xgb.XGBClassifier(
            random_state=random_state,
            use_label_encoder=use_label_encoder,
            eval_metric='logloss', # Métrica estándar para clasificación binaria
            n_jobs=-1
        )

    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        print(f"Entrenando {self.model_name}...")
        self.model.fit(X_train, y_train)
        print(f"{self.model_name} entrenado exitosamente.")

    def predict(self, X_test: pd.DataFrame) -> pd.Series:
        return self.model.predict(X_test)
