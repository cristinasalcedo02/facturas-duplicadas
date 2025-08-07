import streamlit as st
import pandas as pd
import hashlib
import matplotlib.pyplot as plt
from datetime import datetime

# ----------------------------
# CONFIGURACIÓN DE LA APP
# ----------------------------
st.set_page_config(page_title="CAAT - Auditoría de Facturas", layout="wide")
st.title("🧾 CAAT - Auditoría de Facturas Duplicadas")
st.markdown("""
Esta herramienta permite identificar facturas sospechosas de duplicación mediante análisis interno o cruzado. 
Puedes cargar un archivo Excel con múltiples hojas. Selecciona el tipo de análisis que deseas ejecutar.
""")

# ----------------------------
# SUBIDA DE ARCHIVO
# ----------------------------
archivo_excel = st.file_uploader("📤 Sube tu archivo Excel (.xlsx)", type=["xlsx"])

if archivo_excel:
    xls = pd.ExcelFile(archivo_excel)
    hojas = xls.sheet_names

    modo_analisis = st.radio("Selecciona el tipo de análisis:", ["📄 Hoja única", "🔀 Análisis cruzado entre hojas"])

    if modo_analisis == "📄 Hoja única":
        hoja = st.selectbox("Selecciona la hoja para analizar:", hojas)
        df = pd.read_excel(archivo_excel, sheet_name=hoja)

        columnas = df.columns.tolist()
        st.markdown("---")
        st.subheader("🔎 Selecciona las columnas para la prueba de duplicación")

        col1 = st.selectbox("Columna 1", columnas)
        col2 = st.selectbox("Columna 2", columnas)
        col3 = st.selectbox("Columna 3", columnas)

        df["duplicado"] = df.duplicated(subset=[col1, col2, col3], keep=False)

        sospechosas = df[df["duplicado"]]
        resumen = {
            "Total registros": len(df),
            "Duplicados detectados": sospechosas.shape[0],
            "Fecha análisis": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    else:
        hoja1 = st.selectbox("Selecciona la hoja A:", hojas, key="a")
        hoja2 = st.selectbox("Selecciona la hoja B:", hojas, key="b")

        df1 = pd.read_excel(archivo_excel, sheet_name=hoja1)
        df2 = pd.read_excel(archivo_excel, sheet_name=hoja2)

        columnas1 = df1.columns.tolist()
        columnas2 = df2.columns.tolist()

        st.markdown("---")
        st.subheader("🔗 Selecciona columnas clave para comparar entre hojas")

        col1_a = st.selectbox("Hoja A - Columna 1", columnas1)
        col2_a = st.selectbox("Hoja A - Columna 2", columnas1)
        col3_a = st.selectbox("Hoja A - Columna 3", columnas1)

        col1_b = st.selectbox("Hoja B - Columna 1", columnas2)
        col2_b = st.selectbox("Hoja B - Columna 2", columnas2)
        col3_b = st.selectbox("Hoja B - Columna 3", columnas2)

        df1["clave"] = df1[col1_a].astype(str) + df1[col2_a].astype(str) + df1[col3_a].astype(str)
        df2["clave"] = df2[col1_b].astype(str) + df2[col2_b].astype(str) + df2[col3_b].astype(str)

        df1["hash"] = df1["clave"].apply(lambda x: hashlib.sha256(x.encode()).hexdigest())
        df2["hash"] = df2["clave"].apply(lambda x: hashlib.sha256(x.encode()).hexdigest())

        duplicados = pd.merge(df1, df2, on="hash", suffixes=("_a", "_b"))

        resumen = {
            "Registros en Hoja A": len(df1),
            "Registros en Hoja B": len(df2),
            "Coincidencias encontradas": len(duplicados),
            "Fecha análisis": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    # ----------------------------
    # MOSTRAR RESULTADOS
    # ----------------------------
    st.markdown("---")
    st.subheader("📊 Resumen del análisis")
    for k, v in resumen.items():
        st.markdown(f"- **{k}**: {v}")

    if modo_analisis == "📄 Hoja única":
        st.subheader("📋 Facturas sospechosas dentro de la hoja")
        st.dataframe(sospechosas)
    else:
        st.subheader("📋 Coincidencias entre hojas")
        st.dataframe(duplicados)

    # ----------------------------
    # GRÁFICO
    # ----------------------------
    st.subheader("📈 Visualización de resultados")
    fig, ax = plt.subplots()
    ax.bar(resumen.keys(), [v for v in resumen.values() if isinstance(v, int)])
    ax.set_xticklabels(resumen.keys(), rotation=45, ha='right')
    st.pyplot(fig)

    # ----------------------------
    # LOG (se reinicia cada vez)
    # ----------------------------
    log = pd.DataFrame([resumen])
    log.to_csv("log_ejecucion.csv", index=False)
