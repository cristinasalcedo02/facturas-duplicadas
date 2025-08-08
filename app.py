import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import hashlib

# ----------------------------
# CONFIGURACIÓN DE LA APP
# ----------------------------
st.set_page_config(page_title="Auditoría de Facturas", layout="wide")
st.title("🔎 Aplicación Interactiva para Auditoría de Facturas Duplicadas")

# ----------------------------
# INTRODUCCIÓN CON GUÍA
# ----------------------------
st.markdown("""
Esta aplicación permite realizar un análisis automatizado de facturas cargadas en un archivo Excel. Puedes subir un archivo con múltiples hojas, seleccionar qué hojas usar y analizar posibles duplicaciones, inconsistencias o coincidencias entre hojas.

**¿Cómo funciona?**
1. Sube un archivo `.xlsx` desde el panel lateral izquierdo.
2. Selecciona las hojas que deseas analizar como “Archivo A” y (opcionalmente) “Archivo B”.
3. La app detectará:
   - Registros duplicados dentro de cada hoja.
   - Coincidencias entre ambas hojas si seleccionas dos.
   - Resumen visual e indicadores clave de auditoría.
4. Descarga los resultados en Excel o CSV.

Este análisis se reinicia con cada ejecución y **no requiere columnas fijas**, por lo que puedes usar cualquier archivo compatible para auditorías futuras.
""")

# ----------------------------
# CARGA DE ARCHIVO EXCEL
# ----------------------------
archivo_excel = st.file_uploader("📤 Sube el archivo Excel (.xlsx)", type=["xlsx"])

if archivo_excel:
    xls = pd.ExcelFile(archivo_excel)
    hojas = xls.sheet_names

    hoja_a = st.selectbox("Selecciona la hoja para el análisis principal (Archivo A):", hojas)
    hoja_b = st.selectbox("Selecciona una hoja opcional para análisis cruzado (Archivo B):", ["(Ninguna)"] + hojas)

    df_a = pd.read_excel(xls, sheet_name=hoja_a)

    if hoja_b != "(Ninguna)":
        df_b = pd.read_excel(xls, sheet_name=hoja_b)
    else:
        df_b = None

    # ----------------------------
    # HASH DE INTEGRIDAD
    # ----------------------------
    archivo_hash = hashlib.sha256(archivo_excel.getvalue()).hexdigest()

    # ----------------------------
    # VALIDACIÓN BÁSICA Y ANÁLISIS
    # ----------------------------
    st.markdown("## 🧪 Resultados del Análisis")

    def detectar_duplicados(df):
        df = df.copy()
        df["duplicado_general"] = df.duplicated(keep=False)
        return df[df["duplicado_general"]], df

    duplicados_a, df_a = detectar_duplicados(df_a)

    st.markdown(f"### 📄 Resultados - Hoja: `{hoja_a}`")
    st.write(f"🔍 Se detectaron **{len(duplicados_a)}** registros duplicados.")
    if not duplicados_a.empty:
        st.dataframe(duplicados_a)

        csv_dup = duplicados_a.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Descargar duplicados", csv_dup, "duplicados_archivo_a.csv", "text/csv")

    # Ranking de usuarios (si existe columna 'usuario' o similar)
    posibles_usuarios = [col for col in df_a.columns if "usuario" in col.lower()]
    if posibles_usuarios:
        columna_usuario = posibles_usuarios[0]
        ranking = duplicados_a[columna_usuario].value_counts().reset_index()
        ranking.columns = ["Usuario", "Cantidad de duplicados"]
        st.markdown("#### 👥 Ranking de usuarios con más duplicados:")
        st.dataframe(ranking)

    # Visualización (opcional)
    if not duplicados_a.empty:
        fig = px.histogram(duplicados_a, x=duplicados_a.columns[0], title="Distribución de Duplicados")
        st.plotly_chart(fig)

    # ----------------------------
    # ANÁLISIS CRUZADO (OPCIONAL)
    # ----------------------------
    if df_b is not None:
        st.markdown("### 🔄 Análisis cruzado entre hojas")

        claves_comunes = list(set(df_a.columns) & set(df_b.columns))
        if claves_comunes:
            clave = st.selectbox("Selecciona la clave común para comparar:", claves_comunes)
            duplicados_cruzados = pd.merge(df_a, df_b, on=clave, how='inner')

            st.write(f"🔗 Se encontraron **{len(duplicados_cruzados)}** coincidencias entre ambas hojas.")
            st.dataframe(duplicados_cruzados)

            csv_cruzado = duplicados_cruzados.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Descargar coincidencias cruzadas", csv_cruzado, "coincidencias_cruzadas.csv", "text/csv")
        else:
            st.warning("⚠️ No se encontraron campos comunes entre las hojas para análisis cruzado.")

    # ----------------------------
    # LOG DE AUDITORÍA (REINICIABLE)
    # ----------------------------
    log_data = {
        "usuario": "auditor_app",
        "archivo_subido": archivo_excel.name,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "duplicados_archivo_a": len(duplicados_a),
        "coincidencias_cruzadas": len(duplicados_cruzados) if df_b is not None and claves_comunes else 0,
        "hash_integridad": archivo_hash
    }

    st.markdown("### 📋 Log de Auditoría")
    st.json(log_data)
