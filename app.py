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


st.set_page_config(page_title="Datos Geoespaciales del Parque Metropolitano La Libertad", layout="wide")

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


def filtrar_dataframe(df, texto):
    if not texto:
        return df

    columnas = [columna for columna in df.columns if columna != "geometry"]
    mascara = (
        df[columnas]
        .astype(str)
        .apply(lambda columna: columna.str.contains(texto, case=False, na=False))
        .any(axis=1)
    )
    return df[mascara]


st.title("Datos Geoespaciales del Parque Metropolitano La Libertad")
st.caption("Estudiante: Tracy Rivera Benavides")

st.sidebar.header("Buscador")
busqueda = st.sidebar.text_input(
    "Buscar en tablas, gráficos y mapas",
    placeholder="Ejemplo: DESAMPARADOS, RIO AZUL, escuela",
)

if busqueda:
    st.sidebar.success(f"Filtro activo: {busqueda}")
else:
    st.sidebar.info("Sin filtro activo")

st.header("Introducción")
st.write(
    """
El Parque Metropolitano La Libertad surge como una iniciativa de rehabilitación urbana orientada a transformar un antiguo espacio industrial (ocupado durante más de 50 años por la fábrica de Productos de Concreto) en un parque dedicado al Desarrollo Humano. Este proyecto se materializa a partir de una Alianza Público-Privada para el Desarrollo (APPD) entre la Fundación Parque Metropolitano La Libertad y el Ministerio de Cultura y Juventud de Costa Rica (MCJ), con el propósito de gestionar y consolidar un espacio que promueva oportunidades de crecimiento social, cultural, educativo y ambiental para la población (La Libertad, 2024). Desde su creación en el año 2008, el parque se localiza en los cantones de Desamparados y La Unión, en un contexto territorial caracterizado por una alta densidad poblacional y una fuerte interacción con distritos cercanos como Aserrí, Damas, Gravilias, Los Guido, Patarrá, Río Azul, San Antonio, San Miguel y Tirrases. De la misma manera, el parque cuenta con una extensión aproximada de 32 hectáreas de espacio público y ocho hectáreas de bosque conservado, lo que lo convierte en un espacio relevante para el desarrollo social y ambiental de la región (La Libertad, 2024).

### **Estado actual de los datos geoespaciales**
El Parque Metropolitano La Libertad cuenta con información geográfica utilizada para apoyar los procesos de análisis, planificación y toma de decisiones dentro de la institución. Sin embargo, estos datos no son generados directamente por el parque, sino que provienen de diversas instituciones externas que los comparten para su uso institucional.

Algunos datos geográficos disponibles son:

**1. Territorio:** presenta la información geográfica básica que permite ubicar y contextualizar espacialmente el Parque Metropolitano La Libertad dentro del territorio nacional y local. Incluye el límite del parque, así como las divisiones administrativas cercanas como cantones y distritos, lo que permite comprender la relación del parque con su entorno territorial y administrativo.

**2. Ambiente:** se integra información relacionadas con los elementos naturales y de protección ambiental presentes en el territorio. Se incluyen precipitación, ríos, zonas protectoras y el límite del Corredor Biológico Interurbano Bicentenario Tiribí, con el fin de identificar áreas de valor ecológico, conectividad ambiental y recursos naturales que influyen en la planificación y gestión del territorio alrededor del parque.

**3. Población:** muestra información demográfica y social del área de influencia del parque. Contiene datos sobre vivienda, población e indicadores socioeconómicos, lo que permite comprender las características de la población cercana y analizar aspectos como densidad poblacional, condiciones sociales y necesidades territoriales que pueden influir en la planificación de programas y proyectos institucionales.

**4. Institucionalidad:** reúne información sobre las principales instituciones presentes en el territorio, especialmente aquellas relacionadas con educación y administración pública. Incluye la ubicación de escuelas, colegios y gobiernos locales, lo que permite visualizar la red institucional del área y comprender cómo se articulan las instituciones con el desarrollo social y territorial de las comunidades cercanas al parque.

**5. Industria y comercio:** presenta información sobre la actividad económica del territorio, enfocándose en la localización de pymes y emprendimientos presentes en el área de influencia del parque. Esta información permite identificar dinámicas económicas locales, oportunidades de desarrollo productivo y posibles vínculos entre la actividad económica y los programas de formación o emprendimiento impulsados por el parque.

**6. Organizaciones comunales:** se identifican las principales organizaciones comunitarias que participan en la gestión y desarrollo local del territorio. Se incluyen asociaciones de desarrollo, juntas comunales y comités, con el objetivo de reconocer los actores sociales presentes en las comunidades cercanas al parque y fortalecer la articulación entre la institución y las organizaciones comunitarias para la implementación de proyectos y actividades territoriales.

A continuación, se muestran tres gráficos empleando la información anteriomente descrita mediante la biblioteca plotly (biblioteca para gráficos interactivos), así también como dos mapas a partir de las  bibliotecas folium y leafmap.
    """
)

