import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from base_model import BaseModel

class RandomForestBaseline(BaseModel):
    def __init__(self, random_state: int = 42, n_estimators: int = 100):
        super().__init__(model_name="Random_Forest")
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=-1 # Usar todos los procesadores
        )

    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        print(f"Entrenando {self.model_name}...")
        self.model.fit(X_train, y_train)
        print(f"{self.model_name} entrenado exitosamente.")

    def predict(self, X_test: pd.DataFrame) -> pd.Series:
        return self.model.predict(X_test)
