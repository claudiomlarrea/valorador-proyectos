
import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Valorador / Rúbrica – Calculadora", page_icon="🧮", layout="wide")

# ---------- Parámetros configurables ----------
st.sidebar.title("Configuración")
CUERPO_MAX = st.sidebar.number_input("Cuerpo – Puntaje máximo", 1, 1000, 75)
CUERPO_MIN_REQ = st.sidebar.number_input("Cuerpo – Mínimo requerido", 0, CUERPO_MAX, 45)
EQUIPO_MIN_REQ = st.sidebar.number_input("Equipo – Mínimo requerido", 0, 1000, 10)
GLOBAL_MIN_REQ = st.sidebar.number_input("Mínimo global requerido", 0, 1000, 60)

# Categorías y puntos del equipo (fijos)
CATEGORIAS = {
    "Investigador/a Superior I": 6,
    "Investigador/a Principal II": 5,
    "Investigador/a Independiente III": 4,
    "Investigador/a Adjunto/a IV": 3,
    "Investigador/a Asistente V": 2,
    "Becario/a de Iniciación VI": 1,
    "Sin categorización / Externo": 0,
}

# ---------- Escalas ordinales (1–3) ----------
SCALES = {
    "incluye": [("Incluye totalmente (3)", 3), ("Incluye parcialmente (2)", 2), ("Incluye insuficientemente (1)", 1)],
    "cumple": [("Cumple totalmente (3)", 3), ("Cumple parcialmente (2)", 2), ("Cumple insuficientemente (1)", 1)],
    "evidencia_pertinencia": [("Evidencia pertinencia plenamente (3)", 3), ("Evidencia pertinencia parcialmente (2)", 2), ("Evidencia pertinencia insuficientemente (1)", 1)],
    "define_aporte": [("Define el aporte claramente (3)", 3), ("Define el aporte parcialmente (2)", 2), ("Define el aporte insuficientemente (1)", 1)],
    "sustenta_viabilidad": [("Sustenta viabilidad plenamente (3)", 3), ("Sustenta viabilidad parcialmente (2)", 2), ("Sustenta viabilidad insuficientemente (1)", 1)],
    "formula_tecnicamente": [("Formula técnicamente de modo correcto (3)", 3), ("Formula técnicamente de modo parcial (2)", 2), ("Formula técnicamente de modo insuficiente (1)", 1)],
    "especifica": [("Especifica claramente (3)", 3), ("Especifica parcialmente (2)", 2), ("Especifica insuficientemente (1)", 1)],
    "medible_operacional": [("Es medible/operacional plenamente (3)", 3), ("Es medible/operacional parcialmente (2)", 2), ("Es medible/operacional insuficientemente (1)", 1)],
    "temporalidad": [("Delimita temporalidad claramente (3)", 3), ("Delimita temporalidad parcialmente (2)", 2), ("Delimita temporalidad insuficientemente (1)", 1)],
    "articula_perspectiva": [("Articula coherentemente la perspectiva (3)", 3), ("Articula parcialmente la perspectiva (2)", 2), ("Articula insuficientemente la perspectiva (1)", 1)],
    "define_variables": [("Define variables claramente (3)", 3), ("Define variables parcialmente (2)", 2), ("Define variables insuficientemente (1)", 1)],
    "integra_antecedentes": [("Integra antecedentes pertinentes plenamente (3)", 3), ("Integra antecedentes pertinentes parcialmente (2)", 2), ("Integra antecedentes pertinentes insuficientemente (1)", 1)],
    "analisis_critico": [("Realiza análisis crítico sólido (3)", 3), ("Realiza análisis crítico parcial (2)", 2), ("Realiza análisis crítico insuficiente (1)", 1)],
    "delimita_brecha": [("Delimita claramente la brecha (3)", 3), ("Delimita parcialmente la brecha (2)", 2), ("Delimita insuficientemente la brecha (1)", 1)],
    "es_pertinente": [("Es pertinente (3)", 3), ("Es parcialmente pertinente (2)", 2), ("Es insuficientemente pertinente (1)", 1)],
    "delimita": [("Delimita claramente (3)", 3), ("Delimita parcialmente (2)", 2), ("Delimita insuficientemente (1)", 1)],
    "congruencia_instrumentos": [("Totalmente congruentes (3)", 3), ("Parcialmente congruentes (2)", 2), ("Insuficientemente congruentes (1)", 1)],
    "describe": [("Describe claramente (3)", 3), ("Describe parcialmente (2)", 2), ("Describe insuficientemente (1)", 1)],
    "permiten": [("Permiten plenamente (3)", 3), ("Permiten parcialmente (2)", 2), ("Permiten insuficientemente (1)", 1)],
    "explicita": [("Explicita claramente (3)", 3), ("Explicita parcialmente (2)", 2), ("Explicita insuficientemente (1)", 1)],
    "reconoce": [("Reconoce claramente (3)", 3), ("Reconoce parcialmente (2)", 2), ("Reconoce insuficientemente (1)", 1)],
    "fuentes_calidad": [("Selecciona fuentes académicas de calidad plenamente (3)", 3), ("Selecciona fuentes académicas de calidad parcialmente (2)", 2), ("Selecciona fuentes académicas de calidad insuficientemente (1)", 1)],
    "actualidad": [("Acredita actualidad plenamente (3)", 3), ("Acredita actualidad parcialmente (2)", 2), ("Acredita actualidad insuficientemente (1)", 1)],
    "norma": [("Se ajusta plenamente a la norma (3)", 3), ("Se ajusta parcialmente a la norma (2)", 2), ("Se ajusta insuficientemente a la norma (1)", 1)],
    "alinea": [("Alinea plenamente (3)", 3), ("Alinea parcialmente (2)", 2), ("Alinea insuficientemente (1)", 1)],
    "ajustado": [("Ajustado (3)", 3), ("Parcialmente ajustado (2)", 2), ("Insuficientemente ajustado (1)", 1)],
}

