import pandas as pd
from sklearn.linear_model import LogisticRegression
from base_model import BaseModel

class LogisticRegressionModel(BaseModel):
    def __init__(self, random_state: int = 42):
        super().__init__(model_name="Logistic_Regression")
        self.model = LogisticRegression(random_state=random_state, max_iter=1000)

    def _train_logic(self, X_train: pd.DataFrame, y_train: pd.Series) -> None:
        self.model.fit(X_train, y_train)

    def _predict_logic(self, X_test: pd.DataFrame) -> pd.Series:
        return self.model.predict(X_test)
