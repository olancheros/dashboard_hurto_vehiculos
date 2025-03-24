#######################
# Importar librarías
import altair as alt
import geopandas as gpd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

import os

# checking that the current working directory is correct to ensure that the file paths are working
if os.getcwd()[-3:] == "Src":
    os.chdir('..')


#######################
# Page configuration
st.set_page_config(
    page_title="Hurto Vehiculos Dashboard",
    page_icon="💂",
    layout="wide",
    initial_sidebar_state="expanded",
)


#######################
# path
path_autos = "Data/Processed/hurto_autos_2003-2024.csv"
path_motos = "Data/Processed/hurto_motos_2003-2024.csv"
path_autos_mensual = "Data/Processed/hurto_autos_mensual_2003-2024.csv"
path_motos_mensual = "Data/Processed/hurto_motos_mensual_2003-2024.csv"
path_mapa = "Shapefiles/SHP_MGN2018_INTGRD_DEPTO/MGN_ANM_DPTOS.shp"
css_path = "assets/styles.css"


#######################
# cache
TTL = 7200


@st.cache_data(ttl=TTL)
#######################


#######################
# CSS styling
def load_css(file_path):
    with open(file_path) as f:
        st.html(f"<style>{f.read()}</style>")


st.markdown(
    "",
    unsafe_allow_html=True,
)


#######################
# Carga de datos
def dataload(path):
    df = pd.read_csv(path, encoding="utf8", dtype={"cod_depto": str})
    return df


#######################
# Sidebar
with st.sidebar:
    st.title("Hurto Vehículos")

    vehicle_list = ["Automotor", "Motocicleta"]
    selected_vehicle = st.selectbox("Seleccionar tipo vehículo", vehicle_list)

    if selected_vehicle == "Automotor":
        auto_df = dataload(path_autos)
        auto_df_mes = dataload(path_autos_mensual)
    else:
        auto_df = dataload(path_motos)
        auto_df_mes = dataload(path_motos_mensual)

    year_list = list(auto_df.año.unique())[::-1]

    selected_year = st.selectbox("Seleccionar año", year_list)
    df_selected_year = auto_df[auto_df.año == selected_year]
    df_selected_year_tbl = df_selected_year[
        ["cod_depto", "departamento", "año", "num_hurtos"]
    ]
    df_selected_year_sorted = df_selected_year_tbl.sort_values(
        by="num_hurtos", ascending=False
    )

    color_theme_list = [
        "balance",
        "cividis",
        "viridis",
    ]
    selected_color_theme = st.selectbox("Seleccionar Paleta de Color", color_theme_list)

    with st.expander("Observación", expanded=True):
        st.write("""
                - Fuente Datos: [Datos Abiertos Gobierno de Colombia](https://www.datos.gov.co/Seguridad-y-Defensa/HURTO-A-VEH-CULOS/csb4-y6v2/about_data).
                - :orange[**Dptos con mayor aumento/disminución de hurto en el año**]: Departamentos con el mayor aumento y disminución de hurto en el año seleccionado.
                - :orange[**Porcentaje total dptos aumento/disminución de hurto en el año**]: Porcentaje de departamentos donde aumenta y disminuye el hurto .
                - :orange[**Distribución Hurto por Departamento**]: Mapa de coropletas con la variación del hurto en Colombia para el año seleccionado. Escala de color logarítmica para mejor contraste.
                - :orange[**Heatmap**]: Mapa de Calor con la variación del hurto en Colombia para todo el periodo de estudio. Escala de color logarítmica para mejor contraste.
                - :orange[**Comportamiento Anual del Hurto**]: Evolución mensual del hurto para el año seleccionado.
                """)


#######################
# Heatmap
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = px.density_heatmap(
        input_df,
        x=input_x,
        y=input_y,
        z=input_color,
        histfunc="max",
        nbinsx=25,
        nbinsy=25,
        color_continuous_scale=input_color_theme,
        template="plotly_dark",
        labels={input_x: input_x.capitalize(), input_y: input_y.capitalize()},
    )

    heatmap.update_xaxes(tickangle=270, title=None)
    heatmap.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=300,
    )
    heatmap.update(layout_coloraxis_showscale=False)

    return heatmap


