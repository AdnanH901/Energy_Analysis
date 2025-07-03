import pandas as pd
from dash import Dash, html, page_container
import dash_bootstrap_components as dbc
from pycountry import countries

# Initialize the Dash app with Dash Pages enabled
app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.FONT_AWESOME,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css",
    ],
)

# Sidebar layout
sidebar = html.Div(
    [
        html.Div(
            [
                html.Img(src="/assets/hayaul_logo.png", style={"width": "3rem"}),
                html.H2("Hayat-Al", style={"color": "white"}),
            ],
            className="sidebar-header",
        ),
        html.Hr(style={"color": "white", "margin": "1rem 0", "border": "1px solid white"}),
        dbc.Nav(
            [
                dbc.NavLink(
                    [html.I(className="fas fa-home me-2"), html.Span("Home", style={"color": "white"})],
                    href="/",
                    active="exact",
                ),
                dbc.NavLink(
                    [html.I(className="fa fa-leaf me-2"), html.Span("Green House Gas Emissions", style={"color": "white"})],
                    href="/greenhouse_gas_emmisions",
                    active="exact",
                ),
                dbc.NavLink(
                    [html.I(className="bi bi-fuel-pump-fill me-2"), html.Span("Renewable VS Fossil Fuel", style={"color": "white"})],
                    href="/renewable_vs_fossil_fuels",
                    active="exact",
                ),
                dbc.NavLink(
                    [html.I(className="bi bi-lightning-fill me-2"), html.Span("Electricity Mix", style={"color": "white"})],
                    href="/electricity_mix",
                    active="exact",
                ),
                dbc.NavLink(
                    [html.I(className="bi bi-cash-stack me-2"), html.Span("Equity & Affordability", style={"color": "white"})],
                    href="/equity_and_affordability",
                    active="exact",
                ),
                dbc.NavLink(
                    [html.I(className="fa-solid fa-magnifying-glass-chart me-2"), html.Span("Flexible Demand Potential", style={"color": "white"})],
                    href="/flexible_demand_potential",
                    active="exact",
                ),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    className="sidebar",
)

# Main app layout using Dash Pages
app.layout = html.Div([
    sidebar,
    html.Div(page_container, className="content")
])

if __name__ == "__main__":
    app.run(debug=True)