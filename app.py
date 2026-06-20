import tempfile
import urllib.request

import branca.colormap as cm
import folium
import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium


st.set_page_config(page_title="Proyecto Final - Tracy Rivera", layout="wide")

POBLACION_URL = "https://raw.githubusercontent.com/TracyRivb/datos_poblacion/refs/heads/main/pobla_densi_canton.csv"
PRECIPITACION_URL = "https://raw.githubusercontent.com/TracyRivb/precipitacion/refs/heads/main/preci_canton.csv"
CENTROS_URL = "https://raw.githubusercontent.com/TracyRivb/centros_educativos/refs/heads/main/centros_educativos.csv"
DISTRITOS_IDS_URL = "https://github.com/TracyRivb/distritos_ids/raw/refs/heads/main/ids.gpkg"
POBLADOS_URL = "https://github.com/TracyRivb/poblados/raw/refs/heads/main/poblados.gpkg"

CANTONES = [
    "ASERRI",
    "CARTAGO",
    "CURRIDABAT",
    "DESAMPARADOS",
    "LA UNION",
    "MONTES DE OCA",
    "SAN JOSE",
]

MESES = [
    "ENERO",
    "FEBRERO",
    "MARZO",
    "ABRIL",
    "MAYO",
    "JUNIO",
    "JULIO",
    "AGOSTO",
    "SETIEMBRE",
    "OCTUBRE",
    "NOVIEMBRE",
    "DICIEMBRE",
]


@st.cache_data
def cargar_csv(url):
    return pd.read_csv(url)


@st.cache_data
def cargar_gpkg(url):
    with tempfile.NamedTemporaryFile(suffix=".gpkg", delete=False) as tmp:
        urllib.request.urlretrieve(url, tmp.name)
        gdf = gpd.read_file(tmp.name)

    if gdf.crs is not None:
        gdf = gdf.to_crs(epsg=4326)

    return gdf


def buscar_columna(df, opciones):
    for columna in opciones:
        if columna in df.columns:
            return columna
    return None


st.title("Datos Geoespaciales del Parque Metropolitano La Libertad")
st.caption("Estudiante: Tracy Rivera Benavides")

st.header("Introducción")
st.write(
    """
    El Parque Metropolitano La Libertad es un espacio de rehabilitación urbana ubicado entre
    Desamparados y La Unión. Esta aplicación presenta tablas, gráficos y mapas que ayudan
    a interpretar datos de población, precipitación, centros educativos, desarrollo social
    y poblados del área de influencia del parque.
    """
)

st.header("1. Datos de población")

datos_poblacion = cargar_csv(POBLACION_URL)

st.dataframe(datos_poblacion, use_container_width=True)

poblacion_cantones = (
    datos_poblacion
    .groupby("CANTON", as_index=False)["POBLACION"]
    .sum()
)

poblacion_cantones = (
    poblacion_cantones[poblacion_cantones["CANTON"].isin(CANTONES)]
    .sort_values(by="POBLACION", ascending=False)
)

st.subheader("Gráfico 1. Población por cantón de interés")

fig_poblacion = px.bar(
    poblacion_cantones,
    x="CANTON",
    y="POBLACION",
    title="Población por cantón de interés",
    labels={
        "CANTON": "Cantón",
        "POBLACION": "Población (número de habitantes)",
    },
    text="POBLACION",
)

fig_poblacion.update_yaxes(tickformat=",d")
fig_poblacion.update_layout(xaxis_tickangle=-45)
fig_poblacion.update_traces(textposition="outside")

st.plotly_chart(fig_poblacion, use_container_width=True)

st.write(
    """
    Este gráfico permite comparar la cantidad de habitantes en los cantones de interés.
    Los cantones con mayor población pueden representar una mayor demanda potencial de
    actividades, programas y servicios relacionados con el Parque Metropolitano La Libertad.
    """
)

st.header("2. Datos de precipitación")

precipitacion = cargar_csv(PRECIPITACION_URL)

st.dataframe(precipitacion, use_container_width=True)

filtro_precipitacion = precipitacion[precipitacion["CANTON"].isin(CANTONES)]

precipitacion_mensual = filtro_precipitacion.melt(
    id_vars="CANTON",
    value_vars=MESES,
    var_name="MES",
    value_name="PRECIPITACION",
)

precipitacion_agrupada = precipitacion_mensual.groupby(
    ["CANTON", "MES"],
    as_index=False,
)["PRECIPITACION"].sum()

st.subheader("Gráfico 2. Distribución de precipitación mensual por cantón")

fig_precipitacion = px.box(
    precipitacion_agrupada,
    x="CANTON",
    y="PRECIPITACION",
    title="Distribución de precipitación mensual por cantón de interés",
    labels={
        "CANTON": "Cantón",
        "PRECIPITACION": "Precipitación mensual (mm)",
        "MES": "Mes",
    },
    hover_data={
        "MES": True,
        "PRECIPITACION": ":.2f",
    },
    points="outliers",
)

st.plotly_chart(fig_precipitacion, use_container_width=True)

st.write(
    """
    El gráfico de cajas permite comparar la variación mensual de la precipitación por cantón.
    Cantones con rangos más amplios presentan mayor variabilidad entre meses secos y lluviosos.
    """
)

