import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime
import matplotlib.pyplot as plt
import io

# -----------------------------
# CONFIGURACIÓN INICIAL
# -----------------------------
st.set_page_config(page_title="🧮 Auditoría de Duplicados en Facturación", layout="wide")
st.title("🔍 CAAT - Auditoría de Duplicados en Facturas")

st.markdown("""
Esta herramienta permite cargar un archivo Excel con múltiples hojas para detectar facturas posiblemente duplicadas.
- ✅ Puedes seleccionar las hojas que desees analizar.
- 🔍 El sistema identifica duplicados por número de factura, proveedor, monto o combinación de campos clave.
- 📤 Puedes exportar los resultados.
- 📊 Incluye gráficos y ranking por proveedor.
""")

# -----------------------------
# CARGA Y SELECCIÓN DE ARCHIVO
# -----------------------------
archivo = st.file_uploader("📁 Cargar archivo Excel con facturas", type=["xlsx"])

if archivo:
    excel = pd.ExcelFile(archivo)
    hojas = excel.sheet_names

    st.success(f"Archivo cargado con {len(hojas)} hoja(s).")
    hoja_a = st.selectbox("Selecciona la hoja para análisis", hojas)
    df = pd.read_excel(archivo, sheet_name=hoja_a)

    # -----------------------------
    # VALIDACIÓN Y PREPARACIÓN
    # -----------------------------
    columnas = df.columns.str.lower()
    df.columns = columnas

    if "numero_factura" in columnas and "proveedor_id" in columnas and "monto_total" in columnas:
        df["duplicado_numero"] = df.duplicated("numero_factura", keep=False)
        df["duplicado_prov_monto"] = df.duplicated(["proveedor_id", "monto_total"], keep=False)
        df["duplicado_campos_clave"] = df.duplicated(["numero_factura", "monto_total", "proveedor_id"], keep=False)
    else:
        st.warning("⚠️ El archivo no contiene las columnas necesarias para validar duplicados.")
        st.stop()

    # -----------------------------
    # RESUMEN DE HALLAZGOS
    # -----------------------------
    resumen = {
        "Registros procesados": len(df),
        "Duplicados por número de factura": df["duplicado_numero"].sum(),
        "Duplicados por proveedor y monto": df["duplicado_prov_monto"].sum(),
        "Duplicados por combinación de campos clave": df["duplicado_campos_clave"].sum(),
    }

    st.markdown("### 📊 Resumen del análisis")
    st.table(pd.DataFrame.from_dict(resumen, orient='index', columns=["Cantidad"]))

    # -----------------------------
    # TABLA DE FACTURAS SOSPECHOSAS
    # -----------------------------
    sospechosas = df[
        df["duplicado_numero"] | df["duplicado_prov_monto"] | df["duplicado_campos_clave"]
    ]
    st.markdown("### 🧾 Facturas sospechosas")
    st.dataframe(sospechosas, use_container_width=True)

    # -----------------------------
    # GRÁFICO
    # -----------------------------
    st.markdown("### 📈 Visualización")
    fig, ax = plt.subplots()
    ax.bar(resumen.keys(), resumen.values(), color='salmon')
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

    # -----------------------------
    # EXPORTACIÓN
    # -----------------------------
    st.markdown("### 📥 Descargar resultados")
    output = io.BytesIO()
    sospechosas.to_csv(output, index=False)
    st.download_button("⬇️ Descargar archivo CSV", output.getvalue(), file_name="facturas_sospechosas.csv", mime="text/csv")

    # -----------------------------
    # LOG DE AUDITORÍA (reiniciado por sesión)
    # -----------------------------
    usuario = "auditor_app"
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hash_archivo = hashlib.sha256(archivo.getvalue()).hexdigest()

    log = {
        "usuario": usuario,
        "fecha": fecha,
        "registros": len(df),
        "hash_archivo": hash_archivo,
        **resumen
    }

    st.markdown("### 🧾 Log de auditoría")
    st.json(log)
