import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from scipy.stats import ks_2samp
import json
import logging
from datetime import datetime

# Configuración de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DriftDetector:
    def __init__(self, contamination=0.05):
        """
        Detector de anomalías usando Isolation Forest.
        Se entrena con los datos originales (baseline) y asume una pequeña tasa de "contaminación".
        """
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.baseline_data = None
        self.is_fitted = False

    def fit_baseline(self, X_train: pd.DataFrame):
        """Entrena el detector con los datos normales de entrenamiento."""
        logging.info("Entrenando detector de Isolation Forest con datos de linea base...")
        self.baseline_data = X_train
        self.model.fit(X_train)
        self.is_fitted = True
        
    def detect_anomalies(self, X_new: pd.DataFrame, threshold_percent=0.1) -> bool:
        """
        Si un porcentaje alto (> threshold) es clasificado como anomalía por el I-Forest,
        detectamos un posible Data Drift.
        """
        if not self.is_fitted:
            raise ValueError("Debes hacer fit_baseline primero.")
            
        logging.info(f"Evaluando {len(X_new)} nuevos registros buscando drift (Isolation Forest)...")
        # -1 son anomalías, 1 es inliers
        predictions = self.model.predict(X_new)
        anomaly_ratio = np.mean(predictions == -1)
        
        logging.info(f"Ratio de anomalías detectado: {anomaly_ratio:.2%}")
        
        if anomaly_ratio > threshold_percent:
            logging.warning(f"¡DRIFT DETECTADO (I-Forest)! Ratio {anomaly_ratio:.2%} superó el umbral {threshold_percent:.2%}")
            return True
        return False
        
    def check_statistical_drift(self, X_new: pd.DataFrame, p_value_threshold=0.05) -> dict:
        """
        Test Kolmogorov-Smirnov por cada característica.
        Compara la distribución de los nuevos datos vs baseline.
        """
        if self.baseline_data is None:
             raise ValueError("Baseline no definido. Ejecuta fit_baseline.")
             
        logging.info("Ejecutando Test Kolmogorov-Smirnov por variable...")
        drift_report = {}
        drift_detected_overall = False
        
        for col in self.baseline_data.columns:
            # Seleccionar muestra para acelerar si es muy grande
            b_sample = self.baseline_data[col].sample(n=min(5000, len(self.baseline_data)), random_state=42)
            n_sample = X_new[col].sample(n=min(5000, len(X_new)), random_state=42)
            
            # test K-S
            statistic, p_value = ks_2samp(b_sample, n_sample)
            
            # Si p < 0.05 (o umbral), rechazamos hipotesis nula (son diferentes distribuciones)
            is_drift = p_value < p_value_threshold
            drift_report[col] = {"p_value": p_value, "is_drift": is_drift}
            
            if is_drift:
                drift_detected_overall = True
                
        logging.info(f"Reporte K-S generado. Drift global: {drift_detected_overall}")
        return {"drift_detected": drift_detected_overall, "details": drift_report}


def simulate_data_drift():
    """Genera datos nuevos 'corruptos' o desfasados matemáticamente."""
    print("\n--- SIMULACIÓN DE DATA DRIFT ---")
    
    # 1. Cargar Base
    try:
        train_df = pd.read_csv("../../data/processed/train_smote.csv")
        target_col = 'isFraud'
        X_train = train_df.drop(columns=[target_col])
    except Exception as e:
        print(f"Error cargando base: {e}")
        return
        
    # 2. Instanciar Detector y Ajustar
    detector = DriftDetector(contamination=0.01)
    detector.fit_baseline(X_train)
    
    # 3. Datos Sin Drift (Similar a train)
    print("\n>>> CASO 1: Datos Normales")
    X_normal = X_train.sample(n=1000, random_state=42)
    # Test Isolation Forest
    detector.detect_anomalies(X_normal)
    # Test KS
    ks_results = detector.check_statistical_drift(X_normal)
    print(f"KS Drift Global: {ks_results['drift_detected']}")

    # 4. Datos Con Drift (Modificando fuertemente una o dos features)
    print("\n>>> CASO 2: Datos con Drift Simulado")
    X_drift = X_train.sample(n=1000, random_state=99).copy()
    
    # Simulamos que la feature1 sufre un pico inflacionario (valores multiplicados * 10)
    col_to_drift = X_drift.columns[0]
    X_drift[col_to_drift] = X_drift[col_to_drift] * 10 + 50 
    
    # Test Isolation Forest
    detector.detect_anomalies(X_drift)
    # Test KS
    drift_report = detector.check_statistical_drift(X_drift)
    
    if drift_report["drift_detected"]:
        print(f"‼️ ALERTA DE SISTEMA ‼️: Drift Estadístico detectado en la variable: {col_to_drift}")
        print(">>> TRIGGER DE REINYECCIÓN: Enviando solicitud a la cola de Kafka para programar reentrenamiento.")
        
        # Simulación de trigger
        event = {
            "event_type": "DATA_DRIFT_DETECTED",
            "timestamp": datetime.now().isoformat(),
            "reason": "KS Test falló la aserción de distribución.",
            "action_required": "Retrain Models (Batch) & Update Stream Classifier"
        }
        
        with open("drift_alert.json", "w") as f:
            json.dump(event, f, indent=4)
        print("Evento generado: drift_alert.json")


if __name__ == "__main__":
    simulate_data_drift()