# ---------- Ítems de evaluación (Cuerpo) con su escala asociada ----------
CUERPO_ITEMS = [
    ("Resumen del proyecto", "Integridad sintética del resumen", "Incluye de forma sucinta los elementos nucleares del proyecto.", "incluye"),
    ("Resumen del proyecto", "Presentación formal del resumen", "Conformidad con requisitos formales (≤300 palabras), redacción académica y estructura lógica.", "cumple"),
    ("Fundamentación", "Pertinencia del estudio", "La fundamentación evidencia la relevancia del problema en el campo y contexto definidos.", "evidencia_pertinencia"),
    ("Fundamentación", "Aporte esperado del estudio", "Explicita la contribución esperada (teórica/empírica/metodológica).", "define_aporte"),
    ("Fundamentación", "Viabilidad", "Sustenta la factibilidad en relación con recursos, alcances y limitaciones.", "sustenta_viabilidad"),
    ("Objetivo general", "Formulación técnica del objetivo", "Un único enunciado en infinitivo y claro que expresa el propósito central.", "formula_tecnicamente"),
    ("Objetivos específicos", "Especificidad de la formulación", "Cada objetivo en infinitivo delimita lo que se estudiará.", "especifica"),
    ("Objetivos específicos", "Medibilidad", "Permiten derivar indicadores y contrastarlos con datos observables.", "medible_operacional"),
    ("Objetivos específicos", "Temporalidad explícita", "Delimita plazo o hito temporal coherente con el estudio.", "temporalidad"),
    ("Marco teórico", "Pertinencia", "Selecciona y sintetiza literatura directamente vinculada al problema y objetivos.", "evidencia_pertinencia"),
    ("Marco teórico", "Articulación conceptual", "Define conceptos clave y explicita relaciones en una perspectiva coherente.", "articula_perspectiva"),
    ("Marco teórico", "Definición conceptual de constructos", "Presenta definiciones conceptuales claras de los constructos/variables relevantes.", "define_variables"),
    ("Estado del arte", "Pertinencia de los antecedentes", "Antecedentes directamente relevantes para problema, objetivos y contexto.", "integra_antecedentes"),
    ("Estado del arte", "Análisis crítico de los antecedentes", "Emite un juicio crítico sustentado sobre los antecedentes.", "analisis_critico"),
    ("Estado del arte", "Delimitación de la brecha de conocimiento", "Delimita con precisión la brecha específica en la literatura.", "delimita_brecha"),
    ("Metodología", "Pertinencia del diseño de investigación", "El diseño elegido es coherente con el problema y los objetivos.", "es_pertinente"),
    ("Metodología", "Definición de la población / unidad de análisis", "Delimita con precisión la población o unidad de análisis.", "delimita"),
    ("Metodología", "Especificación del muestreo", "Explicita la estrategia de muestreo a utilizar.", "especifica"),
    ("Metodología", "Pertinencia de los instrumentos de recolección", "Los instrumentos propuestos son congruentes con los objetivos del estudio.", "congruencia_instrumentos"),
    ("Metodología", "Descripción del procedimiento de recolección", "Describe de manera ordenada el procedimiento de recolección.", "describe"),
    ("Metodología", "Adecuación de las técnicas de análisis", "Las técnicas analíticas propuestas permiten responder a los objetivos.", "permiten"),
    ("Metodología", "Consideraciones éticas explicitadas", "Declara las consideraciones éticas pertinentes.", "explicita"),
    ("Metodología", "Limitaciones metodológicas reconocidas", "Reconoce limitaciones metodológicas relevantes.", "reconoce"),
    ("Bibliografía", "Calidad académica de las fuentes", "Mayoría de fuentes académicas (revisadas por pares/libros académicos).", "fuentes_calidad"),
    ("Bibliografía", "Actualidad de las fuentes", "Proporción pertinente de publicaciones recientes según el campo.", "actualidad"),
    ("Bibliografía", "Consistencia formal de citación", "Sigue de manera consistente un estilo de citación definido.", "norma"),
    ("Plan y cronograma", "Alineación actividades–objetivos", "Cada actividad está vinculada a un objetivo específico.", "alinea"),
    ("Plan y cronograma", "Ajuste temporal del cronograma", "El cronograma se ajusta al alcance del estudio.", "ajustado"),
]

