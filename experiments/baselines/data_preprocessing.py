import pandas as pd
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import os

def prepare_data(raw_data_path: str, processed_dir: str, sample_size: int = 200000):
    """
    Carga el dataset crudo, toma una muestra, divide en train/test,
    aplica SMOTE solo al conjunto de entrenamiento y guarda los resultados.
    """
    print(f"Cargando datos desde {raw_data_path}...")
    
    # IMPORTANTE: Reemplazar 'DATASET1.CSV' por el nombre real de tu archivo
    # y asegurarse de que exista en la ruta especificada.
    try:
        # Aquí simulo la carga si el archivo no existe para que puedas probar el pipeline
        # En la realidad, deberías usar: df = pd.read_csv(raw_data_path)
        if not os.path.exists(raw_data_path):
            print(f"Archivo no encontrado en {raw_data_path}. Generando datos de prueba...")
            import numpy as np
            # Generando datos simulados con desbalanceo extremo
            np.random.seed(42)
            n_samples = max(sample_size, 10000)
            df = pd.DataFrame({
                'feature1': np.random.randn(n_samples),
                'feature2': np.random.rand(n_samples) * 100,
                'feature3': np.random.randint(0, 10, n_samples),
                'isFraud': np.random.choice([0, 1], p=[0.99, 0.01], size=n_samples) # 1% fraude
            })
            # Asegurar que la columna objetivo se llame 'isFraud' o adaptar esto
            target_col = 'isFraud'
        else:
            df = pd.read_csv(raw_data_path)
            # Reemplaza 'isFraud' por el nombre de tu columna objetivo real
            target_col = 'isFraud' 
    except Exception as e:
        print(f"Error cargando o simulando datos: {e}")
        return

    # 1. Tomar muestra
    print(f"Tomando muestra de {sample_size} registros...")
    if len(df) > sample_size:
        df = df.sample(n=sample_size, random_state=42)
    
    X = df.drop(columns=[target_col])
    y = df[target_col]

    # 2. Split 80/20
    print("Dividiendo en Train/Test (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print(f"Distribución Train ANTES de SMOTE: \n{y_train.value_counts()}")
    print(f"Distribución Test (Original real): \n{y_test.value_counts()}")

    # 3. Aplicar SMOTE *SOLO* al Train
    print("Aplicando SMOTE al conjunto de entrenamiento...")
    smote = SMOTE(random_state=42)
    X_train_sm, y_train_sm = smote.fit_resample(X_train, y_train)

    print(f"Distribución Train DESPUÉS de SMOTE: \n{y_train_sm.value_counts()}")

    # 4. Guardar procesados
    os.makedirs(processed_dir, exist_ok=True)
    
    print(f"Guardando datasets procesados en {processed_dir}...")
    # Convirtiendo a DataFrame para guardar fácilmente
    train_sm_df = pd.concat([pd.DataFrame(X_train_sm, columns=X.columns), pd.Series(y_train_sm, name=target_col)], axis=1)
    test_df = pd.concat([pd.DataFrame(X_test, columns=X.columns), pd.Series(y_test, name=target_col)], axis=1)

    train_sm_df.to_csv(os.path.join(processed_dir, "train_smote.csv"), index=False)
    test_df.to_csv(os.path.join(processed_dir, "test_resampled.csv"), index=False)
    
    print("Preprocesamiento finalizado con éxito.")

if __name__ == "__main__":
    # Rutas relativas al script actual asumiendo que se ejecuta desde la raíz
    RAW_PATH = "../../data/raw/DATASET1.CSV"
    PROCESSED_PATH = "../../data/processed/"
    prepare_data(RAW_PATH, PROCESSED_PATH)
