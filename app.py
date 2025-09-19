
import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Valorador / Rúbrica – Calculadora", page_icon="🧮", layout="centered")

# -----------------------------
# Config defaults (can be edited in sidebar)
# -----------------------------
st.sidebar.title("Configuración de la rúbrica")
st.sidebar.caption("Puedes ajustar los máximos y mínimos globales.")

CUERPO_MAX = st.sidebar.number_input("Cuerpo – Puntaje máximo", min_value=1, max_value=500, value=75)
CUERPO_MIN_REQ = st.sidebar.number_input("Cuerpo – Mínimo requerido", min_value=0, max_value=CUERPO_MAX, value=45)

EQUIPO_MAX = st.sidebar.number_input("Equipo – Puntaje máximo", min_value=1, max_value=500, value=25)
EQUIPO_MIN_REQ = st.sidebar.number_input("Equipo – Mínimo requerido", min_value=0, max_value=EQUIPO_MAX, value=10)

GLOBAL_MIN_REQ = st.sidebar.number_input("Proyecto en General – Mínimo global requerido", min_value=0, max_value=CUERPO_MAX+EQUIPO_MAX, value=60)

st.sidebar.divider()

st.sidebar.subheader("Categorías de Equipo (auto-puntos)")
default_cats = {
    "Investigador/a Superior I": 6,
    "Investigador/a Principal II": 5,
    "Investigador/a Independiente III": 4,
    "Investigador/a Adjunto/a IV": 3,
    "Investigador/a Asistente V": 2,
    "Becario/a de Iniciación VI": 1,
    "Sin categorización / Externo": 0
}
categories = {}
for name, default in default_cats.items():
    categories[name] = st.sidebar.number_input(f"{name}", min_value=0, max_value=1000, value=int(default), step=1)

st.title("🧮 Valorador / Rúbrica – Calculadora automática")

st.markdown("""
Esta calculadora implementa las condiciones de aprobación pactadas:
- **APROBADO** solo si **Equipo ≥ {eq_min}**, **Cuerpo ≥ {cu_min}** y **Total ≥ {glob_min}**.
- En cualquier otro caso: **NO APROBADO**.
""".format(eq_min=EQUIPO_MIN_REQ, cu_min=CUERPO_MIN_REQ, glob_min=GLOBAL_MIN_REQ))

with st.expander("Opcional: cargar un archivo Excel de tu rúbrica (XLSX/XLSM) para adjuntar al informe"):
    uploaded = st.file_uploader("Sube tu plantilla (opcional)", type=["xlsx", "xlsm"])
    uploaded_bytes = uploaded.getvalue() if uploaded is not None else None

st.header("1) Equipo")
st.caption("Elige una categoría; el puntaje se asigna automáticamente según la configuración.")

equipo_cat = st.selectbox("Categoría del/la Investigador/a", list(categories.keys()), index=0)
equipo_pts_auto = categories.get(equipo_cat, 0)

# Permitir agregar puntajes adicionales de equipo que se sumen (componentes)
with st.expander("Componentes adicionales de Equipo (se suman) – opcional"):
    comp_cols = st.columns(3)
    comp_a = comp_cols[0].number_input("Componente A", min_value=0, max_value=1000, value=0, step=1)
    comp_b = comp_cols[1].number_input("Componente B", min_value=0, max_value=1000, value=0, step=1)
    comp_c = comp_cols[2].number_input("Componente C", min_value=0, max_value=1000, value=0, step=1)
    componentes_total = comp_a + comp_b + comp_c

equipo_total_raw = equipo_pts_auto + componentes_total
equipo_total = min(equipo_total_raw, EQUIPO_MAX)
st.metric("Puntaje Equipo", f"{equipo_total} / {EQUIPO_MAX}", delta=None)

st.header("2) Cuerpo")
st.caption("Cargá el puntaje global del Cuerpo o desglósalo por ítems.")

tab1, tab2 = st.tabs(["Puntaje global", "Desglose por ítems (opcional)"])

with tab1:
    cuerpo_global = st.number_input("Cuerpo – Puntaje total (0 a máximo)", min_value=0, max_value=CUERPO_MAX, value=0, step=1)

