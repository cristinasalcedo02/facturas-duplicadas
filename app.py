from datetime import datetime
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import hashlib

# ----------------------------
# CONFIGURACIÓN DE LA APP
# ----------------------------
st.set_page_config(page_title="CAAT - Análisis de Facturas", layout="wide")
st.title("📊 CAAT - Herramienta de Auditoría de Facturas")

st.markdown("""
Esta herramienta de auditoría asistida por computadora (CAAT) permite analizar un archivo Excel con múltiples hojas para detectar posibles inconsistencias o duplicaciones en registros contables.

**Guía rápida de uso:**
1. 📂 Sube un archivo `.xlsx` que contenga tus datos en varias hojas.
2. ✅ Selecciona las hojas que desees analizar o comparar.
3. 🔎 La app detectará duplicados automáticamente.
4. 📊 Visualiza gráficos y resultados en tiempo real.
5. 📥 Exporta o documenta los hallazgos con integridad verificada.

Esta aplicación **es flexible**: no requiere campos predefinidos, lo que permite adaptarse a diferentes estructuras de datos.
""")

# ----------------------------
# CARGA DEL ARCHIVO
# ----------------------------
archivo = st.file_uploader("Sube el archivo Excel con múltiples hojas", type=["xlsx"])

if archivo:
    xls = pd.ExcelFile(archivo)
    hojas = xls.sheet_names
    hoja_a = st.selectbox("Selecciona la hoja para análisis A:", hojas, key="hoja_a")
    hoja_b = st.selectbox("Selecciona la hoja para análisis B (opcional):", hojas, key="hoja_b")

    df_a = pd.read_excel(xls, sheet_name=hoja_a)
    df_b = pd.read_excel(xls, sheet_name=hoja_b) if hoja_b != hoja_a else None

    st.markdown("### 📄 Vista previa del archivo A")
    st.dataframe(df_a.head())

    if df_b is not None:
        st.markdown("### 📄 Vista previa del archivo B")
        st.dataframe(df_b.head())

    # Detección de duplicados automáticos
    duplicados_a = df_a[df_a.duplicated(keep=False)]
    duplicados_b = df_b[df_b.duplicated(keep=False)] if df_b is not None else pd.DataFrame()

    st.markdown("### 🔍 Registros duplicados en el archivo A")
    st.dataframe(duplicados_a)

    if not duplicados_b.empty:
        st.markdown("### 🔍 Registros duplicados en el archivo B")
        st.dataframe(duplicados_b)

    # RESUMEN GRÁFICO
    resumen = {
        "Registros totales A": len(df_a),
        "Duplicados A": len(duplicados_a),
    }
    if df_b is not None:
        resumen["Registros totales B"] = len(df_b)
        resumen["Duplicados B"] = len(duplicados_b)

    st.markdown("### 📊 Gráfico resumen")
    fig, ax = plt.subplots()
    ax.bar(resumen.keys(), resumen.values(), color='cornflowerblue')
    ax.set_ylabel("Cantidad")
    ax.set_title("Resumen del análisis")
    ax.set_xticklabels(resumen.keys(), rotation=15, ha='right')
    st.pyplot(fig)

    # SHA256
    archivo.seek(0)
    sha256 = hashlib.sha256(archivo.read()).hexdigest()
    st.markdown(f"🛡️ **Hash SHA-256 del archivo:** `{sha256}`")

    # LOG (reiniciado en cada ejecución)
    hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log = pd.DataFrame([{
        "fecha": hora,
        "archivo": archivo.name,
        "hoja_a": hoja_a,
        "hoja_b": hoja_b,
        "registros_a": len(df_a),
        "duplicados_a": len(duplicados_a),
        "registros_b": len(df_b) if df_b is not None else "",
        "duplicados_b": len(duplicados_b) if not duplicados_b.empty else "",
        "hash": sha256
    }])
    st.markdown("### 📋 Log de auditoría de esta ejecución")
    st.dataframe(log)

else:
    st.info("🔺 Por favor, sube un archivo Excel para comenzar.")
