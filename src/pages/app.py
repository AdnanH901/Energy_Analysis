import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output


colors = [
    "#ff3333",  # red
    "#cbe2a9",  # pale green
    "#03c1ff",  # light blue
    "#9a56ac",  # purple
    "#6e8dd5",  # steel blue
    "#a9545f",  # muted red-brown
    "#ff9966",  # orange-pink (new)
    "#b5cc7e",  # olive green (new)
    "#3399ff",  # sky blue (new)
    "#c28ecf"   # lavender (new)
]

df = pd.read_csv("data/electricity_energy_comparison.csv")
df["total_renewable_energy_temp"] = df["solar_elec_per_capita"] + df["wind_elec_per_capita"] + df["hydro_elec_per_capita"]
df["total_renewable_energy"] = df["total_renewable_energy_temp"].groupby(df["year"]).rank(pct=True)
df = df[["country", "year", "total_renewable_energy_temp", "total_renewable_energy"]]

def ranked_graph(ranking_metric, time_span, label, upper = False, data: pd.DataFrame = df):
    sorted_df = (
        data.loc[data[time_span] == max(data[time_span])]
        .sort_values(ranking_metric, ascending=False)
    )

    highest = sorted_df[:10]["country"].to_list()
    lowest = sorted_df[-10:]["country"].to_list()
    
    data = (
        data[data["country"].isin(highest)] if upper 
        else data[data["country"].isin(lowest)]
    )
    
    data[ranking_metric] = (
        data[ranking_metric].groupby(data["year"]).rank(pct=True, ascending=False) 
        if upper 
        else
        data[ranking_metric].groupby(data["year"]).rank(pct=True, ascending=True) 
    ).round(1)

    fig, ax = plt.subplots(figsize=(8, 3))  # Preferred
    plt.subplots_adjust(right=0.85)

    if isinstance(data, pd.DataFrame):
        # Group by label (e.g., country) and plot each group's data
        for i, (name, group) in enumerate(data.groupby(label)):
            ax.plot(group[time_span], 
                    group[ranking_metric], 
                    "o-", 
                    color=colors[i % len(colors)],
                    markerfacecolor="white",
                    linewidth=3)
            # Get last year's value for annotation
            last_year = group[time_span].max()
            last_value = group.loc[group[time_span] == last_year, ranking_metric].values[0]
            ax.annotate(name, 
                        xy=(last_year, last_value), 
                        xytext=(last_year + 0.5, last_value), 
                        va="center",
                        color="white")
    else:
        # Original list-of-dict fallback
        for element in data:
            ax.plot(element[time_span], 
                    element[ranking_metric], 
                    "o-", 
                    markerfacecolor="white",
                    linewidth=3)
            ax.annotate(element[label][0], 
                        xy=(element[time_span][-1], element[ranking_metric][-1]), 
                        xytext=(element[time_span][-1] + 0.2, element[ranking_metric][-1]), 
                        va="center")


    ax.set_ylim(1.05, 0.05)


    for spine in ax.spines.values():
        spine.set_visible(False)

    # Alter background color and text.
    fig.patch.set_facecolor('black')
    ax.set_title("Top 10 countries using the lowest levels of renewable energy", fontweight="bold", color="white")

    ax.set_facecolor('black')
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')

    # Set x-axis ticks to every 4 years between 2000 and 2020.
    ax.set_xticks(np.arange(2000, 2021, 4))
    ax.set_yticks(np.arange(0.1, 1.01, 0.1))
    ax.set_yticklabels([f"{int(10*rank)}" for rank in np.arange(0.1, 1.01, 0.1)])

    return plt

def ranked_graph_temp(ranking_metric, time_span, label, upper=False, data: pd.DataFrame = df):
    latest_year = data[time_span].max()
    sorted_df = data.loc[data[time_span] == latest_year].sort_values(ranking_metric, ascending=False)

    highest = sorted_df[:10]["country"].to_list()
    lowest = sorted_df[-10:]["country"].to_list()
    
    data = data[data["country"].isin(highest)] if upper else data[data["country"].isin(lowest)]

    data[ranking_metric] = (
        data[ranking_metric].groupby(data["year"]).rank(pct=True, ascending=not upper)
    ).round(1)

    data["country"] = data["country"].replace({"North Macedonia": "MK"})


    fig = go.Figure()

    circle_size = 13.5

    for i, (name, group) in enumerate(data.groupby(label)):
        group = group.sort_values(time_span)
        fig.add_trace(go.Scatter(
            x=group[time_span],
            y=group[ranking_metric],
            mode='lines+markers+text',
            name=name,
            showlegend=False,
            line=dict(color=colors[i % len(colors)], width=3),
            marker=dict(size=circle_size, color=colors[i % len(colors)], line=dict(color="white", width=1)),
            text=["" for _ in range(len(group)-1)] + [name],
            textposition="middle right",
            textfont=dict(color='white')
        ))


    fig.update_layout(
        height=600,
        title="10 countries consuming the least renewable energy",
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white'),
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(2000, 2021, 4)),
            showgrid=False,
            title='',
            showline=False,
            showticklabels=True,
            ticks='outside',
            tickfont=dict(color='white')
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=np.round(np.arange(0.1, 1.01, 0.1), 1),
            ticktext=[str(int(10 * x)) for x in np.round(np.arange(0.1, 1.01, 0.1), 1)],
            autorange="reversed",
            showgrid=False,
            title='',
            showline=False,
            showticklabels=True,
            ticks='outside',
            tickfont=dict(color='white'),
            
        ),
        grid_xside="top plot"
    )

    return fig

app = Dash(__name__)
app.title = "Renewable Energy Ranking"

app.layout = html.Div(style={'backgroundColor': 'black', 'color': 'white', 'padding': '2rem'}, children=[
    html.H1("Renewable Energy Rankings by Country", style={'textAlign': 'center'}),
    html.Div([
        html.Label("Select Ranking Type:", style={'marginRight': '1rem'}),
        dcc.RadioItems(
            id='ranking-choice',
            options=[
                {'label': 'Top 10 (Most Renewable)', 'value': 'top'},
                {'label': 'Bottom 10 (Least Renewable)', 'value': 'bottom'}
            ],
            value='bottom',
            labelStyle={'display': 'inline-block', 'marginRight': '2rem'},
            style={'color': 'white'}
        )
    ], style={'marginBottom': '2rem', 'textAlign': 'center'}),
    dcc.Graph(id='ranking-graph')
])

@app.callback(
    Output('ranking-graph', 'figure'),
    Input('ranking-choice', 'value')
)
def update_graph(choice):
    upper = True if choice == 'top' else False
    return ranked_graph_temp("total_renewable_energy", "year", "country", upper=upper)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