#######################
# Choropleth map
colombia = gpd.read_file(
    path_mapa,
    encoding="utf8",
    dtype={"DPTO_CCDGO": str},
).loc[
    :,
    (
        "DPTO_CCDGO",
        "DPTO_CNMBR",
        "AREA",
        "LATITUD",
        "LONGITUD",
        "Shape_Leng",
        "Shape_Area",
        "geometry",
    ),
]

colombia = colombia.to_crs(epsg=4326)


def make_choropleth(input_df, input_id, input_column, input_color_theme):
    choropleth = px.choropleth_mapbox(
        input_df,
        geojson=colombia.set_index("DPTO_CCDGO")["geometry"],
        locations=input_id,
        featureidkey="id",
        color=input_column,
        color_continuous_scale=input_color_theme,
        range_color=(
            0,
            max(input_df[input_column]),
        ),  # Rango de color basado en la columna seleccionada
        hover_name="departamento",  # Nombre que se muestra al pasar el mouse
        hover_data=[
            "num_hurtos"
        ],  # Datos adicionales que se muestran al pasar el mouse
        labels={input_column: f"Log Núm Hurtos"},  # Etiqueta para la leyenda
        mapbox_style="carto-darkmatter",  # Estilo del mapa base
        center=dict(lat=4.0, lon=-73.0),  # Centro del mapa en Colombia
        zoom=4.0,  # Nivel de zoom
    )

    # Ajustar el mapa para que se ajuste a las ubicaciones
    choropleth.update_geos(fitbounds="locations", visible=False)

    # Actualizar el layout del gráfico
    choropleth.update_layout(
        height=400,  # Altura del gráfico
        template="plotly_dark",  # Plantilla de estilo oscuro
        plot_bgcolor="rgba(0, 0, 0, 0)",  # Fondo transparente para el gráfico
        paper_bgcolor="rgba(0, 0, 0, 0)",  # Fondo transparente para el área del papel
        margin=dict(l=0, r=0, t=0, b=0),  # Márgenes ajustados
    )
    return choropleth


#######################
# Line chart
df_total = (
    auto_df.groupby(["año"])["num_hurtos"].sum().reset_index(name="sum_num_hurtos")
)
df_total["acumulado"] = np.cumsum(df_total["sum_num_hurtos"])


def make_linechart_year(df):
    # Crear las trazas para cada línea
    fig_1 = go.Figure(
        go.Scatter(
            x=df["año"],
            y=df["sum_num_hurtos"],
            name="Hurto Anual",
            mode="lines+markers",
            line=dict(
                color="royalblue",
                width=2,
            ),
        )
    )

    fig_2 = go.Figure(
        go.Scatter(
            x=df["año"],
            y=df["acumulado"],
            name="Acumulado Anual",
            mode="lines+markers",
            line=dict(color="firebrick", width=2),
        )
    )

    # Crear subplots
    linechart = make_subplots(
        rows=2, cols=1, subplot_titles=("Hurto Anual", "Acumulado Anual")
    )

    # Agregar trazas a los subplots
    for trace in fig_1.data:
        linechart.add_trace(trace, row=1, col=1)

    for trace in fig_2.data:
        linechart.add_trace(trace, row=2, col=1)

    # Configuración del diseño
    linechart.update_layout(
        showlegend=False,
        height=250,
        xaxis2=dict(title=dict(text="Año")),
        yaxis1=dict(title=dict(text="Num Hurtos")),
        yaxis2=dict(title=dict(text="Num Hurtos")),
        # template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        margin=dict(l=0, r=0, t=20, b=0),  # Márgenes ajustados
    )
    return linechart


# Diccionario para mapeo de meses
month = {
    1: "ene",
    2: "feb",
    3: "mar",
    4: "abr",
    5: "may",
    6: "jun",
    7: "jul",
    8: "ago",
    9: "sep",
    10: "oct",
    11: "nov",
    12: "dic",
}

df_selected_year_month = auto_df_mes[auto_df_mes.año == selected_year]
df_selected_month = (
    df_selected_year_month.groupby(["mes"])["num_hurtos"]
    .sum()
    .reset_index(name="sum_num_hurtos")
)
df_selected_month["acumulado"] = np.cumsum(df_selected_month["sum_num_hurtos"])
df_selected_month["mes_cat"] = df_selected_month["mes"].map(month)


