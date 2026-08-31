"""Predicción de LubriInsight.
Clasificación binaria de recurrencia y churn sobre la nueva BD Lubricadora_db.
Diseño visual dinámico (tema oscuro dorado/azul).
"""
from __future__ import annotations

import io
import traceback
import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             f1_score, log_loss, precision_score, recall_score,
                             roc_auc_score, roc_curve)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from utils.database import query_df
from utils.footer import show_footer

# ─── Configuración de página ────────────────────────────────────────────────
st.set_page_config(page_title="LubriInsight | Predicción", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

# ─── Paleta oscura dorado/azul acero (misma identidad del resto de la app) ──
BG = "#0A0B0F"
PANEL = "rgba(255,255,255,0.035)"
PANEL_SOLID = "#12141B"
BORDER = "rgba(255,255,255,0.08)"
GOLD = "#E3A73E"
GOLD_LIGHT = "#F5CF7A"
STEEL = "#4F8FC4"
STEEL_LIGHT = "#9CC9EC"
TEXT = "#EDEFF2"
MUTED = "#98A4B2"
GREEN = "#2ED18C"
RED = "#E5615B"
COLORS = {"navy": TEXT, "blue": STEEL_LIGHT, "gold": GOLD_LIGHT, "green": GREEN, "red": RED, "bg": BG, "muted": MUTED}

st.markdown(f"""<style>
[data-testid="stSidebar"] *{{color:{TEXT} !important}}
[data-testid="stSidebarNav"] a{{border-radius:10px;margin:2px 8px;padding:10px 12px !important;
    transition:background .15s ease}}
[data-testid="stSidebarNav"] span{{font-family:'Playfair Display',serif;font-weight:600;
    font-size:.95rem;letter-spacing:.01em;white-space:normal !important}}
[data-testid="stSidebarNav"] a:hover{{background:rgba(227,167,62,.14) !important}}
[data-testid="stSidebarNav"] a[aria-current="page"]{{
    background:linear-gradient(135deg,rgba(227,167,62,.22),rgba(79,143,196,.14)) !important;
    border-left:3px solid {GOLD_LIGHT}}}
.stApp{{background:radial-gradient(circle at 15% -10%,rgba(217,169,76,.10),transparent 45%),
        radial-gradient(circle at 90% 10%,rgba(143,180,217,.08),transparent 40%),{BG}}}
[data-testid="stHeader"]{{background:{BG} !important}}
[data-testid="stDecoration"]{{display:none !important}}
[data-testid="stSidebar"][aria-expanded="true"]{{min-width:270px !important;max-width:270px !important}}
[data-testid="stSidebar"]{{background:#07080B;border-right:1px solid {BORDER}}}
[data-testid="stSidebar"] *{{color:{TEXT} !important}}

/* Oculta el menú/botón "Deploy" nativo de Streamlit — no forma parte del diseño */
[data-testid="stToolbar"]{{display:none !important}}
#MainMenu{{visibility:hidden !important}}
footer{{visibility:hidden !important}}

.block-container{{max-width:1400px;padding:2rem 4rem 4rem}}
h1,h2,h3,h4{{color:{TEXT};letter-spacing:-.03em;font-family:'Playfair Display',serif}}
p, span, div, label{{color:{TEXT}}}

@keyframes fadeSlideUp{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes softPulse{{0%,100%{{opacity:.5}}50%{{opacity:1}}}}
@keyframes heroSheen{{0%{{left:-60%}}50%{{left:120%}}100%{{left:120%}}}}

.hero{{position:relative;background:linear-gradient(160deg,#12141B 0%,#0A0B0F 70%);border:1px solid rgba(217,169,76,.25);
    border-radius:22px;padding:34px 38px;margin-bottom:28px;box-shadow:0 18px 46px rgba(0,0,0,.55);
    animation:fadeSlideUp .55s ease-out;overflow:hidden}}
.hero::after{{content:'';position:absolute;top:0;left:-60%;width:40%;height:100%;
    background:linear-gradient(100deg,transparent,rgba(245,207,122,.06),transparent);
    animation:heroSheen 5s ease-in-out infinite}}
.hero h1{{margin:0 0 10px;font-size:clamp(2rem,4vw,3.7rem);display:flex;align-items:center;gap:14px;
    background:linear-gradient(90deg,{GOLD_LIGHT},{STEEL_LIGHT});
    -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}}
.hero .hero-icon{{-webkit-text-fill-color:initial;display:inline-block;animation:softPulse 2.4s ease-in-out infinite}}
.hero p{{color:{MUTED};max-width:68ch;font-size:1.05rem;margin:0;line-height:1.55}}
.eyebrow{{text-transform:uppercase;letter-spacing:.12em;font-weight:800;font-size:.73rem;color:{GOLD};margin-bottom:12px;
    display:flex;align-items:center;gap:8px}}
.eyebrow .dot{{width:7px;height:7px;border-radius:50%;background:{GOLD_LIGHT};box-shadow:0 0 8px {GOLD_LIGHT};
    animation:softPulse 1.8s ease-in-out infinite}}

[data-testid="stMetric"]{{background:{PANEL};border:1px solid {BORDER};border-radius:16px;padding:18px;
    box-shadow:0 8px 22px rgba(0,0,0,.35);backdrop-filter:blur(6px)}}
[data-testid="stMetricValue"]{{color:{GOLD_LIGHT};font-variant-numeric:tabular-nums}}
[data-testid="stMetricLabel"]{{color:{STEEL_LIGHT} !important}}

.section{{margin:34px 0 16px}}.section h2{{margin-bottom:4px}}.muted{{color:{MUTED}}}

.var-card{{background:{PANEL};border:1px solid {BORDER};border-radius:14px;padding:18px 20px;margin-bottom:10px;
    box-shadow:0 6px 18px rgba(0,0,0,.3);animation:fadeSlideUp .5s ease-out;
    transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease}}
.var-card:hover{{transform:translateY(-3px);box-shadow:0 12px 26px rgba(0,0,0,.45);border-color:rgba(227,167,62,.35)}}
.var-card .var-icon{{font-size:1.3rem;margin-right:8px}}
.var-card .var-name{{font-weight:700;color:{GOLD_LIGHT};font-size:.95rem}}
.var-card .var-desc{{color:{MUTED};font-size:.82rem;margin-top:4px}}

.objetivo-box{{position:relative;background:linear-gradient(135deg,#12141B 0%,#0A0B0F 100%);border:1px solid rgba(227,167,62,.3);
    border-radius:16px;padding:22px 26px;margin:18px 0 24px;box-shadow:0 10px 28px rgba(0,0,0,.4);
    animation:fadeSlideUp .55s ease-out;overflow:hidden}}
.objetivo-box::after{{content:'';position:absolute;top:0;left:-60%;width:35%;height:100%;
    background:linear-gradient(100deg,transparent,rgba(245,207,122,.05),transparent);animation:heroSheen 6s ease-in-out infinite}}
.objetivo-box h4{{color:{GOLD_LIGHT};margin:0 0 6px;font-size:.85rem;text-transform:uppercase;letter-spacing:.1em}}
.objetivo-box p{{color:{TEXT};margin:0;font-size:.95rem;line-height:1.5}}
.objetivo-box code{{background:rgba(227,167,62,.18);color:{GOLD_LIGHT};padding:2px 8px;border-radius:6px}}

/* Pestañas con la misma tipografía de los títulos (Playfair Display) */
[data-baseweb="tab-list"]{{border-bottom:1px solid {BORDER};gap:6px}}
[data-baseweb="tab"]{{color:{MUTED};font-weight:600;transition:color .2s ease}}
[data-baseweb="tab"] p{{font-family:'Playfair Display',serif;font-weight:600;font-size:1.02rem;letter-spacing:.01em}}
[data-baseweb="tab"]:hover{{color:{GOLD_LIGHT} !important}}
[aria-selected="true"][data-baseweb="tab"]{{color:{GOLD_LIGHT} !important}}
[data-baseweb="tab-highlight"]{{background-color:{GOLD_LIGHT} !important;box-shadow:0 0 8px {GOLD_LIGHT}}}

/* Textos secundarios (captions) con mejor contraste para lectura */
[data-testid="stCaptionContainer"] p, [data-testid="stCaptionContainer"]{{color:#ABB7C6 !important;font-size:.86rem !important;line-height:1.5}}

[data-testid="stAlert"]{{background:{PANEL};border:1px solid {BORDER};border-radius:12px;color:{TEXT};animation:fadeSlideUp .5s ease-out}}
[data-testid="stDataFrame"]{{border:1px solid {BORDER};border-radius:12px;overflow:hidden;animation:fadeSlideUp .5s ease-out}}
[data-testid="stExpander"]{{background:{PANEL};border:1px solid {BORDER};border-radius:12px}}
[data-testid="stExpander"] summary{{color:{STEEL_LIGHT} !important;font-weight:600}}
[data-testid="stForm"]{{background:{PANEL};border:1px solid {BORDER};border-radius:14px;padding:6px}}
[data-testid="stJson"]{{background:{PANEL_SOLID} !important;border:1px solid {BORDER};border-radius:10px}}
[data-testid="stCodeBlock"]{{background:transparent !important}}
[data-testid="stCodeBlock"] pre{{background:{PANEL_SOLID} !important;border:1px solid {BORDER} !important;border-radius:10px !important}}
[data-testid="stCodeBlock"] code{{color:{TEXT} !important;background:transparent !important}}

button[kind="primary"], [data-testid="stFormSubmitButton"] button, [data-testid="baseButton-primary"]{{
    background:linear-gradient(135deg,{GOLD},{GOLD_LIGHT}) !important;color:#0A0B0F !important;
    font-weight:700 !important;border:none !important;border-radius:10px !important;
    transition:transform .2s ease,box-shadow .2s ease}}
button[kind="primary"]:hover, [data-testid="stFormSubmitButton"] button:hover{{transform:translateY(-2px);box-shadow:0 10px 22px rgba(227,167,62,.35)}}
[data-testid="stDownloadButton"] button{{background:{PANEL} !important;color:{STEEL_LIGHT} !important;
    border:1px solid {BORDER} !important;border-radius:10px !important}}

[data-testid="stNumberInput"] input, [data-testid="stTextInput"] input{{
    background:{PANEL_SOLID} !important;color:{TEXT} !important;border:1px solid {BORDER} !important}}
[data-testid="stSelectbox"]{{background:{PANEL} !important;border:1px solid {BORDER} !important;border-radius:8px}}
[data-testid="stSelectbox"] div{{background:transparent !important}}
[data-testid="stSelectbox"] *{{color:{TEXT} !important}}
[data-baseweb="popover"],[data-baseweb="menu"]{{background:{PANEL_SOLID} !important}}
[data-baseweb="popover"] *,[data-baseweb="menu"] *{{color:{TEXT} !important}}
li[role="option"]{{background:{PANEL_SOLID} !important;color:{TEXT} !important}}
li[role="option"]:hover{{background:rgba(255,255,255,.08) !important}}

[data-testid="stRadio"] label{{color:{TEXT} !important}}
[data-testid="stProgress"] > div > div{{background:linear-gradient(90deg,{GOLD},{STEEL}) !important}}

[data-testid="stVerticalBlockBorderWrapper"]{{transition:transform .25s ease,box-shadow .25s ease}}
[data-testid="stVerticalBlockBorderWrapper"]:hover{{transform:translateY(-2px)}}

@media(max-width:800px){{.block-container{{padding:1.2rem}}}}
</style>""", unsafe_allow_html=True)

PLOTLY_LAYOUT = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=TEXT,
    title_font=dict(size=17, color=GOLD_LIGHT, family='Playfair Display'),
    xaxis=dict(gridcolor='rgba(255,255,255,.10)'), yaxis=dict(gridcolor='rgba(255,255,255,.10)'),
    legend=dict(font=dict(color=TEXT)), hoverlabel=dict(bgcolor=PANEL_SOLID, font_color=TEXT, bordercolor=BORDER))

