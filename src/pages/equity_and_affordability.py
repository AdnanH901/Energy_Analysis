from dash import html, register_page
import pandas as pd

register_page(__name__, path="/equity_and_affordability", name="Equity & Affordability")

layout = html.Div([
    html.H1("Equity & Affordability"),
    html.P("TODO: Populate Equity & Affordability page")
])
