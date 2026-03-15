import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime
from scipy.stats import ks_2samp

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def simulate_environment_drift(train_csv: str):
    """
    Simulación de Data Drift mediante el Test No Paramétrico de Kolmogorov-Smirnov.
    Evalúa empíricamente si la distribución de una variable continua cambió.
    """
    print("\n" + "="*50)
    print("🚨 SIMULADOR DE DRIFT (KOLMOGOROV-SMIRNOV TEST)")
    print("="*50 + "\n")
    
    try:
        df_base = pd.read_csv(train_csv).drop(columns=['isFraud'])
    except Exception as e:
        logging.error("No se pudo cargar la data base.")
        return

    # Escogemos la primera variable numérica para la prueba
    col_analizada = df_base.columns[0]
    
    logging.info(f"Fijando distribución Base (Baseline de producción) para la feature: '{col_analizada}'")
    baseline_dist = df_base[col_analizada].sample(n=min(5000, len(df_base)), random_state=42)
    
    # ---------------------------------------------------------
    # CASO 1: Ingestando datos normales (No Drift)
    # ---------------------------------------------------------
    logging.info("\n>>> ESCENARIO 1: Lote de datos estables recibidos.")
    lote_normal = df_base.sample(n=min(5000, len(df_base)), random_state=99)[col_analizada]
    
    stat, p_val = ks_2samp(baseline_dist, lote_normal)
    logging.info(f"Resultado K-S | P-Value: {p_val:.4f}")
    if p_val < 0.05:
         logging.warning("Se detectó Drift en el escenario 1.")
    else:
         logging.info("Distribuciones idénticas. No se requiere acción.")

    # ---------------------------------------------------------
    # CASO 2: Ingestando datos anómalos (Inflación / Alteración de sistema)
    # ---------------------------------------------------------
    logging.info("\n>>> ESCENARIO 2: Lote de datos con perturbación detectada (Drift).")
    # Simulamos que los valores se desplazaron (un offset constante más ruido)
    lote_drifteado = lote_normal * 1.5 + 200 
    
    stat, p_val_drift = ks_2samp(baseline_dist, lote_drifteado)
    logging.info(f"Resultado K-S | P-Value: {p_val_drift:.4e}")
    
    if p_val_drift < 0.05:
         logging.error(f"¡K-S TEST FALLIDO! La distribución de '{col_analizada}' cambió estadísticamente respecto al baseline.")
         
         # Emular el Trigger de Reinyección
         logging.info(">>> DISPARANDO EVENTO: 'RETRAIN_REQUIRED'")
         json_payload = {
             "trigger": "DATA_DRIFT",
             "algorithm": "Kolmogorov-Smirnov Test",
             "feature": col_analizada,
             "p_value": p_val_drift,
             "timestamp": datetime.utcnow().isoformat() + "Z",
             "action": "Enviar lote a Feature Store y disparar DAG de Re-entrenamiento (Airflow/Prefect)"
         }
         
         with open("drift_alert.json", "w") as f:
             json.dump(json_payload, f, indent=4)
             
         logging.info("Payload de alerta guardado en 'drift_alert.json' (Simulando push a Kafka/RabbitMQ).")

if __name__ == "__main__":
    simulate_environment_drift("../../data/processed/train_smote.csv")