st.title("🧮 Valorador / Rúbrica – Calculadora")

# ---------- SECCIÓN EQUIPO ----------
st.header("1) Equipo – hasta 6 investigadores")
cols = st.columns([2,2,2,1])
cols[0].markdown("**Nombre**")
cols[1].markdown("**Categoría**")
cols[2].markdown("**Puntos**")
cols[3].markdown("**—**")

equipo_total = 0
investigadores = []
for i in range(1, 7):
    c1, c2, c3, c4 = st.columns([2,2,2,1])
    nombre = c1.text_input(f"Nombre {i}", key=f"nom_{i}", value="")
    categoria = c2.selectbox(f"Categoría {i}", list(CATEGORIAS.keys()), key=f"cat_{i}")
    puntos = CATEGORIAS[categoria]
    c3.write(f"**{puntos}**")
    incluir = c4.checkbox("Incluir", value=True, key=f"incl_{i}")
    if incluir and nombre.strip():
        equipo_total += puntos
        investigadores.append({"Nombre": nombre.strip(), "Categoría": categoria, "Puntos": puntos})

st.info(f"**Puntaje Equipo (suma de categorías): {equipo_total}**")
st.caption("Nota: por pedido, el puntaje de **Equipo no se escala** ni se capea.")

# ---------- SECCIÓN CUERPO (Ítems completos del Evaluador) ----------
st.header("2) Cuerpo – Evaluación por ítems (escala 1–3)")

secciones = sorted({sec for sec,_,_,_ in [(a,b,c,d) for (a,b,c,d, *rest) in [(s,i,cr,ex,sk) for s,i,cr,ex,sk in CUERPO_ITEMS]]})
tab_secciones = st.tabs(secciones)
cuerpo_sum = 0
selecciones = []