# ─── Banner hero ─────────────────────────────────────────────────────────────
st.markdown(
    '<div class="hero"><div class="eyebrow"><span class="dot"></span>LAVADORA S.A. · INTELIGENCIA COMERCIAL</div>'
    '<h1><span class="hero-icon">🤖</span>Predicción</h1>'
    '<p>Clasificación binaria para anticipar recurrencia y riesgo de abandono de clientes.</p></div>',
    unsafe_allow_html=True)

# ─── Constantes del modelo ───────────────────────────────────────────────────
# Diseño temporal (out-of-time, sin fuga de datos): se observa el historial de
# compras HASTA la fecha de corte, y se etiqueta según lo que ocurre DESPUÉS,
# en una ventana futura. El modelo nunca ve el futuro durante el entrenamiento.
CORTE = pd.Timestamp("2023-12-31")
DIAS_RECURRENCIA = 120  # ventana de "regreso" (~4 meses, ciclo típico de mantenimiento)
DIAS_CHURN = 120        # ventana de "abandono" (~4 meses sin comprar)
RANDOM_STATE = 42
CONSUMIDOR_FINAL = "9999999999999"
CV_FOLDS = 5

# Meta de desempeño del proyecto: accuracy mínima 75%, ideal 80% o más,
# medida sobre el 20% de prueba (holdout) que el modelo nunca vio durante
# el entrenamiento ni la selección de modelo.
ACCURACY_MINIMA = 0.75
ACCURACY_IDEAL = 0.80
UMBRAL_DECISION = 0.50  # umbral estándar; ver nota metodológica más abajo
NOMBRE_MODELO_DISPLAY = "Clasificación Binaria"  # etiqueta mostrada en la interfaz

