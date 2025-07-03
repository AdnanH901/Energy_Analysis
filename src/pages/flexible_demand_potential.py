from dash import html, register_page, dcc, callback, Output, Input, dcc, no_update
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler
from pages.electricity_mix import geojson_europe, geojson_usa, countries, display_choropleth

temp = countries.copy()
temp.remove("United States")

EU_USA = pd.read_csv("data/EU_USA_data.csv")

scoring_data = EU_USA[["country", "year", "carbon_intensity_elec", "per_capita_electricity", "fossil_share_elec", "renewables_share_elec"]]
normalized_data = scoring_data[["country", "year"]].copy(deep=True)

# Select the features you want to normalize
features_to_normalize = ["carbon_intensity_elec", "per_capita_electricity", "fossil_share_elec", "renewables_share_elec"]

# Create a new DataFrame with country and year preserved
normalized_data = scoring_data[["country", "year"]].copy(deep=True)

# Initialize the scaler
scaler = MinMaxScaler()

# Fit-transform the data and add normalized columns to the new DataFrame
normalized_values = scaler.fit_transform(scoring_data[features_to_normalize])

# Add normalized columns with _norm suffix
for i, col in enumerate(features_to_normalize):
    normalized_data[f"{col}_norm"] = normalized_values[:, i]

# Insert subjectively "Positive" columns.
normalized_data["per_capita_electricity_norm"] = 1 - normalized_data["per_capita_electricity_norm"]
normalized_data["renewables_share_elec_norm"] = 1 - normalized_data["renewables_share_elec_norm"]

normalized_data["market_demand_score"] = 100 * (
    normalized_data["carbon_intensity_elec_norm"] * 0.325 +
    normalized_data["per_capita_electricity_norm"] * 0.325 +
    normalized_data["fossil_share_elec_norm"] * 0.2 +
    normalized_data["renewables_share_elec_norm"] * 0.15
)

def scoring_label(row):
    if row["market_demand_score"] >= 75:
        return "High Potential"
    elif row["market_demand_score"] >= 50:
        return "Moderate Potential"
    elif row["market_demand_score"] >= 25:
        return "Low-Medium Potential"
    else:
        return "Low Potential"
    
register_page(__name__, path="/flexible_demand_potential", name="Flexible Demand Potential", suppress_callback_exceptions=True)

layout = html.Div([
    html.Div([
        html.H1("Global Market Demand Potential", style={"margin": 0}),

        html.Div([
            html.Label(html.B("Line Graph:"), style={"color": "#ffffff", "marginRight": "10px"}),
            dcc.Dropdown(
                id='country-line-graph-dropdown',
                options=[
                    {'label': country, 'value': country} for country in countries
                ],
                value='United Kingdom',
                placeholder="Select Country",
                style={"width": "180px", "marginRight": "1rem", "color": "#ffffff"}
            ),
            html.Label(html.B("Choropleth Map:"), style={"color": "#ffffff", "marginRight": "10px"}),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': country, 'value': country} for country in countries],
                value=countries,  # Default value
                multi=True,
                placeholder="Select Country",
                style={
                    "width": "200px", 
                    "height": "37.5px",
                    "color": "#ffffff", 
                    "backgroundColor": "#000000",
                    'overflowY': 'scroll'
                }
            ),
        ], style={
            "display": "flex",
            "alignItems": "center"
        }),
    ],
    style={
        "display": "flex",
        "justifyContent": "space-between",
        "alignItems": "center",
        "padding": "10px 20px",
        "marginBottom": "15px"
    }),
    html.Br(),
    html.Div([
        dcc.Graph(id="country-line-graph", style={'width': '100%'})
    ], style={'display': 'center', 'justifyContent': 'center', 'marginTop': '50px', 'width': '100%'}),
    html.Br(),
    html.Div([
        dcc.Graph(id="side-graph", style={'display': 'none'}),
        dcc.Graph(id="default-market-potential-globe", style={'width': '100%', 'display': 'inline-block'}),
    ], style={'display': 'flex', 'justifyContent': 'space-between'}),
    html.Br(), html.Br(), html.Br(),
    html.Div([
        dcc.Slider(id='year-slider', min=2000, max=2020,
            step=1, value=2020, included=True, updatemode='drag',
            marks={str(year): {'label':None, 'style': {'color': '#ffffff'}} for year in range(2000, 2021, 4)},
            tooltip={"placement": "bottom", "always_visible": True},
        )
    ], style={'padding': '0px 20px', 'color': '#333333'})
])

@callback(
    Output("default-market-potential-globe", "figure"),
    Output("side-graph", "figure"),
    Input("country-dropdown", "value"),
    Input("year-slider", "value")
)
def display_choropleth_temp(countries, year):
    fig = display_choropleth(normalized_data, countries, year, "market_demand_score", "country", multi=True)
    fig_USA = display_choropleth(normalized_data, countries, year, "market_demand_score", "country", multi=True, USA_toggle=True)

    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Market Potential (%)",
            orientation="v",  # vertical colorbar
            ticklabelposition="outside bottom",
            tickfont=dict(size=12),
        )
    )
    fig.update_coloraxes(cmin=0, cmax=100)

    fig.update_layout(
        coloraxis_colorbar=dict(
            title=dict(
                text="Market Potential (%)",
                font=dict(
                    color='#ffffff'
                )
            ),
            orientation="v",  # vertical colorbar
            ticklabelposition="outside bottom",
            tickfont=dict(size=12, color='#ffffff'),
        )
    )
    fig_USA.update_coloraxes(cmin=0, cmax=100)

    if "United States" in countries and len(countries) > 1:
        return (fig, fig_USA)
    elif "United States" in countries and len(countries) == 1:
        return (fig, fig_USA)
    else:
        return (fig, no_update)
    
@callback(
    Output("country-line-graph", "figure"),
    Input("country-line-graph-dropdown", "value"),
)
def update_line_graph(selected_country):
    if selected_country is None:
        return no_update

    country_data = normalized_data[(normalized_data["country"] == selected_country) & (normalized_data["year"] < 2021)]

    fig = px.line(country_data, x='year', y='market_demand_score', markers=True)
    fig.update_layout(
        title=f"Market Potential for {selected_country}",
        xaxis_title="Year",
        yaxis_title="Market Potential (%)",
        template="plotly_dark",
        height=400,
        width=1375,
        legend_title_text=None,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        
        # Background color
        plot_bgcolor="#000000",   # Plot area (behind the data)
        paper_bgcolor="#000000",  # Full figure background
    )
    fig.update_traces(line=dict(color='#03c1ff'))
    return fig
    
@callback(
    Output("side-graph", "style"),
    Output("default-market-potential-globe", "style"),
    Input("country-dropdown", "value"),
)
def toggle_side_graph(countries):
    if "United States" in countries and len(countries) > 1:
        return {'display': 'block'}, {'width': '51.5%', 'display': 'inline-block'}
    else:
        return {'display': 'none'}, {'width': '100%', 'display': 'inline-block'}