st.header("1. Datos de población")

datos_poblacion = cargar_csv(POBLACION_URL)
datos_poblacion_filtrados = filtrar_dataframe(datos_poblacion, busqueda)

st.dataframe(datos_poblacion_filtrados, use_container_width=True)

poblacion_cantones = (
    datos_poblacion_filtrados
    .groupby("CANTON", as_index=False)["POBLACION"]
    .sum()
)

poblacion_cantones = (
    poblacion_cantones[poblacion_cantones["CANTON"].isin(CANTONES)]
    .sort_values(by="POBLACION", ascending=False)
)

st.write(
    """
   **Descripción de variables:** La tabla denominada “datos_población” está compuesta por tres columnas principales: “POBLACION”, “DENSIDAD” y “CANTON”. Estas variables permiten representar información demográfica relacionada con los cantones de Costa Rica. La columna “POBLACION” corresponde a la cantidad total de habitantes registrados en cada cantón, mientras que la variable “DENSIDAD” indica la concentración de población en relación con el territorio, generalmente expresada en habitantes por kilómetro cuadrado. La columna “CANTON” identifica el nombre de cada unidad territorial analizada.

    """
)

st.subheader("Gráfico 1. Población por cantón de interés")

if poblacion_cantones.empty:
    st.warning("No hay datos de población que coincidan con la búsqueda.")
else:
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
    **Descripción del gráfico**: El gráfico 1 contiene información relacionada con la población de distintos cantones de Costa Rica, específicamente: Aserrí, Cartago, Curridabat, Desamparados, La Unión, Montes de Oca y San José. Para cada uno de estos cantones se registra la cantidad total de habitantes, permitiendo visualizar la distribución poblacional de las principales zonas de influencia vinculadas al Parque Metropolitano La Libertad.

La selección de estos cantones responde a criterios de proximidad territorial y dinámica de uso del parque, ya que corresponden a los sectores desde donde proviene una gran parte de las personas visitantes. Debido a esta relación espacial y funcional, la información poblacional de estos territorios es importante para comprender el contexto demográfico asociado al área de estudio.

De acuerdo con los datos presentados, el cantón con mayor cantidad de habitantes es San José, con una población de 313 262 habitantes, mientras que el cantón con menor población corresponde a Aserrí, con 49 271 habitantes. Estas diferencias demográficas permiten identificar variaciones importantes en la concentración poblacional de los territorios analizados.


    """
)

st.header("2. Datos de precipitación")

precipitacion = cargar_csv(PRECIPITACION_URL)
precipitacion_filtrada = filtrar_dataframe(precipitacion, busqueda)

st.dataframe(precipitacion_filtrada, use_container_width=True)

filtro_precipitacion = precipitacion_filtrada[precipitacion_filtrada["CANTON"].isin(CANTONES)]

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

st.write(
    """
    **Descripción de variables:** Dentro de las principales variables de la tabla se encuentra la columna "CANTON", la cual identifica el nombre del cantón al que pertenecen los registros climáticos. También, la tabla posee una columna individual para cada mes del año, correspondientes a "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SETIEMBRE", "OCTUBRE", "NOVIEMBRE" y "DICIEMBRE". Cada una de estas columnas almacena la precipitación mensual total registrada en el cantón respectivo, generalmente expresada en milímetros (mm) del año 2020.

Los datos de precipitación mensual son fundamentales para la gestión del riesgo en zonas cercanas al Parque Metropolitano La Libertad, debido a que permiten identificar patrones de comportamiento climático asociados a eventos de lluvias intensas y periodos de alta acumulación hídrica. La información es fundamental para evaluar áreas con mayor susceptibilidad a inundaciones, saturación de suelos y deslizamientos, especialmente en sectores con pendientes pronunciadas, cercanía a ríos o condiciones de vulnerabilidad territorial.

    """
)

st.subheader("Gráfico 2. Distribución de precipitación mensual por cantón")

if precipitacion_agrupada.empty:
    st.warning("No hay datos de precipitación que coincidan con la búsqueda.")
else:
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
   **Descripción del gráfico:** en el gráfico 2 se observa que todos los cantones presentan un comportamiento relativamente similar, con medianas cercanas a los 200 mm mensuales. Sin embargo, Aserrí destaca por registrar los valores máximos de precipitación más altos, alcanzando aproximadamente 460 mm, lo que indica una mayor intensidad o acumulación de lluvias en ciertos meses del año. Asimismo, presenta una dispersión considerable, reflejando una alta variabilidad temporal de la precipitación.

Por otro lado, cantones como Curridabat, Montes de Oca y San José muestran medianas ligeramente inferiores y rangos relativamente amplios, lo que sugiere fluctuaciones importantes entre meses secos y lluviosos. Cartago y La Unión presentan distribuciones más concentradas, indicando un comportamiento pluviométrico más estable en comparación con otros cantones analizados.
    """
)

