import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Suite de Benchmarks Fase 0", layout="wide")

st.title("🛡️ Suite de Detección de Fraude - Fase 0 (Baselines)")
st.markdown("Comparativa de modelos Batch con estrategia de mitigación de desbalanceo (SMOTE).")

@st.cache_data(ttl=2)
def cargar_datos():
    if not os.path.exists("metrics.json"):
        return None
    with open("metrics.json", "r") as f:
        return pd.DataFrame(json.load(f))

df = cargar_datos()

if df is None:
    st.error("Archivo `metrics.json` no encontrado. Ejecuta `python steps.py` primero.")
else:
    # 1. KPIs Generales
    mejores_modelos = df.sort_values(by="f1_score", ascending=False).iloc[0]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Modelo Top (F1)", mejores_modelos['model_name'])
    col2.metric("Mejor Recall", df.loc[df['recall'].idxmax()]['model_name'])
    col3.metric("Entrenamiento más rápido", df.loc[df['train_time_sec'].idxmin()]['model_name'])
    col4.metric("Inferencia más rápida", df.loc[df['infer_time_sec'].idxmin()]['model_name'])
    
    st.divider()

    # 2. Tabla Comparativa
    st.subheader("📑 Resultados Analíticos Consolidado")
    
    # Formateo de la tabla de display
    df_display = df.drop(columns=['confusion_matrix']).copy()
    
    st.dataframe(
        df_display.style.highlight_max(subset=['accuracy', 'precision', 'recall', 'f1_score'], color='#004d00', axis=0) \
                        .highlight_min(subset=['train_time_sec', 'infer_time_sec'], color='#004d00', axis=0) \
                        .format({col: "{:.4f}" for col in df_display.columns if col != 'model_name'}),
        use_container_width=True
    )

    st.divider()
    
    # 3. Gráficas Lado a Lado
    st.subheader("📊 Comparativa de Rendimiento y Latencia")
    
    tab1, tab2 = st.tabs(["Métricas de Clasificación", "Latencias de Cómputo"])
    
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            fig_f1 = px.bar(df, x="model_name", y="f1_score", color="model_name", 
                            title="F1-Score (Trade-off Precision/Recall)", text_auto=".3f")
            fig_f1.update_layout(showlegend=False)
            st.plotly_chart(fig_f1, use_container_width=True)
            
        with c2:
            fig_rec = px.bar(df, x="model_name", y="recall", color="model_name",
                             title="Recall (Captura Total de Fraudes)", text_auto=".3f")
            fig_rec.update_layout(showlegend=False)
            st.plotly_chart(fig_rec, use_container_width=True)
            
    with tab2:
        c3, c4 = st.columns(2)
        with c3:
            fig_train = px.bar(df, x="model_name", y="train_time_sec", color="model_name",
                               title="Tiempo de Entrenamiento (Segundos)", text_auto=".2f")
            fig_train.update_layout(showlegend=False)
            st.plotly_chart(fig_train, use_container_width=True)
            
        with c4:
            fig_inf = px.bar(df, x="model_name", y="infer_time_sec", color="model_name",
                              title="Latencia de Inferencia por Lote (Segundos)", text_auto=".4f")
            fig_inf.update_layout(showlegend=False)
            st.plotly_chart(fig_inf, use_container_width=True)

    st.divider()

    # 4. Matrices de Confusión Dinámicas
    st.subheader("📉 Análisis de Matrices de Confusión")
    
    modelo_seleccionado = st.selectbox("Selecciona un modelo para ver su Matriz de Confusión", df['model_name'])
    
    cm = df[df['model_name'] == modelo_seleccionado]['confusion_matrix'].values[0]
    
    fig_cm = go.Figure(data=go.Heatmap(
        z=cm,
        x=['Predic. No Fraude', 'Predic. Fraude'],
        y=['Real No Fraude', 'Real Fraude'],
        hoverongaps=False,
        colorscale='Blues',
        text=[[str(val) for val in row] for row in cm],
        texttemplate="%{text}",
        textfont={"size": 20}
    ))
    fig_cm.update_layout(width=500, height=500)
    
    col_cm1, col_cm2 = st.columns([1, 2])
    with col_cm1:
        st.plotly_chart(fig_cm, use_container_width=True)
    with col_cm2:
         st.markdown(f"**Insights del modelo {modelo_seleccionado}:**")
         st.markdown(f"- **Verdaderos Negativos (TN):** {cm[0][0]} -> Operaciones sanas permitidas.")
         st.markdown(f"- **Falsos Positivos (FP):** {cm[0][1]} -> Fricción con cliente (Bloqueaste a un inocente).")
         st.markdown(f"- **Falsos Negativos (FN):** {cm[1][0]} -> **PERDIDA DE DINERO** (Fraude ignorado).")
         st.markdown(f"- **Verdaderos Positivos (TP):** {cm[1][1]} -> Fraude bloqueado con éxito.")
         
         st.info("💡 En detección de fraude bancario, en Fase Batch buscamos minimizar los **FN** mientras mantenemos los **FP** dentro del umbral tolerado por Riesgos.")

