from dash import html, register_page

register_page(__name__, path="/", name="Home")

layout = html.Div([
    html.H1("Home"),
    html.P("TODO: Populate Home page")
])