def make_linechart_month(df):
    # Crear las trazas para cada línea
    fig_1 = go.Figure(
        go.Scatter(
            x=df["mes_cat"],
            y=df["sum_num_hurtos"],
            name="Hurto Mensual",
            mode="lines+markers",
        )
    )

    fig_2 = go.Figure(
        go.Scatter(
            x=df["mes_cat"],
            y=df["acumulado"],
            name="Acumulado Mensual",
            mode="lines+markers",
        )
    )

    # Crear subplots
    linechart = make_subplots(
        rows=2, cols=1, subplot_titles=("Hurto Mensual", "Acumulado Mensual")
    )

    # Agregar trazas a los subplots
    for trace in fig_1.data:
        linechart.add_trace(trace, row=1, col=1)

    for trace in fig_2.data:
        linechart.add_trace(trace, row=2, col=1)

    # Configuración del diseño
    linechart.update_layout(
        showlegend=False,
        height=280,
        xaxis2=dict(title=dict(text="Mes")),
        yaxis1=dict(title=dict(text="Num Hurtos")),
        yaxis2=dict(title=dict(text="Num Hurtos")),
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        margin=dict(l=0, r=0, t=20, b=0),  # Márgenes ajustados
    )
    return linechart


#######################
# Donut chart
def make_donut(input_response, input_text, input_color):
    if input_color == "blue":
        chart_color = ["#29b5e8", "#155F7A"]
    if input_color == "green":
        chart_color = ["#27AE60", "#12783D"]
    if input_color == "orange":
        chart_color = ["#F39C12", "#875A12"]
    if input_color == "red":
        chart_color = ["#E74C3C", "#781F16"]

    source = pd.DataFrame(
        {"Topic": ["", input_text], "% value": [100 - input_response, input_response]}
    )
    source_bg = pd.DataFrame({"Topic": ["", input_text], "% value": [100, 0]})

    plot = (
        alt.Chart(source)
        .mark_arc(innerRadius=45, cornerRadius=25)
        .encode(
            theta="% value",
            color=alt.Color(
                "Topic:N",
                scale=alt.Scale(
                    # domain=['A', 'B'],
                    domain=[input_text, ""],
                    # range=['#29b5e8', '#155F7A']),  # 31333F
                    range=chart_color,
                ),
                legend=None,
            ),
        )
        .properties(width=130, height=130)
    )

    text = plot.mark_text(
        align="center",
        color="#29b5e8",
        font="Lato",
        fontSize=32,
        fontWeight=700,
        fontStyle="italic",
    ).encode(text=alt.value(f"{input_response} %"))
    plot_bg = (
        alt.Chart(source_bg)
        .mark_arc(innerRadius=45, cornerRadius=20)
        .encode(
            theta="% value",
            color=alt.Color(
                "Topic:N",
                scale=alt.Scale(
                    # domain=['A', 'B'],
                    domain=[input_text, ""],
                    range=chart_color,
                ),  # 31333F
                legend=None,
            ),
        )
        .properties(width=130, height=130)
    )
    return plot_bg + plot + text


#######################
# Convert population to text
def format_number(num):
    if num > 1000:
        if not num % 1000:
            return f"{num // 1000} k"
        return f"{round(num / 1000, 2)} k"
    return f"{num}"


#######################
# Cálculo año-sobre-año variación de hurto
def calculate_thieft_difference(input_df, input_year):
    selected_year_data = input_df[input_df["año"] == input_year].reset_index()
    previous_year_data = input_df[input_df["año"] == input_year - 1].reset_index()
    selected_year_data["diferencia_hurto"] = selected_year_data.num_hurtos.sub(
        previous_year_data.num_hurtos, fill_value=0
    )
    return pd.concat(
        [
            selected_year_data.departamento,
            selected_year_data.cod_depto,
            selected_year_data.num_hurtos,
            selected_year_data.diferencia_hurto,
        ],
        axis=1,
    ).sort_values(by="diferencia_hurto", ascending=False)


#######################
# Dashboard Main Panel

#######################
# Títle
st.markdown("#### Hurto Automotores en Colombia entre los Años 2003 a 2024")


#######################
# Viz Total Trend
main_col = st.columns((1), gap="small", border=True)
st.markdown("###### Análisis Año Seleccionado")
with main_col[0]:
    linechart_total = make_linechart_year(df_total)
    st.plotly_chart(linechart_total, use_container_width=True)


