import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px

# Configuración de página
st.set_page_config(
    page_title="Model Experiments Dashboard",
    page_icon="🤖",
    layout="wide"
)

# Estilos CSS
st.markdown("""
<style>
    .reportview-container {
        margin-top: -2em;
    }
    .stMetric-value {
        font-size: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

# Título y Descripción
st.title("🎯 Baseline Models Dashboard")
st.markdown("Monitorización de la Fase 0: **Comparativa de Modelos Batch** en la Detección de Fraude.")

# Función para cargar métricas
@st.cache_data(ttl=1)  # Recarga cada segundo si cambia
def load_metrics(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r') as f:
        metrics = json.load(f)
    return pd.DataFrame(metrics)

# Ruta del archivo (asume que se ejecuta desde experiments/baselines/)
METRICS_FILE = "metrics.json"

df_metrics = load_metrics(METRICS_FILE)

if df_metrics is None:
    st.warning(f"No se encontró el archivo `{METRICS_FILE}`. Ejecuta primero `python steps.py`.")
else:
    st.subheader("📊 Tabla Comparativa de Rendimiento")

    # Resaltar en la tabla
    st.dataframe(
        df_metrics.style.highlight_max(subset=['f1_score', 'recall', 'precision', 'accuracy'], 
                                       color='lightgreen', axis=0),
        use_container_width=True
    )

    st.markdown("---")

    # Gráficos
    st.subheader("📈 Análisis Visual")
    
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**F1-Score por Modelo (Equilibrio Precision/Recall)**")
        fig_f1 = px.bar(
            df_metrics, 
            x='model_name', 
            y='f1_score',
            labels={'model_name': 'Algoritmo', 'f1_score': 'F1 Score'},
            color='model_name',
            text_auto='.3f'
        )
        fig_f1.update_layout(showlegend=False)
        st.plotly_chart(fig_f1, use_container_width=True)

    with col2:
        st.markdown("**Recall por Modelo (Capacidad de detectar Fraude real)**")
        fig_recall = px.bar(
            df_metrics, 
            x='model_name', 
            y='recall',
            labels={'model_name': 'Algoritmo', 'recall': 'Recall (Sensibilidad)'},
            color='model_name',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            text_auto='.3f'
        )
        fig_recall.update_layout(showlegend=False)
        st.plotly_chart(fig_recall, use_container_width=True)

    st.markdown("---")
    
    # Análisis Insights
    st.subheader("💡 Insights Generados")
    best_f1_idx = df_metrics['f1_score'].idxmax()
    best_recall_idx = df_metrics['recall'].idxmax()
    
    best_f1_model = df_metrics.loc[best_f1_idx, 'model_name']
    best_recall_model = df_metrics.loc[best_recall_idx, 'model_name']
    
    st.info(f"""
    - **Mejor modelo en F1-Score (Equilibrio general):** `{best_f1_model}` ({df_metrics['f1_score'].max():.3f})
    - **Mejor modelo en Recall (Menos falsos negativos):** `{best_recall_model}` ({df_metrics['recall'].max():.3f})
    
    *En detección de fraude, suele priorizarse un alto **Recall** (capturar el mayor fraude posible), siempre y cuando la **Precision** no decaiga excesivamente.*
    """)

    st.sidebar.header("Información")
    st.sidebar.info(
        "Este dashboard lee automáticamente el archivo `metrics.json` generado por el orquestador `steps.py`."
    )
    if st.sidebar.button("↻ Actualizar Datos"):
        st.rerun()