st.header("3. Centros educativos")

centros_educativos = cargar_csv(CENTROS_URL)
centros_educativos_filtrados = filtrar_dataframe(centros_educativos, busqueda)

st.dataframe(centros_educativos_filtrados, use_container_width=True)

centros_peds = centros_educativos_filtrados[centros_educativos_filtrados["PEDS"] == 1]

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

st.write(
    """
  **Descripción de las variables:** La tabla llamada “agrupacion_centros” está compuesta por diferentes columnas por las variables “CENTRO_EDU”, “PEDS”, “RENDIMIENTO_ACADEMICO” y “ESTUDIANTES”.

La columna “CENTRO_EDU” corresponde al nombre de cada centro educativo o escuela analizada dentro del área de estudio. Por su parte, la variable “PEDS” identifica la participación de las instituciones en el Programa de Educación para el Desarrollo Sostenible del Parque Metropolitano La Libertad (PEDS), mediante valores binarios donde 0 representa que el centro educativo no participa en el programa y 1 indica que sí participa.

Asimismo, la columna “RENDIMIENTO_ACADEMICO” contiene información relacionada con el desempeño académico de cada institución educativa, permitiendo realizar comparaciones entre centros educativos y evaluar posibles relaciones con variables territoriales o de participación institucional. La variable “ESTUDIANTES” representa la cantidad total de estudiantes registrados en cada escuela, lo cual permite dimensionar el alcance poblacional de los centros educativos incluidos en el análisis.

    """
)

st.subheader("Gráfico 3. Relación entre estudiantes y rendimiento académico")

if agrupacion_centros.empty:
    st.warning("No hay centros educativos que coincidan con la búsqueda.")
else:
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
    **Descripción del gráfico:** El gráfico 3 muestra la relación entre la cantidad de estudiantes por institución educativa y el rendimiento académico de distintos centros educativos vinculados al área de influencia del Parque Metropolitano La Libertad.

Entre los resultados más importantes se destaca que la Escuela de Gravilias presenta uno de los rendimientos académicos más altos del conjunto analizado, mientras que instituciones como la Escuela Francisco Gamboa reflejan valores comparativamente menores. Además, la Escuela Quince de Agosto sobresale por ser la institución con mayor cantidad de estudiantes, aunque su rendimiento académico se mantiene en valores intermedios respecto al resto de escuelas.

De esta manera, el gráfico no muestra una relación lineal claramente definida entre la cantidad de estudiantes y el rendimiento académico, lo que sugiere que el desempeño académico no depende únicamente del tamaño de la población estudiantil.

    """
)

st.header("4. Mapa 1: Índice de Desarrollo Social en distritos de interés")

distritos_ids_gdf = cargar_gpkg(DISTRITOS_IDS_URL)
distritos_ids_gdf_filtrados = filtrar_dataframe(distritos_ids_gdf, busqueda)

st.write(
    """
  **Descripción de las variables:** El GeoPackage (GPKG) seleccionado contiene diversas variables asociadas a la división político-administrativa y a las características sociodemográficas de los distritos analizados. Entre la información disponible se incluyen datos de población total, densidad poblacional, crecimiento demográfico, cantidad de hombres y mujeres, así como otros indicadores relevantes para el análisis territorial.

Para este caso, se enfocará en los distritos con mayor incidencia e influencia sobre el Parque Metropolitano La Libertad, los cuales corresponden a:  San Juan de Dios, Río Azul, Damas, Gravilias, San Antonio, San Rafael Abajo, San Diego, Desamparados, Tirrases, Zapote, Curridabat, Los Guido, Patarrá, San Rafael Arriba y San Miguel. Estos distritos constituyen el principal ámbito de acción e impacto del parque, por lo que su caracterización resulta fundamental para comprender las dinámicas sociales y territoriales del entorno.

