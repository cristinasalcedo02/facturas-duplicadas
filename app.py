import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime
import plotly.express as px

# ---------------------------------
# CONFIGURACIÓN INICIAL DE LA APP
# ---------------------------------
st.set_page_config(page_title="🔎 CAAT - Análisis de Facturas", layout="wide")

st.title("🔎 CAAT - Herramienta de Auditoría de Facturas Duplicadas")
st.markdown("""
Esta aplicación permite cargar un archivo de Excel y seleccionar las hojas para análisis individual o cruzado.
Ideal para detectar duplicaciones, validar integridad y generar reportes de auditoría.
""")

# ---------------------------------
# CARGA DEL ARCHIVO
# ---------------------------------
archivo = st.file_uploader("📁 Sube el archivo Excel con múltiples hojas", type=["xlsx"])

if archivo:
    hojas = pd.ExcelFile(archivo).sheet_names
    hoja_a = st.selectbox("Selecciona la hoja para el Análisis Principal (A):", hojas)
    hoja_b = st.selectbox("¿Deseas comparar con otra hoja? (B) (opcional):", ["(Sin comparación)"] + hojas)

    df_a = pd.read_excel(archivo, sheet_name=hoja_a)

    if hoja_b != "(Sin comparación)":
        df_b = pd.read_excel(archivo, sheet_name=hoja_b)
    else:
        df_b = None

    # ---------------------------------
    # FUNCIONES AUXILIARES
    # ---------------------------------
    def hash_archivo(file_bytes):
        return hashlib.sha256(file_bytes.read()).hexdigest()

    def detectar_duplicados(df):
        df = df.copy()
        duplicados_por_fila = df.duplicated(keep=False)
        df["duplicado_fila"] = duplicados_por_fila
        return df

    def comparar_dataframes(df1, df2):
        comunes = pd.merge(df1, df2, how="inner")
        return comunes

    # ---------------------------------
    # PROCESAMIENTO
    # ---------------------------------
    resumen = {}

    st.subheader("🔍 Resultados del análisis")

    df_a_proc = detectar_duplicados(df_a)
    total_duplicados = df_a_proc["duplicado_fila"].sum()
    resumen["Duplicados en hoja A"] = total_duplicados

    if df_b is not None:
        cruzados = comparar_dataframes(df_a, df_b)
        resumen["Registros cruzados duplicados entre A y B"] = len(cruzados)
    else:
        cruzados = None

    resumen["Total registros en A"] = len(df_a)

    # ---------------------------------
    # DESCARGA DEL REPORTE
    # ---------------------------------
    st.download_button("📥 Descargar resultados (CSV)", data=df_a_proc.to_csv(index=False), file_name="resultado_auditoria.csv")

    # ---------------------------------
    # RESUMEN VISUAL Y GRÁFICO
    # ---------------------------------
    st.markdown("### 📊 Resumen del análisis:")
    resumen_df = pd.DataFrame.from_dict(resumen, orient="index", columns=["Cantidad"])
    st.dataframe(resumen_df)

    fig = px.bar(resumen_df, x=resumen_df.index, y="Cantidad", title="Distribución de Hallazgos")
    st.plotly_chart(fig)

    # ---------------------------------
    # LOG DE EJECUCIÓN TEMPORAL
    # ---------------------------------
    st.markdown("#### 🧾 Log de auditoría (sesión actual):")
    log = {
        "usuario": "auditor",
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "archivo_subido": archivo.name,
        "hash_archivo": hash_archivo(archivo),
        "total_registros": len(df_a),
        "duplicados_en_A": total_duplicados,
        "cruzados_AB": len(cruzados) if cruzados is not None else 0
    }
    st.json(log)
