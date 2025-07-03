from dash import html, register_page
from io import BytesIO
import base64
import matplotlib.pyplot as plt
from pages.app import ranked_graph as rg

register_page(__name__, path="/renewable_vs_fossil_fuels", name="Renewable VS Fossil Fuel")

# Create figure and return base64-encoded image
def matplotlib_fig_to_base64():
    plt.close('all')  # Clear old figures

    rg("total_renewable_energy", "year", "country", upper=False)

    buf = BytesIO()
    plt.savefig(buf, format="png", facecolor="#000000", bbox_inches='tight')  # Ensure clean background
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return img_base64


layout = html.Div([
    html.H1("Renewable VS Fossil Fuel"),
    html.Div([
        html.Img(src=f"data:image/png;base64,{matplotlib_fig_to_base64()}", id="CVF-rank-chart", style={"width": "100%", "maxWidth": "5000px"}),
    ], className="chart-container", style={"flex": "1"}),

])