También, se considera la variable “IDS” (Índice de Desarrollo Social), que evalua las condiciones de desarrollo de cada distrito a partir de diversos factores socioeconómicos. Este indicador es una herramienta estratégica para la toma de decisiones, ya que, facilita la identificación de territorios con mayores necesidades de intervención y apoyo.
    """
)

st.dataframe(distritos_ids_gdf_filtrados.drop(columns="geometry"), use_container_width=True)

ids_col = "IDS"

nombre_distrito_col = buscar_columna(
    distritos_ids_gdf_filtrados,
    ["DISTRITO", "NOM_DIST", "NOMBRE", "distrito", "nombre"],
)

if distritos_ids_gdf_filtrados.empty:
    st.warning("No hay distritos que coincidan con la búsqueda.")
else:
    min_ids = float(distritos_ids_gdf_filtrados[ids_col].min())
    max_ids = float(distritos_ids_gdf_filtrados[ids_col].max())

    colormap = cm.linear.RdYlGn_09.scale(min_ids, max_ids)
    colormap.caption = "Índice de Desarrollo Social"

    mapa_ids = folium.Map(location=[9.93, -84.08], zoom_start=11, tiles="OpenStreetMap")

    for _, registro in distritos_ids_gdf_filtrados.iterrows():
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
    **Descripción del mapa:** se muestra la distribución del Índice de Desarrollo Social (IDS) en los distritos que conforman el área de influencia del Parque Metropolitano La Libertad. Los resultados evidencian diferencias importantes entre los territorios analizados, con valores que oscilan entre 63,43 y 86,02 puntos.

Los distritos con los valores más bajos corresponden a Río Azul (63,43) y Los Guido (66,38), mientras que los índices más altos se presentan en Gravilias (86,02), San Antonio (84,81) y Curridabat (83,35). En general, la mayoría de los distritos se ubican en rangos intermedios de desarrollo social.

Esta información permite al parque identificar territorios con mayores necesidades sociales y orientar de manera más eficiente la planificación de proyectos, programas y actividades comunitarias, priorizando aquellos distritos con menores niveles de desarrollo social.
    """
)

st.header("5. Mapa 2: Poblados en cantones de interés")

poblados_gdf = cargar_gpkg(POBLADOS_URL)
poblados_gdf_filtrados = filtrar_dataframe(poblados_gdf, busqueda)

st.dataframe(poblados_gdf_filtrados.drop(columns="geometry"), use_container_width=True)

st.write(
    """
    **Descripción de las variables:** El GeoPackage (GPKG) seleccionado corresponde a una capa geográfica que almacena información espacial y descriptiva de entidades territoriales. Para cada registro se incluye un identificador único (**fid**), un código de identificación de la entidad (**ET_ID**), el nombre de la entidad (**NOMBRE**), una clasificación o tipo de entidad (**CATEGORIA**), la hoja cartográfica de referencia (**HOJA**) y las coordenadas espaciales (**X** y **Y**) que indican la ubicación geográfica de cada elemento.


Los datos se encuentran filtrados por los cantones de interés para el Parque Metropolitano La Libertad que son: Aserrí, Cartago, Curridabat, Desamparados, La Unión, Montes de Oca y San José. Este tipo de información es vital para la gestión territorial y los análisis espaciales, pues, facilita la identificación, localización y caracterización de los elementos presentes en el territorio.

    """
)

if poblados_gdf_filtrados.empty:
    st.warning("No hay poblados que coincidan con la búsqueda.")
else:
    mapa_poblados = folium.Map(location=[9.9, -84.0], zoom_start=11, tiles="OpenStreetMap")

    cluster = MarkerCluster(name="Poblados").add_to(mapa_poblados)

    for _, registro in poblados_gdf_filtrados.iterrows():
        geometria = registro.geometry
        punto = geometria if geometria.geom_type == "Point" else geometria.centroid

        nombre = registro["NOMBRE"] if "NOMBRE" in poblados_gdf_filtrados.columns else "Poblado"
        categoria = registro["CATEGORIA"] if "CATEGORIA" in poblados_gdf_filtrados.columns else "Sin categoría"

        folium.Marker(
            location=[punto.y, punto.x],
            popup=folium.Popup(f"<b>Categoría:</b> {categoria}", max_width=250),
            tooltip=nombre,
        ).add_to(cluster)

    st_folium(mapa_poblados, width=1100, height=550)

st.write(
    """
    **Descripción del mapa:** se muestra la distribución de los poblados dentro del área de influencia del Parque Metropolitano La Libertad. La mayor concentración se localiza en los sectores urbanos de San José, Desamparados, Curridabat y sus alrededores, donde se agrupan hasta 329 poblados, evidenciando una alta densidad de asentamientos en comparación con las zonas periféricas y rurales del sur.

Esta información es importante para el parque porque permite identificar las áreas con mayor cantidad de población potencial beneficiaria de sus programas y actividades. Además, facilita la planificación de proyectos, la definición de estrategias de alcance comunitario y la priorización de recursos hacia los territorios con mayor concentración de poblados y, por ende, con un mayor potencial de impacto social.

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
