import streamlit as st
import pandas as pd
import yaml
from typing import Any, Dict, List, Tuple

st.set_page_config(page_title="Valorador de Proyectos", layout="wide")

# ---------- Utilidades ----------

CATEGORIAS_EQUIPO: Dict[str, int] = {
    "Investigador/a Superior I": 10,
    "Investigador/a Principal II": 9,
    "Investigador/a Independiente III": 8,
    "Investigador/a Adjunto/a IV": 5,
    "Investigador/a Asistente V": 4,
    "Becario/a de Iniciación VI": 2,
    "Sin categorización / Externo": 1,
}

def normaliza_item(x: Any) -> Tuple[str, str, Any, Any]:
    """
    Acepta dicts o listas/tuplas y devuelve (seccion, item, criterio, escala).
    - Dict: tolera claves alternativas.
    - Lista/tupla: completa con None y recorta a 4.
    """
    if isinstance(x, dict):
        seccion = x.get("seccion") or x.get("section") or x.get("s")
        item    = x.get("item")    or x.get("nombre")  or x.get("i")
        criterio= x.get("criterio")or x.get("clave")   or x.get("c")
        escala  = x.get("escala")  or x.get("opciones")or x.get("e")
        return (seccion, item, criterio, escala)
    elif isinstance(x, (list, tuple)):
        l = list(x) + [None, None, None, None]
        return tuple(l[:4])
    else:
        return (None, None, None, None)