sec_idx = {sec: idx for idx, sec in enumerate(secciones)}

for sec, item, criterio, explicacion, escala_key in CUERPO_ITEMS:
    with tab_secciones[sec_idx[sec]]:
        st.subheader(item)
        st.write(f"**Criterio:** {criterio}")
        st.caption(explicacion)
        labels = [lbl for (lbl, val) in SCALES[escala_key]]
        choice = st.selectbox("Seleccione una opción", labels, key=f"sel_{sec}_{item}")
        puntos = dict(SCALES[escala_key])[choice]
        cuerpo_sum += puntos
        selecciones.append({"Sección": sec, "Ítem": item, "Escala": choice, "Puntos": puntos})

cuerpo_total = min(cuerpo_sum, CUERPO_MAX)
st.info(f"**Puntaje Cuerpo (suma, capado a {CUERPO_MAX}): {cuerpo_total}**")

# ---------- Totales y condición ----------
total = equipo_total + cuerpo_total
aprobado = (equipo_total >= EQUIPO_MIN_REQ) and (cuerpo_total >= CUERPO_MIN_REQ) and (total >= GLOBAL_MIN_REQ)

st.header("3) Totales y condición")
colt = st.columns(4)
colt[0].metric("Equipo", equipo_total)
colt[1].metric("Cuerpo", f"{cuerpo_total} / {CUERPO_MAX}")
colt[2].metric("Total", total)
colt[3].metric("Condición", "APROBADO" if aprobado else "NO APROBADO")

# ---------- Exportar a Excel ----------
st.subheader("Exportar informe")
proyecto = st.text_input("Nombre del proyecto / postulante", value="Proyecto sin nombre")
obs = st.text_area("Observaciones", value="")

df_equipo = pd.DataFrame(investigadores) if investigadores else pd.DataFrame(columns=["Nombre","Categoría","Puntos"])
df_items = pd.DataFrame(selecciones)
df_resumen = pd.DataFrame([{
    "Proyecto/Postulante": proyecto,
    "Equipo (suma categorías)": equipo_total,
    "Cuerpo (capado)": cuerpo_total,
    "Máximo Cuerpo": CUERPO_MAX,
    "Total": total,
    "Aprobación": "APROBADO" if aprobado else "NO APROBADO",
    f"Condición Equipo (mín {EQUIPO_MIN_REQ})": "OK" if equipo_total >= EQUIPO_MIN_REQ else "NO",
    f"Condición Cuerpo (mín {CUERPO_MIN_REQ})": "OK" if cuerpo_total >= CUERPO_MIN_REQ else "NO",
    "Mínimo Global requerido": GLOBAL_MIN_REQ,
    "Observaciones": obs
}])

def export_xlsx(resumen, equipo, items):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        resumen.to_excel(writer, index=False, sheet_name="Resumen")
        equipo.to_excel(writer, index=False, sheet_name="Equipo")
        items.to_excel(writer, index=False, sheet_name="Cuerpo_items")
        for sheet in ["Resumen","Equipo","Cuerpo_items"]:
            ws = writer.sheets[sheet]
            df = resumen if sheet=="Resumen" else (equipo if sheet=="Equipo" else items)
            for idx, col in enumerate(df.columns):
                width = max(12, int(max([len(str(x)) for x in df[col]]+[len(col)]))+2)
                ws.set_column(idx, idx, width)
    buf.seek(0)
    return buf.getvalue()

xlsx_bytes = export_xlsx(df_resumen, df_equipo, df_items)
st.download_button("⬇️ Descargar Excel (resumen + equipo + cuerpo)", data=xlsx_bytes, file_name="valoracion_proyecto.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.caption("Hecho con ❤️ en Streamlit. Reglas: Equipo ≥ mín, Cuerpo ≥ mín, Total ≥ mín. Equipo no se escala.")
