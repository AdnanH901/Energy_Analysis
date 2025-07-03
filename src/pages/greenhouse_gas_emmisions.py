from dash import html, dcc, register_page, Input, Output, callback, no_update
import pandas as pd
import plotly.express as px
from pages.electricity_mix import countries
import dash_bootstrap_components as dbc

register_page(__name__, path="/greenhouse_gas_emmisions", name="Green House Gas Emissions")

# Load and preprocess data
df = pd.read_csv("data/greenhouse_gas_data.csv")
df["GGE_per_PEC"] = 1000 * df["greenhouse_gas_emissions"] / df["primary_energy_consumption"]  # Measured in kg/MWh
# Group by year and compute percentile rank within each year
df['pct_rank'] = (
    df.groupby('year')['GGE_per_PEC']
      .rank(pct=True)
      .fillna(0)  # Optional: replace NaNs with 0
)
df['pct_rank'] = 100*(1-df['pct_rank'])

# Layout
layout = html.Div([
    html.Div([
        html.H1("Green House Gas Emissions", style={"color": "white"}),

        html.Div([
            html.Label(html.B("Line Graph:"), style={"color": "#ffffff", "marginRight": "10px"}),
            dcc.Dropdown(
                id='country-dropdown-gge',
                options=[{'label': country, 'value': country} for country in countries],
                value='United Kingdom',
                placeholder="Select Country",
                style={"width": "180px", "height": "37.5px", "marginRight": "1rem","backgroundColor": "#000000", "color": "#ffffff"}
            ),
            html.Label(html.B("Scatter Plot:"), style={"color": "#ffffff", "marginRight": "10px"}),
            dcc.Dropdown(
                id='year-dropdown-gge',
                options=[{'label': year, 'value': year} for year in range(2000, 2021)],
                value=2020,
                placeholder="Select Year",
                style={
                    "width": "200px", 
                    "height": "37.5px",
                    "color": "#ffffff", 
                    "backgroundColor": "#000000",
                }
            ),
        ], style={
            "display": "flex",
            "alignItems": "center"
        }),
    ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"}),

    html.Br(),
    html.H2("Emissions Intensity per Energy Produced", style={"color": "white"}),

    html.Div([
        # Graph (Left Side)
        html.Div([
            dcc.Graph(
                id='carbon-intensity-per-energy-produced',
                style={'width': '100%', 'height': '100%'}
            )
        ], style={
            "width": "70%",
            "padding": "20px",
            "boxSizing": "border-box",
            "flexShrink": "0"
        }),

        # Description Text (Right Side)
        html.Div([
            html.P(
                """
                This graph illustrates the amount of greenhouse gases emitted per megawatt-hour (MWh) of energy produced
                also known as EIEP. In other words, for every hour that passes, how many kilograms of greenhouse gases 
                must be emitted to produce 1 MW of electricity? For reference, 1 MW can power a typical U.S. household 
                for an entire month. Ideally, countries should aim to keep their EIEP values low. Countries with consistently 
                high EIEP may present significant opportunities for energy saving and efficiency focused companies.
                """,
                style={"color": "lightgray",}
            )
        ], style={
            "width": "30%",
            "padding": "20px",
            "marginTop": "10px",
            "boxSizing": "border-box",
            "flexShrink": "0"
        }),
    ], style={
        'display': 'flex',
        'justifyContent': 'center',
        'alignItems': 'flex-start',
        'width': '100%',
        'marginTop': '10px',
        "marginLeft": "-15px"
    }),
    html.Div([
        html.H2("Key Insights", style={"color": "white"}),
        html.Div(style={"height": '16px'}),
        html.Div([
            """
            The data shows many countries with varying EIEP levels. Here is a breakdown of interesting EIEP levels from different 
            countries.
            """,
            html.Ul([
                html.Div(style={"height": "15px"}),
                html.Li(
                    """
                    Countries with very low EIEP levels are Albania, Iceland, Switzerland, and Norway. This is interesting as these are 
                    countries that utilise more renewable energy which makes sense as countries that use cleaner energy extraction methods 
                    will have produce less greenhouse gas emissions when generating energy.
                    """
                ),
                html.Div(style={"height": "5px"}),
                html.Li(
                    """
                    Countries with very high EIEP levels include North Macedonia, Montenegro, Moldova, Cyprus and Serbia. These countries 
                    are all relatively young and need a short-term solution to their energy needs. Dirty energy is optimal for these 
                    countries due to lack of infrastructure, and initial and upkeeping costs.
                    """
                ),
                html.Div(style={"height": "5px"}),
                html.Li(
                    """
                    Countries where they originally had high levels of EIEP but have decreased EIEP levels substantially overtime are Estonia, Greece and 
                    Denmark.
                    """
                ),
            ]),
            """
            EIEP offers a simple, powerful metric to gauge how green a country's electricity production is. Countries with lower EIEP are 
            further along in the clean energy transition, while high-EIEP countries are at risk of being left behind both environmentally 
            and economically.
            """
        ],
        style={
            "color": "lightgray",
            "marginLeft": "20px",
            "marginRight": "20px"
        })
    ]),
    
    html.Div([
        dcc.Graph(id="scatter-plot", style={"width": "200%", "overflowX": "auto"}),
        html.Div([
            html.Div(
                html.B("EEIP Percentile"), 
                style={
                    "fontSize": "12.5px",
                    "whiteSpace": "nowrap",
                    "writingMode": "vertical-rl",
                    "transform": "rotate(270deg)",
                    "textAlign": "center",
                }
            ),
            dcc.Slider(
                0, 100, 1,
                id="gge-percentile-slider",
                value=100,
                marks=None,
                vertical=True,
                tooltip={
                    "always_visible": True,
                    "template": "{value}%",
                    "placement": "left"
                },
            )
        ],
        style={
            "height": "400px",
            "marginRight": "20px",
            "marginTop": "-200px"
        })
    ], style={"display": "flex", "align-items": "center",})


])

@callback(
    Output('carbon-intensity-per-energy-produced', 'figure'),
    Input('country-dropdown-gge', 'value')
)
def update_emmisions_intensity(selected_country):
    if selected_country is None:
        return no_update

    data = df[(df["country"] == selected_country) & (df["year"] < 2021) & (df["year"] >= 2000)]

    fig = px.line(data, x='year', y='GGE_per_PEC', markers=True)
    fig.update_layout(
        title=f"<b>Emissions Intensity per Energy Produced</b> (kg/MWh) for {selected_country}",
        xaxis_title="Year",
        yaxis_title="",
        template="plotly_dark",
        legend_title_text=None,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        
        # Background color
        plot_bgcolor="#000000",   # Plot area (behind the data)
        paper_bgcolor="#000000",  # Full figure background

        # Remove grid lines
        # xaxis=dict(showgrid=False),
        # yaxis=dict(showgrid=False),
    )
    fig.update_traces(line=dict(color='#ff402f'))
    return fig

@callback(
    Output('scatter-plot', 'figure'),
    Input('year-dropdown-gge', 'value'),
    Input('gge-percentile-slider', 'value')
)
def update_scatter_plot(selected_year, percentile):
    if selected_year is None:
        return no_update

    data = df[(df["year"] == selected_year) & (df["pct_rank"] <= percentile)]
    
    # Pre-format the data for custom hovertemplate
    data["EEIP_formatted"] = data["GGE_per_PEC"].round(2)
    data["GDP_formatted"] = "£" + data["gdp"].apply(lambda x: f"{x:,.2f}")
    data["population_formatted"] = data["population"].apply(lambda x: f"{int(x):,}")

    fig = px.scatter(
        data, 
        x="country", 
        y="GGE_per_PEC", 
        color="GGE_per_PEC",
        # size="GGE_per_PEC",
        hover_name="country",
        custom_data=["country", "iso_code", "population_formatted", "GDP_formatted", "EEIP_formatted"],
        title=f"EEIP in year {selected_year} (kg/MWh)"
    )
    
    fig.for_each_trace(lambda t: t.update(
        hovertemplate=t.hovertemplate
        .replace("country=", "Country: ")
        .replace("population=", "Population: ")
        .replace("iso_code=", "ISO Code: ")
        .replace("gdp=", "GDP: ")
        .replace("GGE_per_PEC=", "EEIP: ")
    ))

    # Define a custom hovertemplate
    fig.update_traces(
        hovertemplate=(
            "Country: %{customdata[0]}<br>" +
            "ISO Code: %{customdata[1]}<br>" +
            "Population: %{customdata[2]}<br>" +
            "GDP: %{customdata[3]}<br>" +
            "EEIP: %{customdata[4]} kg/MWh<extra></extra>"
        )
    )
    
    fig.update_layout(
        showlegend=False,
        template="plotly_dark",
        xaxis_title="Country",
        yaxis_title="EEIP (kg/MWh)",
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        xaxis_tickangle=45,
        height=600
    )

    fig.update_coloraxes(showscale=False)

    return fig