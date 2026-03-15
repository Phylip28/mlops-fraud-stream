import pandas as pd
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import os
import math

def prepare_data(raw_data_path: str, processed_dir: str, sample_size: int = 200000):
    """
    Carga el dataset, extrae una muestra estratificada, divide en train/test,
    aplica SMOTE exclusivamente al train y guarda los resultados.
    """
    print(f"Cargando datos desde {raw_data_path}...")
    
    try:
        if not os.path.exists(raw_data_path):
            print(f"Archivo no encontrado en {raw_data_path}. Generando datos distribuidos con desbalanceo...")
            import numpy as np
            np.random.seed(42)
            n_samples = max(sample_size, 10000)
            df = pd.DataFrame({
                'amount': np.random.exponential(100, n_samples),
                'oldbalanceOrg': np.random.rand(n_samples) * 50000,
                'newbalanceOrig': np.random.rand(n_samples) * 50000,
                'isFraud': np.random.choice([0, 1], p=[0.995, 0.005], size=n_samples)
            })
            target_col = 'isFraud'
        else:
            df = pd.read_csv(raw_data_path)
            target_col = 'isFraud' 
    except Exception as e:
        print(f"Error cargando o simulando datos: {e}")
        return

    # 1. Tomar muestra estratificada
    print(f"Extrayendo muestra estratificada de {sample_size} registros...")
    if len(df) > sample_size:
        # Muestra balanceada de modo que se guarde la misma proporcion de fraude
        df_sample, _ = train_test_split(df, train_size=sample_size, stratify=df[target_col], random_state=42)
    else:
        df_sample = df.copy()
    
    X = df_sample.drop(columns=[target_col])
    y = df_sample[target_col]

    # 2. Split 80/20 (Estratificado para la validación real)
    print("Dividiendo en Train/Test (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print(f"Distribución original en Train: \n{y_train.value_counts(normalize=True)*100}\n")
    print(f"Distribución intacta en Test: \n{y_test.value_counts(normalize=True)*100}\n")

    # 3. Aplicar SMOTE *SOLO* al Train
    print("Aplicando SMOTE al conjunto de entrenamiento...")
    smote = SMOTE(random_state=42)
    X_train_sm, y_train_sm = smote.fit_resample(X_train, y_train)

    print(f"Distribución FINAL en Train (Tras SMOTE): \n{y_train_sm.value_counts(normalize=True)*100}")

    # 4. Guardar datasets
    os.makedirs(processed_dir, exist_ok=True)
    
    print(f"Guardando datasets en {processed_dir}...")
    train_sm_df = pd.concat([pd.DataFrame(X_train_sm, columns=X.columns), pd.Series(y_train_sm, name=target_col)], axis=1)
    test_df = pd.concat([pd.DataFrame(X_test, columns=X.columns), pd.Series(y_test, name=target_col)], axis=1)

    train_sm_df.to_csv(os.path.join(processed_dir, "train_smote.csv"), index=False)
    test_df.to_csv(os.path.join(processed_dir, "test_resampled.csv"), index=False)
    
    print("✅ Preprocesamiento completado. No se inyectó ruido al Test set.")

if __name__ == "__main__":
    RAW_PATH = "../../data/raw/DATASET1.CSV"
    PROCESSED_PATH = "../../data/processed/"
    prepare_data(RAW_PATH, PROCESSED_PATH)
