import pandas as pd
import lightgbm as lgb
from base_model import BaseModel

class LightGBMModel(BaseModel):
    def __init__(self, random_state: int = 42):
        super().__init__(model_name="LightGBM")
        self.model = lgb.LGBMClassifier(
            random_state=random_state,
            n_jobs=-1
        )

    def _train_logic(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        self.model.fit(X_train, y_train)

    def _predict_logic(self, X_test: pd.DataFrame) -> pd.Series:
        return self.model.predict(X_test)