with tab2:
    st.write("Define y puntúa ítems del Cuerpo (se suman).")
    n_items = st.number_input("Cantidad de ítems", min_value=1, max_value=20, value=5, step=1)
    cuerpo_sum = 0
    item_min_breaches = []
    for i in range(1, n_items+1):
        with st.container(border=True):
            st.subheader(f"Ítem {i}")
            col = st.columns(3)
            nombre = col[0].text_input(f"Nombre del ítem {i}", value=f"Ítem {i}")
            min_req = col[1].number_input(f"Mínimo requerido {i}", min_value=0, max_value=CUERPO_MAX, value=0, step=1, key=f"min_{i}")
            puntaje = col[2].number_input(f"Puntaje {i}", min_value=0, max_value=CUERPO_MAX, value=0, step=1, key=f"pts_{i}")
            cuerpo_sum += puntaje
            if puntaje < min_req:
                item_min_breaches.append((nombre, min_req, puntaje))
    cuerpo_sum = min(cuerpo_sum, CUERPO_MAX)
    st.info(f"Puntaje Cuerpo por ítems (capado al máximo): **{cuerpo_sum} / {CUERPO_MAX}**")
    if item_min_breaches:
        st.warning("Algunos ítems están por debajo de su mínimo requerido: " + ", ".join([f"{n} ({p}/{m})" for n,m,p in item_min_breaches]))

# Seleccionar el puntaje de Cuerpo definitivo (si hay desglose, se puede usar ese)
use_items = st.toggle("Usar el puntaje del desglose por ítems como puntaje final del Cuerpo", value=False)
cuerpo_total = int(cuerpo_sum if use_items else cuerpo_global)
cuerpo_total = min(cuerpo_total, CUERPO_MAX)

st.metric("Puntaje Cuerpo", f"{cuerpo_total} / {CUERPO_MAX}", delta=None)

# -----------------------------
# Totales y regla de aprobación
# -----------------------------
total = cuerpo_total + equipo_total
aprobado = (equipo_total >= EQUIPO_MIN_REQ) and (cuerpo_total >= CUERPO_MIN_REQ) and (total >= GLOBAL_MIN_REQ)

st.header("3) Totales y condición")
cols = st.columns(3)
cols[0].metric("Total", f"{total} / {CUERPO_MAX + EQUIPO_MAX}")
cols[1].metric("Condición – Equipo", f"{'OK' if equipo_total >= EQUIPO_MIN_REQ else 'No alcanza'}")
cols[2].metric("Condición – Cuerpo", f"{'OK' if cuerpo_total >= CUERPO_MIN_REQ else 'No alcanza'}")

st.success("✅ **APROBADO**") if aprobado else st.error("❌ **NO APROBADO**")

# -----------------------------
# Exportar Informe
# -----------------------------
st.divider()
st.subheader("Exportar informe")
persona = st.text_input("Nombre del proyecto / postulante", value="Proyecto sin nombre")
observ = st.text_area("Observaciones", value="")

df_resumen = pd.DataFrame([{
    "Proyecto/Postulante": persona,
    "Categoría Equipo": equipo_cat,
    "Equipo (auto + componentes)": equipo_total,
    "Cuerpo": cuerpo_total,
    "Total": total,
    "Aprobado": "APROBADO" if aprobado else "NO APROBADO",
    "Condición Equipo (mín {})".format(EQUIPO_MIN_REQ): "OK" if equipo_total >= EQUIPO_MIN_REQ else "NO",
    "Condición Cuerpo (mín {})".format(CUERPO_MIN_REQ): "OK" if cuerpo_total >= CUERPO_MIN_REQ else "NO",
    "Mínimo Global requerido": GLOBAL_MIN_REQ,
    "Observaciones": observ
}])

st.dataframe(df_resumen, use_container_width=True)

def to_excel_bytes(df: pd.DataFrame) -> bytes:
    import io
    with pd.ExcelWriter(io.BytesIO(), engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Resumen")
        workbook  = writer.book
        worksheet = writer.sheets["Resumen"]
        for idx, col in enumerate(df.columns, 1):
            col_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(idx-1, idx-1, col_len)
        writer.save()
        data = writer.book.filename.getvalue()
    return data

excel_bytes = to_excel_bytes(df_resumen)
st.download_button("⬇️ Descargar resumen en Excel", data=excel_bytes, file_name="resumen_valorador.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Adjuntar también el archivo de rúbrica cargado (si hubo uno)
if uploaded is not None:
    st.download_button("⬇️ Descargar copia del archivo subido", data=uploaded_bytes, file_name=uploaded.name)

st.divider()
st.caption("Hecho con ❤️ en Streamlit. Puedes desplegarlo en Streamlit Community Cloud o en tu propio servidor.")