#######################
# Viz Maps and Annual Trend
col = st.columns((1, 3, 2), gap="medium", border=True)
with col[0]:
    st.markdown("###### Dptos con mayor aumento/disminución de hurto en el año")

    df_thieft_difference_sorted = calculate_thieft_difference(auto_df, selected_year)

    if selected_year > 2003:
        first_department_name = df_thieft_difference_sorted.departamento.iloc[0]
        first_department_thieft = format_number(
            df_thieft_difference_sorted.num_hurtos.iloc[0]
        )
        first_department_delta = format_number(
            df_thieft_difference_sorted.diferencia_hurto.iloc[0]
        )
    else:
        first_department_name = "N.D"
        first_department_thieft = "N.D"
        first_department_delta = ""
    st.metric(
        label=first_department_name,
        value=first_department_thieft,
        delta=first_department_delta,
    )

    if selected_year > 2003:
        last_department_name = df_thieft_difference_sorted.departamento.iloc[-1]
        last_department_thieft = format_number(
            df_thieft_difference_sorted.num_hurtos.iloc[-1]
        )
        last_department_delta = format_number(
            df_thieft_difference_sorted.diferencia_hurto.iloc[-1]
        )
    else:
        last_department_name = "N.D"
        last_department_thieft = "N.D"
        last_department_delta = ""
    st.metric(
        label=last_department_name,
        value=last_department_thieft,
        delta=last_department_delta,
    )

    st.markdown("###### Porcentaje total dptos aumento/disminución de hurto en el año")

    if selected_year > 2003:
        # Filtro departamentos con diferencia de número de hurtos > 50
        df_greater_50 = df_thieft_difference_sorted[
            df_thieft_difference_sorted.diferencia_hurto > 1
        ]
        df_less_50 = df_thieft_difference_sorted[
            df_thieft_difference_sorted.diferencia_hurto < -1
        ]

        # % de Departamentos con diferencia de hurtos > 50
        department_thieft_greater = round(
            (len(df_greater_50) / df_thieft_difference_sorted.departamento.nunique())
            * 100
        )
        department_thieft_less = round(
            (len(df_less_50) / df_thieft_difference_sorted.departamento.nunique()) * 100
        )
        donut_chart_greater = make_donut(
            department_thieft_greater, "Aumento Hurto", "red"
        )
        donut_chart_less = make_donut(
            department_thieft_less, "Disminución Hurto", "green"
        )
    else:
        department_thieft_greater = 0
        department_thieft_less = 0
        donut_chart_greater = make_donut(
            department_thieft_greater, "Aumento Hurto", "red"
        )
        donut_chart_less = make_donut(
            department_thieft_less, "Disminución Hurto", "green"
        )

    thieft_col = st.columns((0.15, 1, 0.15))
    with thieft_col[1]:
        st.write("Aumentó")
        st.altair_chart(donut_chart_greater)
        st.write("Disminuyó")
        st.altair_chart(donut_chart_less)

with col[1]:
    st.markdown("###### Distribución Hurto por Departamento")

    choropleth = make_choropleth(
        df_selected_year, "cod_depto", "log_num_hurtos", selected_color_theme
    )
    st.plotly_chart(choropleth, use_container_width=True)

    st.markdown("###### Heatmap")

    heatmap = make_heatmap(
        auto_df, "año", "departamento", "log_num_hurtos", selected_color_theme
    )
    st.plotly_chart(heatmap, use_container_width=True)

with col[2]:
    st.markdown("###### Comportamiento Anual del Hurto")

    linechart = make_linechart_month(df_selected_month)
    st.plotly_chart(linechart, use_container_width=True)

    st.markdown("###### Top 10 del Año")

    st.dataframe(
        df_selected_year_sorted,
        column_order=("departamento", "num_hurtos"),
        hide_index=True,
        width=None,
        column_config={
            "departamento": st.column_config.TextColumn(
                "Departamento",
            ),
            "num_hurtos": st.column_config.ProgressColumn(
                "Num Hurtos",
                format="%f",
                min_value=0,
                max_value=max(df_selected_year_sorted.num_hurtos),
            ),
        },
    )


#######################
# Copyright
final_col = st.columns((1), gap="small", border=False)
oscar_data = "Creado por: [Oscar Lacheros](https://www.linkedin.com/in/oscarosvaldolancherosromero-a2b87363) | Ciencia de Datos | UCompensar | :copyright: 2025"
with final_col[0]:
    st.markdown(oscar_data, unsafe_allow_html=True)
