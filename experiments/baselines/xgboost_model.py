import pandas as pd
import xgboost as xgb
from base_model import BaseModel

class XGBoostModel(BaseModel):
    def __init__(self, random_state: int = 42):
        super().__init__(model_name="XGBoost")
        self.model = xgb.XGBClassifier(
            random_state=random_state,
            use_label_encoder=False,
            eval_metric='logloss',
            n_jobs=-1
        )

    def _train_logic(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        self.model.fit(X_train, y_train)

    def _predict_logic(self, X_test: pd.DataFrame) -> pd.Series:
        return self.model.predict(X_test)
