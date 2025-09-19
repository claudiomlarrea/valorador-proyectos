# Valorador / Rúbrica – Calculadora (Streamlit)

Aplicación **Streamlit** lista para usar y desplegar en **Streamlit Community Cloud** o **GitHub + Streamlit**.

## 🔧 Qué hace
- Calcula puntajes de **Equipo** (con categorías auto‑puntaje + componentes adicionales) y **Cuerpo** (puntaje global o desglose por ítems).
- Aplica la regla de aprobación acordada: **APROBADO** solo si `Equipo ≥ 10`, `Cuerpo ≥ 45` y `Total ≥ 60` (todo configurable).
- Exporta un **resumen en Excel**.
- Permite **subir tu plantilla Excel** (opcional) para adjuntarla al informe descargable.

## ▶️ Ejecutar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

## ☁️ Desplegar en Streamlit Community Cloud
1. Sube estos archivos a un repositorio en GitHub.
2. Ve a https://streamlit.io/cloud y conecta tu repo.
3. Establece `app.py` como **main file**.
4. (Opcional) Agrega `runtime.txt` si usas Python 3.10+.

## ⚙️ Configuración rápida
En la barra lateral puedes ajustar:
- **Máximos/Mínimos** de Cuerpo y Equipo.
- **Mínimo global requerido** (Total).
- **Mapa de categorías de Equipo → puntaje automático**.

## 🧩 Estructura
```
.
├── app.py
├── requirements.txt
├── runtime.txt
└── README.md
```

> Si tienes una rúbrica compleja en Excel con fórmulas y macros, esta app ofrece una vía **simplificada** pero flexible. Podemos integrarla con tu estructura exacta más adelante si compartes un ejemplo definitivo.
