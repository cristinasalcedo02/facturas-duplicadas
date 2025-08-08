import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime
import plotly.express as px

# ---------------------------
# CONFIGURACIÓN DE LA APP
# ---------------------------
st.set_page_config(page_title="CAAT - Detección de Duplicados", layout="wide")
st.title("🧾 CAAT - Detección de Facturas Duplicadas")

# ---------------------------
# INTRODUCCIÓN Y GUÍA
# ---------------------------
st.markdown("""
Esta herramienta de auditoría permite detectar facturas sospechosas de duplicación dentro de archivos Excel cargados por el usuario.  
✅ **Guía rápida de uso**:
1. Sube un archivo Excel con al menos **dos hojas** que contengan tus datos contables o financieros.
2. Selecciona qué hoja deseas analizar como “Archivo A” y cuál como “Archivo B”.
3. La app identificará duplicados dentro de cada hoja y entre ambas.
4. Revisa los hallazgos, exporta resultados y guarda evidencias del análisis.

**Nota**: No se requiere una estructura específica de nombres de columnas. La app se adapta dinámicamente a los datos proporcionados.
""")

# ---------------------------
# CARGA DEL ARCHIVO EXCEL
# ---------------------------
archivo_excel = st.file_uploader("📤 Sube tu archivo Excel con varias hojas", type=["xlsx"])
if archivo_excel:
    xls = pd.ExcelFile(archivo_excel)
    hojas_disponibles = xls.sheet_names
    hoja_a = st.selectbox("📄 Selecciona la hoja para Archivo A", hojas_disponibles)
    hoja_b = st.selectbox("📄 Selecciona la hoja para Archivo B (opcional)", hojas_disponibles)

    df_a = pd.read_excel(xls, sheet_name=hoja_a)
    df_b = pd.read_excel(xls, sheet_name=hoja_b) if hoja_b else None

    # ---------------------------
    # VALIDACIONES Y HASH
    # ---------------------------
    def calcular_hash(df):
        return hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values).hexdigest()

    hash_a = calcular_hash(df_a)
    hash_b = calcular_hash(df_b) if df_b is not None else ""

    # ---------------------------
    # DETECCIÓN DE DUPLICADOS
    # ---------------------------
    def detectar_duplicados(df):
        df_temp = df.copy()
        duplicados = {}
        for col in df.columns:
            duplicados[f"duplicado_{col}"] = df.duplicated(subset=[col], keep=False)
        duplicados_df = pd.concat([df_temp, pd.DataFrame(duplicados)], axis=1)
        return duplicados_df

    resultado_a = detectar_duplicados(df_a)
    resultado_b = detectar_duplicados(df_b) if df_b is not None else None

    # ---------------------------
    # ANÁLISIS CRUZADO
    # ---------------------------
    coincidencias = pd.DataFrame()
    if df_b is not None:
        columnas_comunes = list(set(df_a.columns).intersection(set(df_b.columns)))
        if columnas_comunes:
            coincidencias = pd.merge(df_a, df_b, on=columnas_comunes, how="inner")

    # ---------------------------
    # RESUMEN Y RESULTADOS
    # ---------------------------
    st.subheader("📊 Resumen del Análisis")
    resumen = {
        "Total de registros en Archivo A": len(df_a),
        "Total de duplicados en A (por columnas)": sum(resultado_a.filter(like="duplicado_").any(axis=1)),
        "Hash de integridad A": hash_a,
    }

    if df_b is not None:
        resumen["Total de registros en Archivo B"] = len(df_b)
        resumen["Total de duplicados en B (por columnas)"] = sum(resultado_b.filter(like="duplicado_").any(axis=1))
        resumen["Hash de integridad B"] = hash_b
        resumen["Coincidencias exactas entre A y B"] = len(coincidencias)

    for clave, valor in resumen.items():
        st.markdown(f"- **{clave}**: {valor}")

    # ---------------------------
    # GRÁFICO DE DUPLICADOS
    # ---------------------------
    st.subheader("📈 Visualización de duplicados")
    grafico_data = pd.DataFrame({
        "Categoría": ["Duplicados A", "Duplicados B", "Coincidencias entre A y B"],
        "Cantidad": [
            resumen.get("Total de duplicados en A (por columnas)", 0),
            resumen.get("Total de duplicados en B (por columnas)", 0),
            resumen.get("Coincidencias exactas entre A y B", 0)
        ]
    })
    fig = px.bar(grafico_data, x="Categoría", y="Cantidad", text="Cantidad", color="Categoría")
    st.plotly_chart(fig)

    # ---------------------------
    # DESCARGA DE RESULTADOS
    # ---------------------------
    st.subheader("📥 Exportar resultados")
    if not resultado_a.empty:
        resultado_a.to_csv("resultado_a.csv", index=False)
        st.download_button("Descargar resultados de Archivo A", data=resultado_a.to_csv(index=False), file_name="resultado_a.csv", mime="text/csv")

    if df_b is_
