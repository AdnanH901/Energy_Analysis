import pandas as pd
import numpy as np
import plotly.express as px
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend suitable for script and web rendering
import matplotlib.pyplot as plt

# Load data into pandas dataframe
df1 = pd.read_csv('data/electricity_data.csv')

df1["gas_percentage"] = (100 * df1["gas_electricity"] / df1["total_electricity"] // 1).astype(int)
df1["relative_gas_percentage"] = ((100 * df1["gas_electricity"] / df1["total_dirty_electricity"]).replace([float('inf'), -float('inf')], np.nan).fillna(0) // 1).astype(int)
df1["oil_percentage"] = (100 * df1["oil_electricity"] / df1["total_electricity"] // 1).astype(int)
df1["relative_oil_percentage"] = ((100 * df1["oil_electricity"] / df1["total_dirty_electricity"]).replace([float('inf'), -float('inf')], np.nan).fillna(0) // 1).astype(int)
df1["coal_percentage"] = (100 * df1["coal_electricity"] / df1["total_electricity"] // 1).astype(int)
df1["relative_coal_percentage"] = ((100 * df1["coal_electricity"] / df1["total_dirty_electricity"]).replace([float('inf'), -float('inf')], np.nan).fillna(0) // 1).astype(int)

df1["wind_percentage"] = (100 * df1["wind_electricity"] / df1["total_electricity"] // 1).astype(int)
df1["solar_percentage"] = (100 * df1["solar_electricity"] / df1["total_electricity"] // 1).astype(int)
df1["hydro_percentage"] = (100 * df1["hydro_electricity"] / df1["total_electricity"] // 1).astype(int)
df1["biofuel_percentage"] = (100 * df1["biofuel_electricity"] / df1["total_electricity"] // 1).astype(int)
df1["nuclear_percentage"] = (100 * df1["nuclear_electricity"] / df1["total_electricity"] // 1).astype(int)
df1["low_carbon_percentage"] = (100 * df1["low_carbon_electricity"] / df1["total_electricity"] // 1).astype(int)

clean_ring_colours = [
    "#ADF4A5",  # lightest
    "#89EB6C", 
    "#65D837",  
    "#4CBB17",  
    "#3FAE14", 
    "#2E7D1A",  
    "#1D4F0D",  # darkest
]


dirty_ring_colours = [
    "#ff402f",  # lightest
    "#cc3326",
    "#99261c"   # darkest
]

clean_ring_colours.reverse()
dirty_ring_colours.reverse()


def curved_text(ax, label, radius, angle_range=(-290, -360)):
    chars = list(label)
    n = len(chars)
    angles = np.linspace(np.radians(angle_range[0]), np.radians(angle_range[1]), n)

    for char, angle in zip(chars, angles):
        ax.text(
            angle,
            radius,
            char,
            fontsize=26,
            fontweight='bold',
            color="white",
            ha="center",
            va="center",
            rotation=np.degrees(angle),
            rotation_mode='anchor'
        )

def radial_bar_plotter(country, year, type, mult = 1):

    if not country or not year:
        return  # Or return some default/fallback chart
    
    if type == 'clean':
        clean_energy_dict = {
            'clean_electrical_energy': [
                "wind_electricity",
                "solar_electricity",
                "hydro_electricity",
                "biofuel_electricity",
                "nuclear_electricity",
                "low_carbon_electricity"
            ],

            'percentages': [
                int(df1["wind_percentage"].loc[(df1["year"] == year) & (df1["country"] == country)].values[0]),
                int(df1["solar_percentage"].loc[(df1["year"] == year) & (df1["country"] == country)].values[0]),
                int(df1["hydro_percentage"].loc[(df1["year"] == year) & (df1["country"] == country)].values[0]),
                int(df1["biofuel_percentage"].loc[(df1["year"] == year) & (df1["country"] == country)].values[0]),
                int(df1["nuclear_percentage"].loc[(df1["year"] == year) & (df1["country"] == country)].values[0]),
                int(df1["low_carbon_percentage"].loc[(df1["year"] == year) & (df1["country"] == country)].values[0])
            ],
        }

        df = pd.DataFrame(clean_energy_dict).sort_values(
                by='percentages', 
                ascending=False
        ).reset_index(drop=True)

        ring_labels = [f'   {x.replace('_', ' ').title()} ({v}%) ' for x, v in zip(list(df['clean_electrical_energy']), 
                                                    list(df['percentages']))]
        ring_colours = clean_ring_colours

    else:
        dirty_energy_dict = {
            'dirty_electrical_energy': [
                "gas_electricity",
                "oil_electricity",
                "coal_electricity"
            ],

            'percentages': [
                int(df1["gas_percentage"].loc[(df1["year"] == year) & (df1["country"] == country)].values[0]),
                int(df1["oil_percentage"].loc[(df1["year"] == year) & (df1["country"] == country)].values[0]),
                int(df1["coal_percentage"].loc[(df1["year"] == year) & (df1["country"] == country)].values[0])
            ],

            'relative_percentages': [
                int(df1["relative_gas_percentage"].loc[(df1["year"] == year) & (df1["country"] == country)].values[0]),
                int(df1["relative_oil_percentage"].loc[(df1["year"] == year) & (df1["country"] == country)].values[0]),
                int(df1["relative_coal_percentage"].loc[(df1["year"] == year) & (df1["country"] == country)].values[0])
            ]
        }

        df = pd.DataFrame(dirty_energy_dict).sort_values(
            by='percentages',
            ascending=False
        ).reset_index(drop=True)

        ring_labels = [f'   {x.replace('_', ' ').title()} ({v}%) ' for x, v in zip(list(df['dirty_electrical_energy']), 
                                                    list(df['percentages']))]
        ring_colours = dirty_ring_colours

    max_value_full_ring = max(df['percentages'])

    data_len = len(df)
    # Begin creating the figure
    fig = plt.figure(
        figsize=(10,10), 
        linewidth=10,
        edgecolor='#000000', 
        facecolor='#000000'
    )

    rect = [0.1,0.1,0.8,0.8]

    # Add axis for radial backgrounds
    ax_polar_bg = fig.add_axes(rect, polar=True, frameon=False)
    ax_polar_bg.set_theta_zero_location('N')
    ax_polar_bg.set_theta_direction(1)
        
    # Loop through each entry in the dataframe and plot a grey
    # ring to create the background for each one
    for i in range(data_len):
        ax_polar_bg.barh(
            i,  1.5 * np.pi, 
            color='grey', 
            alpha=0.1
        )
    # Hide all axis items
    ax_polar_bg.axis('off')
        
    # Add axis for radial chart for each entry in the dataframe
    ax_polar = fig.add_axes(rect, polar=True, frameon=False)
    ax_polar.set_theta_zero_location('N')
    ax_polar.set_theta_direction(1)
    ax_polar.set_rgrids(
        [i for i in range(len(ring_labels))], 
        labels=ring_labels, 
        angle=0, 
        fontsize=14, 
        fontweight='bold',
        color='white', 
        verticalalignment='center'
    )

    # Loop through each entry in the dataframe and create a coloured 
    # ring for each entry
    for i in range(data_len):
        if i == 0:
            ax_polar.barh(i, list(df['percentages'])[i]*1.5*np.pi/(max_value_full_ring if max_value_full_ring != 0 else 1), 
                    color=ring_colours[i])
        else:
            ax_polar.barh(i, list(df['percentages'])[i]*mult*1.5*np.pi/(max_value_full_ring if max_value_full_ring != 0 else 1), 
                    color=ring_colours[i])
    
    ax_polar.grid(False)
    ax_polar.tick_params(
        axis='both', 
        left=False, 
        bottom=False, 
        labelbottom=False, 
        labelleft=True
    )

    # Add curved title above the radial chart
    label_radius = data_len + 0.5  # A bit beyond the last ring
    if type == "clean":
        curved_text(ax_polar, "Clean Energy Sources", radius=label_radius)
    elif type == "dirty":
        curved_text(ax_polar, "Dirty Energy Sources", radius=label_radius)


