import pandas as pd
from sklearn.datasets import make_classification
import os

def generate_balanced_data():
    os.makedirs("data/raw", exist_ok=True)
    
    # 1. Dataset Balanceado de Transacciones
    X_bin, y_bin = make_classification(
        n_samples=1000, 
        n_features=12, 
        n_informative=8, 
        n_redundant=2,
        weights=[0.5, 0.5], 
        random_state=42
    )
    df_binary = pd.DataFrame(X_bin, columns=[f"feature_{i}" for i in range(12)])
    df_binary["target"] = y_bin
    df_binary.to_csv("data/raw/balanced_binary_dataset.csv", index=False)
    
    # 2. Dataset Balanceado Multiclase
    X_multi, y_multi = make_classification(
        n_samples=1500, 
        n_features=15, 
        n_informative=10, 
        n_redundant=3,
        n_classes=3,
        weights=[0.33, 0.33, 0.34], 
        random_state=100
    )
    df_multi = pd.DataFrame(X_multi, columns=[f"feature_{i}" for i in range(15)])
    df_multi["target"] = y_multi
    df_multi.to_csv("data/raw/balanced_multiclass_dataset.csv", index=False)
    
    print("? Datasets balanceados generados exitosamente en la carpeta 'data/raw/'")

if __name__ == "__main__":
    generate_balanced_data()