st.header("3. Centros educativos")

centros_educativos = cargar_csv(CENTROS_URL)

st.dataframe(centros_educativos, use_container_width=True)

centros_peds = centros_educativos[centros_educativos["PEDS"] == 1]

agrupacion_centros = (
    centros_peds
    .groupby(["CENTRO_EDU", "PEDS"])
    .agg({
        "RENDIMIENTO_ACADEMICO": "mean",
        "ESTUDIANTES": "sum",
    })
    .reset_index()
    .sort_values(by="ESTUDIANTES", ascending=False)
)

st.subheader("Tabla de agrupamiento de centros educativos")
st.dataframe(agrupacion_centros, use_container_width=True)

st.subheader("Gráfico 3. Relación entre estudiantes y rendimiento académico")

fig_centros = px.scatter(
    agrupacion_centros,
    x="ESTUDIANTES",
    y="RENDIMIENTO_ACADEMICO",
    text="CENTRO_EDU",
    title="Relación entre estudiantes y rendimiento académico en instituciones de interés",
    labels={
        "ESTUDIANTES": "Cantidad de estudiantes por institución",
        "RENDIMIENTO_ACADEMICO": "Rendimiento académico",
        "CENTRO_EDU": "Centro educativo",
    },
    hover_data={
        "PEDS": True,
        "ESTUDIANTES": ",",
        "RENDIMIENTO_ACADEMICO": ":.2f",
    },
)

fig_centros.update_traces(
    marker=dict(color="red", size=10),
    textposition="top center",
)

st.plotly_chart(fig_centros, use_container_width=True)

st.write(
    """
    Este gráfico muestra si existe alguna relación visual entre la cantidad de estudiantes
    y el rendimiento académico. Los puntos permiten comparar instituciones y observar
    cuáles tienen mayor población estudiantil o mayor rendimiento.
    """
)

st.header("4. Mapa 1: Índice de Desarrollo Social en distritos de interés")

distritos_ids_gdf = cargar_gpkg(DISTRITOS_IDS_URL)

st.dataframe(distritos_ids_gdf.drop(columns="geometry"), use_container_width=True)

ids_col = "IDS"

nombre_distrito_col = buscar_columna(
    distritos_ids_gdf,
    ["DISTRITO", "NOM_DIST", "NOMBRE", "distrito", "nombre"],
)

min_ids = float(distritos_ids_gdf[ids_col].min())
max_ids = float(distritos_ids_gdf[ids_col].max())

colormap = cm.linear.RdYlGn_09.scale(min_ids, max_ids)
colormap.caption = "Índice de Desarrollo Social"

mapa_ids = folium.Map(location=[9.93, -84.08], zoom_start=11, tiles="OpenStreetMap")

for _, registro in distritos_ids_gdf.iterrows():
    nombre = registro[nombre_distrito_col] if nombre_distrito_col else "Distrito"
    ids = registro[ids_col]

    popup = f"<b>Distrito:</b> {nombre}<br><b>IDS:</b> {ids}"

    folium.GeoJson(
        registro.geometry,
        style_function=lambda feature, valor=ids: {
            "fillColor": colormap(valor),
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.7,
        },
        tooltip=f"{nombre}: IDS {ids}",
        popup=popup,
    ).add_to(mapa_ids)

colormap.add_to(mapa_ids)

st_folium(mapa_ids, width=1100, height=550)

st.write(
    """
    El mapa permite identificar diferencias sociales entre distritos. Los sectores con IDS
    más bajo pueden ser considerados prioritarios para programas sociales, culturales o educativos.
    """
)

st.header("5. Mapa 2: Poblados en cantones de interés")

poblados_gdf = cargar_gpkg(POBLADOS_URL)

st.dataframe(poblados_gdf.drop(columns="geometry"), use_container_width=True)

mapa_poblados = folium.Map(location=[9.9, -84.0], zoom_start=11, tiles="OpenStreetMap")

cluster = MarkerCluster(name="Poblados").add_to(mapa_poblados)

for _, registro in poblados_gdf.iterrows():
    geometria = registro.geometry
    punto = geometria if geometria.geom_type == "Point" else geometria.centroid

    nombre = registro["NOMBRE"] if "NOMBRE" in poblados_gdf.columns else "Poblado"
    categoria = registro["CATEGORIA"] if "CATEGORIA" in poblados_gdf.columns else "Sin categoría"

    folium.Marker(
        location=[punto.y, punto.x],
        popup=folium.Popup(f"<b>Categoría:</b> {categoria}", max_width=250),
        tooltip=nombre,
    ).add_to(cluster)

st_folium(mapa_poblados, width=1100, height=550)

st.write(
    """
    La concentración de marcadores ayuda a reconocer zonas urbanas con mayor presencia de poblados.
    Esta información puede apoyar la planificación de actividades y la priorización de territorios
    con mayor población potencial beneficiaria.
    """
)

st.header("Conclusión")

st.write(
    """
    La aplicación integra tablas, gráficos y mapas para analizar el entorno territorial del
    Parque Metropolitano La Libertad. La información de población, precipitación, educación,
    desarrollo social y poblados permite apoyar procesos de planificación institucional y
    toma de decisiones sobre el área de influencia del parque.
    """
)