NUMERIC_FEATURES = [
    "recencia", "frecuencia", "monto_total", "ticket_promedio", "antiguedad_dias",
    "productos_unicos", "categorias_unicas", "dias_promedio_entre_compras",
]
CATEGORICAL_FEATURES = ["id_tipo_documento", "genero", "localidad"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
# Recurrencia se enfoca en comportamiento real de compra; evita variables demográficas
# que agregan ruido en datasets pequeños. Churn conserva todas las variables.
RECURRENCIA_FEATURES = [
    "recencia", "frecuencia", "monto_total", "ticket_promedio",
    "antiguedad_dias", "productos_unicos", "categorias_unicas",
    "dias_promedio_entre_compras",
]

# ─── Iconos y descripciones para cada variable ───────────────────────────────
FEATURE_META = {
    "recencia": ("📅", "Recencia", "Días desde la última compra hasta el corte"),
    "frecuencia": ("🔁", "Frecuencia", "Número de transacciones únicas realizadas"),
    "monto_total": ("💰", "Monto Total", "Suma total facturada por el cliente"),
    "ticket_promedio": ("🏷️", "Ticket Promedio", "Promedio de gasto por transacción"),
    "antiguedad_dias": ("⏳", "Antigüedad (días)", "Días desde la primera compra hasta el corte"),
    "productos_unicos": ("📦", "Productos Únicos", "Cantidad de productos distintos comprados"),
    "categorias_unicas": ("🏷️", "Categorías Únicas", "Cantidad de categorías distintas exploradas"),
    "dias_promedio_entre_compras": ("⏱️", "Días Prom. entre Compras", "Promedio de días entre cada transacción"),
    "id_tipo_documento": ("🆔", "Tipo de Documento", "Tipo de identificación del cliente"),
    "genero": ("👤", "Género", "Masculino o Femenino"),
    "localidad": ("📍", "Localidad", "Ubicación geográfica del cliente"),
}

# ─── Mapeo de género legible ─────────────────────────────────────────────────
GENERO_MAP = {"1": "Masculino", "2": "Femenino", "1.0": "Masculino", "2.0": "Femenino"}


def mapear_genero(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte valores numéricos de género a etiquetas legibles."""
    df["genero"] = df["genero"].astype(str).str.strip().map(lambda x: GENERO_MAP.get(x, x))
    return df


def cargar_fuentes() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ventas = query_df("""
        SELECT id_venta, cedula_cliente, fecha_venta::date AS fecha_venta, total
        FROM venta
        WHERE fecha_venta IS NOT NULL AND total IS NOT NULL
          AND cedula_cliente <> :consumidor
    """, {"consumidor": CONSUMIDOR_FINAL})
    detalle = query_df("""
        SELECT dv.id_venta, dv.id_producto, dv.cantidad, p.id_categoria
        FROM detalle_venta dv JOIN producto p ON p.id_producto = dv.id_producto
    """)
    clientes = query_df("""
        SELECT cedula, id_tipo_documento, genero, localidad
        FROM cliente WHERE cedula <> :consumidor
    """, {"consumidor": CONSUMIDOR_FINAL})
    ventas["fecha_venta"] = pd.to_datetime(ventas["fecha_venta"], errors="coerce")
    ventas["total"] = pd.to_numeric(ventas["total"], errors="coerce")
    ventas = ventas.dropna(subset=["fecha_venta", "total", "cedula_cliente"])
    if not detalle.empty:
        detalle["cantidad"] = pd.to_numeric(detalle["cantidad"], errors="coerce")
    clientes = mapear_genero(clientes)
    return ventas, detalle, clientes


def _promedio_dias(grupo: pd.DataFrame) -> float:
    fechas = grupo["fecha_venta"].drop_duplicates().sort_values()
    return float(fechas.diff().dt.days.dropna().mean()) if len(fechas) > 1 else 0.0


def construir_dataset(ventas, detalle, clientes, objetivo: str) -> pd.DataFrame:
    historico = ventas[ventas["fecha_venta"] <= CORTE].copy()
    dias = DIAS_RECURRENCIA if objetivo == "recurrencia" else DIAS_CHURN
    futuro = ventas[(ventas["fecha_venta"] > CORTE) & (ventas["fecha_venta"] <= CORTE + pd.Timedelta(days=dias))]
    base = historico.groupby("cedula_cliente").agg(
        primera_compra=("fecha_venta", "min"), ultima_compra=("fecha_venta", "max"),
        frecuencia=("id_venta", "nunique"), monto_total=("total", "sum"), ticket_promedio=("total", "mean"),
    ).reset_index()
    base["recencia"] = (CORTE - base["ultima_compra"]).dt.days.clip(lower=0)
    base["antiguedad_dias"] = (CORTE - base["primera_compra"]).dt.days.clip(lower=0)
    gaps = historico.groupby("cedula_cliente").apply(_promedio_dias, include_groups=False).rename("dias_promedio_entre_compras")
    base = base.merge(gaps, on="cedula_cliente", how="left")
    d = detalle[detalle["id_venta"].isin(historico["id_venta"])]
    if not d.empty:
        d = d.merge(historico[["id_venta", "cedula_cliente"]], on="id_venta", how="inner")
        base = base.merge(d.groupby("cedula_cliente").agg(productos_unicos=("id_producto", "nunique"), categorias_unicas=("id_categoria", "nunique")).reset_index(), on="cedula_cliente", how="left")
    else:
        base["productos_unicos"], base["categorias_unicas"] = 0, 0
    base = base.merge(clientes, left_on="cedula_cliente", right_on="cedula", how="left").drop(columns="cedula", errors="ignore")
    compro = base["cedula_cliente"].astype(str).isin(set(futuro["cedula_cliente"].astype(str))).astype(int)
    base["target"] = compro if objetivo == "recurrencia" else 1 - compro
    for col in NUMERIC_FEATURES:
        base[col] = pd.to_numeric(base[col], errors="coerce").fillna(0)
    for col in CATEGORICAL_FEATURES:
        base[col] = base[col].fillna("SIN ESPECIFICAR").astype(str)
    return base[["cedula_cliente", *FEATURES, "target"]]


def crear_pipeline(clasificador=None, features=None) -> Pipeline:
    features = features or FEATURES
    numeric = [f for f in features if f in NUMERIC_FEATURES]
    categorical = [f for f in features if f in CATEGORICAL_FEATURES]
    transformers = [("numericas", Pipeline([("imputacion", SimpleImputer(strategy="median")), ("escalado", StandardScaler())]), numeric)]
    if categorical:
        transformers.append(("categoricas", Pipeline([("imputacion", SimpleImputer(strategy="most_frequent")), ("codificacion", OneHotEncoder(handle_unknown="ignore"))]), categorical))
    pre = ColumnTransformer(transformers)
    if clasificador is None:
        clasificador = LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE)
    return Pipeline([("preprocesamiento", pre), ("clasificador", clasificador)])


def entrenar(df: pd.DataFrame, objetivo: str) -> dict:
    """Entrena y selecciona el mejor modelo de clasificación binaria.

    Metodología:
    1. División real 80% entrenamiento / 20% prueba (holdout único, estratificado,
       usado UNA sola vez al final — nunca participa en la selección de modelo).
    2. Se comparan 3 algoritmos (Regresión Logística, Random Forest, Gradient
       Boosting) mediante validación cruzada estratificada de 5 particiones
       DENTRO del 80% de entrenamiento, con Accuracy como métrica de selección
       (que es la métrica objetivo del proyecto: mínimo 75%, ideal 80%+).
    3. Se usan hiperparámetros fijos y regularizados (no se hace una búsqueda
       agresiva de hiperparámetros): con ~270 clientes, una búsqueda exhaustiva
       tiende a sobreajustarse al ruido de las particiones de validación y en la
       práctica empeora el resultado en el TEST real. Hiperparámetros simples y
       estables generalizan mejor en datasets pequeños.
    4. El modelo con mayor Accuracy promedio en validación cruzada se reentrena
       con el 80% completo y se evalúa una única vez sobre el 20% de prueba
       (nunca antes visto), con umbral de decisión estándar (0.5).
    """
    features = RECURRENCIA_FEATURES if objetivo == "recurrencia" else FEATURES
    if df["target"].nunique() < 2 or df["target"].value_counts().min() < 10:
        raise ValueError("No hay suficientes observaciones en ambas clases; se requieren al menos 10 por clase.")

    X_train, X_test, y_train, y_test = train_test_split(
        df[features], df["target"].astype(int), test_size=0.20,
        stratify=df["target"], random_state=RANDOM_STATE
    )

    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)

    candidatos = {
        "Regresión Logística": LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE),
        "Random Forest": RandomForestClassifier(
            n_estimators=400, min_samples_leaf=2, class_weight="balanced_subsample",
            random_state=RANDOM_STATE, n_jobs=-1,
        ),
        "Gradient Boosting": GradientBoostingClassifier(random_state=RANDOM_STATE),
    }

    comparacion = []
    pipelines_ajustados = {}
    for nombre, clasificador in candidatos.items():
        pipe = crear_pipeline(clasificador, features=features)
        cv_scores = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="accuracy")
        pipe.fit(X_train, y_train)
        pipelines_ajustados[nombre] = pipe
        comparacion.append({
            "modelo": nombre,
            "cv_accuracy_mean": float(cv_scores.mean()),
            "cv_accuracy_std": float(cv_scores.std()),
        })

    comparacion.sort(key=lambda c: c["cv_accuracy_mean"], reverse=True)
    mejor = comparacion[0]
    modelo_nombre = mejor["modelo"]
    modelo = pipelines_ajustados[modelo_nombre]

    proba_test = modelo.predict_proba(X_test)[:, 1]
    pred_test = (proba_test >= UMBRAL_DECISION).astype(int)
    metrics = {
        "accuracy": accuracy_score(y_test, pred_test),
        "precision": precision_score(y_test, pred_test, zero_division=0),
        "recall": recall_score(y_test, pred_test, zero_division=0),
        "f1": f1_score(y_test, pred_test, zero_division=0),
        "roc_auc": roc_auc_score(y_test, proba_test),
        "log_loss": log_loss(y_test, proba_test, labels=[0, 1]),
    }
    return {
        "modelo": modelo, "X_test": X_test, "y_test": y_test,
        "y_pred": pred_test, "y_proba": proba_test,
        "umbral": UMBRAL_DECISION, "modelo_nombre": modelo_nombre,
        "features": features,
        "comparacion_modelos": pd.DataFrame(comparacion),
        "cv_accuracy": mejor["cv_accuracy_mean"],
        "cv_accuracy_std": mejor["cv_accuracy_std"],
        "accuracy_objetivo_cumplido": bool(metrics["accuracy"] >= ACCURACY_MINIMA),
        "accuracy_ideal_alcanzado": bool(metrics["accuracy"] >= ACCURACY_IDEAL),
        "metrics": metrics,
    }


def mostrar_variables(df: pd.DataFrame, objetivo: str) -> None:
    st.subheader("📊 Variables del Modelo")
    st.caption("Variables calculadas con datos históricos hasta el 31/12/2023. El consumidor final genérico se excluye.")

    # ─── Variable Objetivo (Y) ───
    if objetivo == "recurrencia":
        y_desc = f"El cliente <strong>compró</strong> en los {DIAS_RECURRENCIA} días posteriores al corte (31/12/2023)."
        y_zero = "No compró en ese periodo."
    else:
        y_desc = f"El cliente <strong>no compró</strong> en los {DIAS_CHURN} días posteriores al corte (31/12/2023)."
        y_zero = "Sí compró en ese periodo."

    st.markdown(f"""
    <div class="objetivo-box">
        <h4>🎯 Variable Objetivo (Y): <code>{objetivo}</code></h4>
        <p><strong>Clase 1:</strong> {y_desc}<br>
        <strong>Clase 0:</strong> {y_zero}</p>
    </div>
    """, unsafe_allow_html=True)

    # ─── Variables Predictoras (X) ───
    st.markdown("#### 🛠️ Variables Predictoras (X)")
    st.caption("Estas son las características que el modelo usa para hacer la predicción.")

    # Numéricas
    st.markdown("**📊 Numéricas**")
    cols_per_row = 4
    for i in range(0, len(NUMERIC_FEATURES), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, feat in enumerate(NUMERIC_FEATURES[i:i+cols_per_row]):
            icon, name, desc = FEATURE_META[feat]
            with cols[j]:
                st.markdown(f"""
                <div class="var-card">
                    <span class="var-icon">{icon}</span><span class="var-name">{name}</span>
                    <div class="var-desc">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

    # Categóricas (solo se usan en el modelo de churn)
    if objetivo == "churn":
        st.markdown("**🏷️ Categóricas**")
        cols = st.columns(3)
        for j, feat in enumerate(CATEGORICAL_FEATURES):
            icon, name, desc = FEATURE_META[feat]
            with cols[j]:
                st.markdown(f"""
                <div class="var-card">
                    <span class="var-icon">{icon}</span><span class="var-name">{name}</span>
                    <div class="var-desc">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.caption("El modelo de recurrencia usa solo variables de comportamiento de compra (sin datos demográficos), para reducir ruido con pocos clientes.")

    with st.expander("📊 Ver distribución de la variable objetivo"):
        balance = df["target"].value_counts().rename_axis("clase").reset_index(name="registros")
        balance["etiqueta"] = balance["clase"].map({0: "Clase 0", 1: "Clase 1"})
        fig = px.bar(balance, x="etiqueta", y="registros", color="etiqueta", color_discrete_sequence=[COLORS["blue"], COLORS["gold"]])
        fig.update_layout(**PLOTLY_LAYOUT, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)


def mostrar_evaluacion(resultado: dict, objetivo: str) -> None:
    st.subheader("📊 Evaluación real")

    st.caption(f"División 80% entrenamiento / 20% prueba (estratificada). El modelo se eligió comparando "
               f"3 algoritmos con validación cruzada de {CV_FOLDS} particiones sobre el 80% de entrenamiento; "
               f"el 20% de prueba nunca participó en esa selección y se usó una sola vez al final.")

    if resultado["accuracy_ideal_alcanzado"]:
        st.success(f"✅ Accuracy en TEST: {resultado['metrics']['accuracy']:.1%} — supera la meta ideal de {ACCURACY_IDEAL:.0%}.")
    elif resultado["accuracy_objetivo_cumplido"]:
        st.success(f"✅ Accuracy en TEST: {resultado['metrics']['accuracy']:.1%} — cumple la meta mínima de {ACCURACY_MINIMA:.0%}.")
    else:
        st.warning(f"⚠️ Accuracy en TEST: {resultado['metrics']['accuracy']:.1%}. No alcanza el {ACCURACY_MINIMA:.0%} mínimo con las variables actuales.")

    st.markdown("---")

    # ─── Métricas de clasificación en TEST (Accuracy, Precisión-Recall, ROC-AUC, Log-Loss) ───
    st.markdown("**🔒 Métricas de clasificación en TEST (20%, nunca visto durante el entrenamiento)**")
    labels = [("Accuracy", "accuracy"), ("Precisión", "precision"), ("Recall", "recall"),
              ("F1-Score", "f1"), ("ROC-AUC", "roc_auc"), ("Log-Loss", "log_loss")]
    cols = st.columns(6)
    for col, (label, key) in zip(cols, labels):
        with col:
            valor = resultado["metrics"][key]
            fmt = f"{valor:.3f}" if key == "log_loss" else f"{valor:.1%}"
            st.metric(label, fmt)
    st.caption(f"{resultado['X_test'].shape[0]} clientes en TEST · Umbral de decisión: {resultado['umbral']:.2f}")

    a, b = st.columns(2)
    with a:
        cm = confusion_matrix(resultado["y_test"], resultado["y_pred"], labels=[0, 1])
        fig = go.Figure(go.Heatmap(z=cm, x=["Predicho 0", "Predicho 1"], y=["Real 0", "Real 1"], text=cm, texttemplate="%{text}",
            colorscale=[[0, PANEL_SOLID], [0.5, STEEL], [1, GOLD_LIGHT]], showscale=False, textfont=dict(color=TEXT, size=16)))
        fig.update_layout(title="Matriz de confusión", height=360, **PLOTLY_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
    with b:
        fpr, tpr, _ = roc_curve(resultado["y_test"], resultado["y_proba"])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=fpr, y=tpr, mode="lines", name=f"Modelo AUC={resultado['metrics']['roc_auc']:.2f}", line={"color": COLORS["gold"], "width": 3}))
        fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Azar", line={"color": COLORS["muted"], "dash": "dash"}))
        fig.update_layout(title="Curva ROC", height=360, **PLOTLY_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
    report = pd.DataFrame(classification_report(resultado["y_test"], resultado["y_pred"], target_names=["Clase 0", "Clase 1"], output_dict=True)).T.reset_index().rename(columns={"index": "Clase"})
    st.dataframe(report.round(3), hide_index=True, use_container_width=True)
    with st.expander("Diagnóstico de probabilidades"):
        dist = pd.DataFrame({"probabilidad": resultado["y_proba"]})
        fig = px.histogram(dist, x="probabilidad", nbins=25, color_discrete_sequence=[COLORS["blue"]])
        fig.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
        st.write(f"Mínimo: {dist.probabilidad.min():.4f} · Máximo: {dist.probabilidad.max():.4f} · Desviación: {dist.probabilidad.std():.4f}")


# ─── Perfiles de ejemplo (valores típicos reales, calculados por mediana de clase) ──
# Se usan para poblar el laboratorio de predicción con un clic, sin tener que
# buscar un cliente ni llenar el formulario a mano durante una demo en vivo.
PERFIL_CLIENTE_FIEL = {
    "recencia": 45, "frecuencia": 8, "monto_total": 380, "ticket_promedio": 48,
    "antiguedad_dias": 600, "productos_unicos": 14, "categorias_unicas": 4,
    "dias_promedio_entre_compras": 55,
    "id_tipo_documento": "1", "genero": "Masculino", "localidad": "LIMÓN INDANZA",
}
PERFIL_CLIENTE_RIESGO = {
    "recencia": 210, "frecuencia": 2, "monto_total": 70, "ticket_promedio": 40,
    "antiguedad_dias": 400, "productos_unicos": 4, "categorias_unicas": 2,
    "dias_promedio_entre_compras": 40,
    "id_tipo_documento": "1", "genero": "Femenino", "localidad": "LIMÓN INDANZA",
}


def _cargar_perfil(objetivo: str, perfil: dict) -> None:
    """Escribe los valores del perfil directamente en session_state de los widgets."""
    for feature, valor in perfil.items():
        st.session_state[f"{objetivo}_{feature}"] = valor


def laboratorio(resultado: dict, df: pd.DataFrame, objetivo: str) -> None:
    st.subheader("🔮 Laboratorio de predicción")
    st.caption("Carga un ejemplo con un clic o busca un cliente real, ajusta lo que quieras y ejecuta la predicción.")

    features_modelo = resultado["features"]

    # ─── Botones de ejemplo rápido ───
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("✅ Ejemplo: cliente fiel", use_container_width=True, key=f"btn_fiel_{objetivo}"):
            _cargar_perfil(objetivo, PERFIL_CLIENTE_FIEL)
            st.rerun()
    with b2:
        if st.button("⚠️ Ejemplo: cliente en riesgo", use_container_width=True, key=f"btn_riesgo_{objetivo}"):
            _cargar_perfil(objetivo, PERFIL_CLIENTE_RIESGO)
            st.rerun()
    with b3:
        usar_cliente_real = st.toggle("🔎 Buscar cliente real", key=f"toggle_real_{objetivo}")

    if usar_cliente_real:
        clientes = query_df("SELECT cedula, nombre, apellido FROM cliente WHERE cedula <> :consumer", {"consumer": CONSUMIDOR_FINAL})
        clientes["nombre_completo"] = (clientes.nombre.fillna("").astype(str).str.strip() + " " + clientes.apellido.fillna("").astype(str).str.strip()).str.strip()
        disponibles = df.merge(clientes[["cedula", "nombre_completo"]], left_on="cedula_cliente", right_on="cedula", how="left").drop_duplicates("cedula_cliente").sort_values("nombre_completo")
        disponibles["etiqueta"] = disponibles.apply(lambda r: f"{r.nombre_completo or 'Sin nombre'} · {r.cedula_cliente}", axis=1)
        elegido = st.selectbox("👤 Cliente real", disponibles["etiqueta"].tolist(), key=f"selector_{objetivo}")
        if st.button("Cargar datos de este cliente", key=f"btn_cargar_real_{objetivo}"):
            fila = disponibles[disponibles.etiqueta == elegido].iloc[0]
            _cargar_perfil(objetivo, {f: fila[f] for f in NUMERIC_FEATURES + CATEGORICAL_FEATURES if f in fila})
            st.rerun()

    st.markdown("---")

    with st.form(f"formulario_{objetivo}"):
        st.markdown(f"**📊 Variables Numéricas**")
        entradas = {}
        c1, c2, c3 = st.columns(3)
        for idx, feature in enumerate(NUMERIC_FEATURES):
            icon, label, _ = FEATURE_META[feature]
            target_col = [c1, c2, c3][idx % 3]
            with target_col:
                valor_default = st.session_state.get(f"{objetivo}_{feature}", PERFIL_CLIENTE_FIEL[feature])
                entradas[feature] = st.number_input(
                    f"{icon} {label}",
                    min_value=0.0,
                    value=float(valor_default),
                    step=1.0,
                    format="%.0f",
                    key=f"{objetivo}_{feature}"
                )

        # Las variables categóricas solo se piden (y solo se usan) en el modelo de churn.
        if "id_tipo_documento" in features_modelo:
            st.markdown(f"**🏷️ Variables Categóricas**")
            cat_cols = st.columns(3)
            for idx, feature in enumerate(CATEGORICAL_FEATURES):
                icon, label, _ = FEATURE_META[feature]
                opciones_cat = sorted(df[feature].astype(str).unique().tolist())
                default_val = str(st.session_state.get(f"{objetivo}_{feature}", PERFIL_CLIENTE_FIEL[feature]))
                default_idx = opciones_cat.index(default_val) if default_val in opciones_cat else 0
                with cat_cols[idx]:
                    entradas[feature] = st.selectbox(f"{icon} {label}", opciones_cat, index=default_idx, key=f"{objetivo}_{feature}")

        ejecutar = st.form_submit_button("🔮 Ejecutar predicción", type="primary", use_container_width=True)

    if ejecutar:
        entrada = pd.DataFrame([entradas], columns=features_modelo)
        prob = float(resultado["modelo"].predict_proba(entrada)[:, 1][0])
        umbral_operativo = resultado["umbral"]
        positivo = prob >= umbral_operativo
        st.markdown("---")
        st.markdown("### 🎯 Resultado de la Predicción")
        r1, r2 = st.columns([1, 2])
        with r1:
            st.metric("📊 Probabilidad", f"{prob:.1%}", f"umbral: {umbral_operativo:.0%}")
        with r2:
            if objetivo == "recurrencia":
                if positivo:
                    st.success("🟢 Cliente potencialmente recurrente")
                else:
                    st.error("🔴 Baja probabilidad de recurrencia")
            else:
                if positivo:
                    st.error("🔴 Alto riesgo de abandono")
                else:
                    st.success("🟢 Bajo riesgo de abandono")
        st.progress(prob)
        st.caption(f"Clasificación con el mismo umbral usado en la evaluación oficial ({umbral_operativo:.0%}) — consistente con las métricas reportadas.")
        with st.expander("📝 Ver datos de entrada utilizados"):
            st.dataframe(entrada, hide_index=True, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# EJECUCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════
try:
    ventas, detalle, clientes = cargar_fuentes()
    if ventas.empty:
        st.warning("No existen ventas válidas para construir los modelos.")
    else:
        st.info(f"📆 Diseño temporal: observación hasta 31/12/2023. Recurrencia y churn usan {DIAS_RECURRENCIA} días futuros. El consumidor final no se modela.")
        objetivo = st.radio("Selecciona el modelo", ["recurrencia", "churn"], format_func=lambda x: "🧾 Recurrencia" if x == "recurrencia" else "⚠️ Churn", horizontal=True)
        df = construir_dataset(ventas, detalle, clientes, objetivo)

        # ─── TARJETAS MÉTRICAS ARRIBA (antes de los tabs) ────────────────────
        balance = df.target.value_counts()
        cards = st.columns(3)
        cards[0].metric("👥 CLIENTES MODELABLES", f"{len(df):,}", "Consumidor final excluido")
        cards[1].metric("✅ CLASE 1", f"{int(balance.get(1, 0)):,}", "Objetivo positivo")
        cards[2].metric("⬜ CLASE 0", f"{int(balance.get(0, 0)):,}", "Objetivo negativo")

        # ─── TABS ────────────────────────────────────────────────────────────
        tabs = st.tabs(["📘 Entender el modelo", "⚙️ Entrenamiento", "📊 Evaluación", "🔮 Probar predicción"])
        with tabs[0]:
            mostrar_variables(df, objetivo)
        with tabs[1]:
            st.markdown("**⚙️ Configuración aplicada**")
            st.write(
                f"Clasificación binaria con división real 80% entrenamiento / 20% prueba (estratificada). "
                f"Internamente se evalúan varias configuraciones con validación cruzada de {CV_FOLDS} "
                f"particiones dentro del 80% de entrenamiento, seleccionando la que obtenga mayor Accuracy "
                f"promedio — la métrica objetivo del proyecto (mínimo {ACCURACY_MINIMA:.0%}, ideal "
                f"{ACCURACY_IDEAL:.0%}+). El 20% de prueba se usa una única vez, al final, para confirmar "
                f"el desempeño real sobre datos nunca vistos."
            )
            if st.button("🚀 Entrenar / reentrenar modelo", type="primary", key=f"entrenar_{objetivo}"):
                with st.spinner("Separando datos 80/20 y comparando modelos..."):
                    try:
                        st.session_state[f"resultado_{objetivo}"] = entrenar(df, objetivo)
                        st.success("✅ Modelo entrenado correctamente.")
                    except Exception as exc:
                        st.error("No fue posible entrenar el modelo con los datos disponibles.")
                        st.exception(exc)
            if f"resultado_{objetivo}" in st.session_state:
                res_actual = st.session_state[f"resultado_{objetivo}"]
                st.json({
                    "tipo_modelo": NOMBRE_MODELO_DISPLAY,
                    "accuracy_cv_train": round(res_actual["cv_accuracy"], 3),
                    "accuracy_test": round(res_actual["metrics"]["accuracy"], 3),
                })
        resultado = st.session_state.get(f"resultado_{objetivo}")
        with tabs[2]:
            if resultado:
                mostrar_evaluacion(resultado, objetivo)
            else:
                st.info("Entrena el modelo para ver métricas reales, matriz de confusión, curva ROC y reporte de clasificación.")
        with tabs[3]:
            if resultado:
                laboratorio(resultado, df, objetivo)
            else:
                st.info("Primero entrena el modelo. Después podrás seleccionar un cliente real y cambiar los predictores antes de ejecutar la predicción.")
        if resultado:
            with st.expander("⬇️ Exportar resultados"):
                out = resultado["X_test"].copy()
                out["real"] = resultado["y_test"]
                out["predicho"] = resultado["y_pred"]
                out["probabilidad"] = resultado["y_proba"]
                st.download_button("💾 Descargar predicciones TEST", out.to_csv(index=False).encode("utf-8"), f"predicciones_{objetivo}.csv", "text/csv")
                buf = io.BytesIO()
                joblib.dump(resultado["modelo"], buf)
                st.download_button("💾 Descargar modelo .joblib", buf.getvalue(), f"modelo_{objetivo}.joblib", "application/octet-stream")
except Exception:
    st.error("No fue posible cargar el módulo de Predicción. Revisa la conexión y las tablas reales.")
    with st.expander("Detalle técnico"):
        st.code(traceback.format_exc())

# Pie de página (autoría), agregado automáticamente
show_footer()