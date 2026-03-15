import pandas as pd
from catboost import CatBoostClassifier
from base_model import BaseModel

class CatBoostModel(BaseModel):
    def __init__(self, random_state: int = 42):
        super().__init__(model_name="CatBoost")
        self.model = CatBoostClassifier(
            random_state=random_state,
            verbose=False,
            thread_count=-1
        )

    def _train_logic(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        self.model.fit(X_train, y_train)

    def _predict_logic(self, X_test: pd.DataFrame) -> pd.Series:
        return self.model.predict(X_test)