def cargar_items_desde_yaml(path: str = "rubric_config.yaml") -> List[Tuple[str, str, Any, Any]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        raw_items: List[Any] = cfg.get("items", [])
        items_norm = [normaliza_item(x) for x in raw_items]
        # Validación básica
        malos = [i for i, (s, it, _, _) in enumerate(items_norm) if not s or not it]
        if malos:
            st.error(
                "Hay ítems mal formateados en `rubric_config.yaml` "
                f"(faltan `seccion` o `item`) en posiciones: {', '.join(map(str, malos))}. "
                "Revisá tu YAML o usá la plantilla incluida."
            )
            st.stop()
        return items_norm
    except FileNotFoundError:
        st.warning("No se encontró `rubric_config.yaml`. Se cargará una lista mínima de ejemplo.")
        return [
            ("Metodología", "Diseño del estudio", "disenio", [["Insuficiente",1], ["Adecuado",2], ["Excelente",3]]),
            ("Resultados", "Calidad de datos", "calidad_datos", [["Insuficiente",1], ["Adecuado",2], ["Excelente",3]]),
        ]

def escala_a_dict(escala: Any) -> Dict[str, int]:
    """
    Convierte la escala de [[etiqueta, valor], ...] a dict {etiqueta: valor}.
    Si ya viene como dict, la devuelve.
    """
    if isinstance(escala, dict):
        return {str(k): int(v) for k, v in escala.items()}
    if isinstance(escala, list):
        out = {}
        for par in escala:
            if isinstance(par, (list, tuple)) and len(par) >= 2:
                out[str(par[0])] = int(par[1])
        return out
    return {"Insuficiente": 1, "Adecuado": 2, "Excelente": 3}

def sumar_equipo(puntajes: List[int], minimo_req: int, maximo: int, capear: bool) -> Tuple[int, bool, int]:
    total = sum(puntajes)
    total_capeado = min(total, maximo) if capear else total
    cumple_min = total_capeado >= minimo_req
    return total_capeado, cumple_min, total

# ---------- Sidebar: configuración ----------

st.sidebar.header("Configuración")

cuerpo_max = st.sidebar.number_input("Cuerpo – Puntaje máximo", value=75, step=1)
cuerpo_min = st.sidebar.number_input("Cuerpo – Mínimo requerido", value=45, step=1)
equipo_min = st.sidebar.number_input("Equipo – Mínimo requerido", value=10, step=1)
equipo_max = st.sidebar.number_input("Equipo – Máximo (cap)", value=25, step=1)
global_min = st.sidebar.number_input("Mínimo global requerido", value=60, step=1)
cap_equipo = st.sidebar.checkbox("Capear Equipo al máximo", value=False,
                                 help="Si está activo, si Equipo supera el máximo configurado, se recorta al máximo.")

st.sidebar.markdown("---")
st.sidebar.caption("Tip: podés ajustar estos valores según tu reglamento.")

st.title("Valorador / Rúbrica – Calculadora (Streamlit)")

# ---------- 1) Equipo ----------

st.subheader("1) Equipo – Puntaje por categorías")

cols = st.columns(3)
nombres = []
categorias = []
incluir = []
for i in range(1, 7):
    with cols[(i-1) % 3]:
        st.markdown(f"**Nombre {i}**")
        nombre = st.text_input(f"Nombre {i}", key=f"nombre_{i}", label_visibility="collapsed")
        cat = st.selectbox(
            f"Categoría {i}",
            options=list(CATEGORIAS_EQUIPO.keys()),
            key=f"cat_{i}",
            label_visibility="collapsed",
        )
        chk = st.checkbox("Incluir", value=True, key=f"incluir_{i}")
    nombres.append(nombre)
    categorias.append(cat)
    incluir.append(chk)

puntajes_equipo = []
for cat, inc in zip(categorias, incluir):
    if inc and cat in CATEGORIAS_EQUIPO:
        puntajes_equipo.append(CATEGORIAS_EQUIPO[cat])
    else:
        puntajes_equipo.append(0)

equipo_total, equipo_cumple_min, equipo_raw = sumar_equipo(
    puntajes_equipo, minimo_req=equipo_min, maximo=equipo_max, capear=cap_equipo
)

st.info(
    f"Puntaje Equipo (suma de categorías): **{equipo_total}** "
    + (f"(raw: {equipo_raw}, cap {equipo_max})" if cap_equipo else "")
)

# ---------- 2) Cuerpo ----------

st.subheader("2) Cuerpo – Evaluación por ítems (escala 1–3)")

items = cargar_items_desde_yaml()
secciones = sorted({s for (s, _, _, _) in items})

cuerpo_valores: Dict[str, int] = {}
cuerpo_detalle: List[Dict[str, Any]] = []

for seccion in secciones:
    st.markdown(f"### {seccion}")
    subset = [(s, it, cr, es) for (s, it, cr, es) in items if s == seccion]
    for (_, item, criterio, escala) in subset:
        esc_dict = escala_a_dict(escala)
        etiquetas = list(esc_dict.keys())
        # Estado persistente por criterio
        state_key = f"cuerpo_{seccion}_{criterio}"
        etiqueta_seleccionada = st.radio(
            f"{item}",
            options=etiquetas,
            key=state_key,
            horizontal=True,
        )
        valor = esc_dict.get(etiqueta_seleccionada, 0)
        cuerpo_valores[criterio] = valor
        cuerpo_detalle.append({
            "seccion": seccion,
            "item": item,
            "criterio": criterio,
            "etiqueta": etiqueta_seleccionada,
            "valor": valor
        })

cuerpo_total = int(sum(cuerpo_valores.values()))
st.success(f"Puntaje Cuerpo: **{cuerpo_total}** / máx. configurado {cuerpo_max}")

# ---------- 3) Totales y Reglas de Aprobación ----------

total_global = equipo_total + cuerpo_total

cond_cuerpo = cuerpo_total >= cuerpo_min
cond_equipo = equipo_total >= equipo_min
cond_global = total_global >= global_min

aprobado = cond_cuerpo and cond_equipo and cond_global

st.markdown("---")
st.subheader("3) Totales")
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Equipo", equipo_total)
with c2:
    st.metric("Cuerpo", cuerpo_total)
with c3:
    st.metric("Total", total_global)

st.markdown(
    f"**Condiciones:** "
    f"Cuerpo ≥ {cuerpo_min} → {'✅' if cond_cuerpo else '❌'} &nbsp; | &nbsp; "
    f"Equipo ≥ {equipo_min} → {'✅' if cond_equipo else '❌'} &nbsp; | &nbsp; "
    f"Global ≥ {global_min} → {'✅' if cond_global else '❌'}"
)

st.markdown(
    f"### Resultado: {'🟢 APROBADO' if aprobado else '🔴 NO APROBADO'}"
)

# ---------- 4) Exportación (opcional ligera) ----------

def exportar_excel():
    df_equipo = pd.DataFrame({
        "Nombre": nombres,
        "Categoría": categorias,
        "Incluir": incluir,
        "Puntos": puntajes_equipo
    })
    df_cuerpo = pd.DataFrame(cuerpo_detalle)

    with pd.ExcelWriter("valoracion.xlsx", engine="xlsxwriter") as writer:
        df_equipo.to_excel(writer, index=False, sheet_name="Equipo")
        df_cuerpo.to_excel(writer, index=False, sheet_name="Cuerpo")
        meta = pd.DataFrame([
            {"Cuerpo_min": cuerpo_min, "Cuerpo_max": cuerpo_max,
             "Equipo_min": equipo_min, "Equipo_max": equipo_max,
             "Global_min": global_min,
             "Cap_equipo": cap_equipo,
             "Equipo_total": equipo_total,
             "Cuerpo_total": cuerpo_total,
             "Total_global": total_global,
             "Resultado": "APROBADO" if aprobado else "NO APROBADO"}
        ])
        meta.to_excel(writer, index=False, sheet_name="Totales")

    with open("valoracion.xlsx", "rb") as f:
        st.download_button(
            "⬇️ Descargar Excel de valoración",
            data=f,
            file_name="valoracion.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

st.markdown("---")
exportar_excel()
st.caption("Nota: podés desactivar el cap de Equipo en la barra lateral si tu reglamento no lo permite.")
