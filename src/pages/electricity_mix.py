# pages/em.py
from dash import html, dcc, register_page, callback, Output, Input, no_update
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
from pages.radial_bar import radial_bar_plotter as rbp
import json

with open("data/europe_countries.geojson") as f:
    geojson_europe = json.load(f)
with open("data/USA.geojson") as f:
    geojson_usa = json.load(f)

# Countries relevant to Axle's business goals.
countries = [
    "Albania", "Armenia", "Austria", "Azerbaijan", 
    "Belarus", "Belgium", "Bulgaria", 
    "Croatia", "Cyprus", 
    "Denmark", 
    "Estonia", 
    "Finland", "France", 
    "Georgia", "Germany", "Greece", 
    "Hungary", 
    "Iceland", "Ireland", "Italy", 
    "Kazakhstan", "Kosovo", 
    "Latvia", "Lithuania", "Luxembourg", 
    "Moldova", "Montenegro", 
    "Netherlands", "North Macedonia", "Norway", 
    "Poland", "Portugal", 
    "Romania", "Russia", 
    "Serbia", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", 
    "Turkey", 
    "Ukraine", "United Kingdom", "United States" 
]


def electricity_mix_label(row):
    if abs(row["total_clean_electricity"] - row["total_dirty_electricity"]) < 1:
        return "Equal"
    elif row["total_clean_electricity"] > row["total_dirty_electricity"]:
        return "Clean"
    elif row["total_clean_electricity"] < row["total_dirty_electricity"]:
        return "Dirty"
    else:
        return "Unknown"

def display_choropleth(df, country_selection, year, color_column, locations_column, multi=False, USA_toggle=False):
    color = "#00008B"
    plt.close()

    if not multi and "United States" == country_selection or multi and "United States" in country_selection and len(country_selection) == 1:
        fig = px.choropleth_map(
            df.loc[(df['year'] == year) & (df['country'].isin(countries))]
            if not multi else
            df.loc[(df['year'] == year) & (df['country'].isin(country_selection))],
            geojson=geojson_usa,
            color=color_column,
            color_continuous_scale=["#deebf7", color] if multi else None,
            color_discrete_map=label_to_color if not multi else None,
            locations=locations_column,
            featureidkey="properties.NAME",
            map_style="carto-darkmatter",
            center={"lat": 54.5, "lon": -119},
            zoom=2,
        )
    elif not multi and "United States" != country_selection or multi and not "United States" in country_selection:
        fig = px.choropleth_map(
            df.loc[(df['year'] == year) & (df['country'].isin(countries))]
            if not multi else
            df.loc[(df['year'] == year) & (df['country'].isin(country_selection))],
            geojson=geojson_europe,
            color=color_column,
            color_continuous_scale=["#deebf7", color] if multi else None,
            color_discrete_map=label_to_color if not multi else None,
            locations=locations_column,
            featureidkey="properties.NAME",
            map_style="carto-darkmatter",
            center={"lat": 54.908, "lon": -17.316},
            zoom=2.5,
        )
    elif multi and "United States" in country_selection and not USA_toggle:
        fig = px.choropleth_map(
            df.loc[(df['year'] == year) & (df['country'].isin(country_selection))],
            geojson=geojson_europe,
            color=color_column,
            color_continuous_scale=["#deebf7", color],
            locations=locations_column,
            featureidkey="properties.NAME",
            map_style="carto-darkmatter",
            center={"lat": 56.5, "lon": 12},
            zoom=2.15,
        )

    else:
        fig = px.choropleth_map(
            df.loc[(df['year'] == year) & (df['country'].isin(country_selection))],
            geojson=geojson_usa,
            color=color_column,
            color_continuous_scale=["#deebf7", color],
            locations=locations_column,
            featureidkey="properties.NAME",
            map_style="carto-darkmatter",
            center={"lat": 54.5, "lon": -119},
            zoom=2,
        )

        fig.update_layout(
            showlegend=None,  # Hides the entire legend
            coloraxis_showscale=False,
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            paper_bgcolor="black",
            plot_bgcolor="black",
            autosize=False,
            width=625,
        )
        return fig

    fig.update_layout(
        autosize=True,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        legend=dict(
            title_text="",           # Remove "winner"
            bgcolor="black",         # Legend background
            font=dict(color="white") # Legend text color
        ),
        paper_bgcolor="black",       # Whole figure background
        plot_bgcolor="black"         # Plot area background
    )

    return fig

label_to_color = {
    "Clean": "#4CBB17",
    "Dirty": "#FF5733",
    "Equal": "#03c1ff",
    "Unknown": "#ffffff"
}


electricity_data = pd.read_csv('data/electricity_data.csv')  # Load your cleaned electricity data
electricity_data["electricity_mix_label"] = electricity_data.apply(electricity_mix_label, axis=1)
electricity_data["country_color"] = electricity_data["electricity_mix_label"].map(label_to_color)
register_page(__name__, path="/electricity_mix", name="Electricity Mix")

# Create figure and return base64-encoded image
def matplotlib_fig_to_base64(category, country=None, year=None):
    plt.close('all')  # Clear old figures

    rbp(country, year, category)  # Call your radial bar function

    buf = BytesIO()
    plt.savefig(buf, format="png", facecolor="#000000", bbox_inches='tight')  # Ensure clean background
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return img_base64

#### WEBPAGE LAYOUT ####

layout = html.Div([
    html.Div([
        html.H1("Electricity Production Share", style={"color": "white"}),

        html.Div([
            dcc.Dropdown(
                id='country-dropdown',
                options=[
                    {'label': country, 'value': country} for country in countries
                ],
                value='United Kingdom',
                placeholder="Select Country",
                style={"width": "180px", "marginRight": "1rem", "color": "#ffffff"}
            ),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(y), 'value': y} for y in range(2000, 2021)],
                value=2020,
                placeholder="Select Year",
                style={"width": "120px",}
            ),
        ], style={"display": "flex", "marginLeft": "auto"})  # Pushes dropdowns to the right
    ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"}),

    html.Div([
        html.Div([
            html.Img(src=None, id="clean-energy-chart", style={"width": "100%", "maxWidth": "500px"}),
        ], className="chart-container", style={"flex": "1"}),

        html.Div([
            html.Img(src=None, id="dirty-energy-chart", style={"width": "100%", "maxWidth": "500px"}),
        ], className="chart-container", style={"flex": "1"}),
    ], style={"display": "flex", "justifyContent": "center", "alignItems": "center", "flexWrap": "wrap"}),

    dcc.Graph(id="geospatial-graph")

], style={"backgroundColor": "black", "padding": "2rem"})



@callback(
    Output("clean-energy-chart", "src"),
    Output("dirty-energy-chart", "src"),
    Input("country-dropdown", "value"),
    Input("year-dropdown", "value")
)
def update_radial_charts(selected_country, selected_year):
    img_clean = matplotlib_fig_to_base64("clean", selected_country, selected_year)
    img_dirty = matplotlib_fig_to_base64("dirty", selected_country, selected_year)

    return f"data:image/png;base64,{img_clean}", f"data:image/png;base64,{img_dirty}"

@callback(
    Output("geospatial-graph", "figure"),
    Input("country-dropdown", "value"),
    Input("year-dropdown", "value")
)
def display_choropleth_map_temp(country, year):
    fig = display_choropleth(electricity_data, country, year, "electricity_mix_label", "country")
    return fig