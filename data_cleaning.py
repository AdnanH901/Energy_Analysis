import pandas as pd
from IPython.display import display
from os import path

original_data = pd.read_csv('data/WorldEnergyConsumption.csv')

# Countries relevant to Axle's business goals.
countries = [
    "Albania", "Armenia", "Austria", 
    "Belarus", "Belgium", "Bulgaria", 
    "Croatia", "Cyprus", 
    "Denmark", 
    "Estonia", 
    "Finland", "France", 
    "Georgia", "Germany", "Greece", 
    "Hungary", 
    "Iceland", "Ireland", "Italy", 
    "Latvia", "Lithuania", "Luxembourg", 
    "Moldova", "Montenegro", 
    "Netherlands", "North Macedonia", "Norway", 
    "Poland", "Portugal", 
    "Romania", "Russia", 
    "Serbia", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", 
    "Turkey", 
    "Ukraine", "United Kingdom", "United States" 
]


##### ELECTRICITY DATA CLEANING #####
clean_electricity_columns = [
    "biofuel_electricity",
    "hydro_electricity",
    "low_carbon_electricity",
    "nuclear_electricity",
    "solar_electricity",
    "wind_electricity"
]

dirty_electricity_columns = [
    "coal_electricity",
    "gas_electricity",
    "oil_electricity"
]

aggregate_electricity_data = [
    "country", 
    "year", 
    "electricity_generation" 
]

electricity_columns = clean_electricity_columns + dirty_electricity_columns

# Filter and clean the original data.
electricity_data = (
    original_data[aggregate_electricity_data + clean_electricity_columns + dirty_electricity_columns]
    .loc[(original_data['country'].isin(countries)) & (original_data['year'] < 2022) & (original_data['year'] >= 2000)].copy(deep=True)
)
electricity_data.fillna(0, inplace=True)

electricity_data["total_electricity"] = electricity_data[electricity_columns].sum(axis=1)

# sum all values pertaining to clean and dirty electricity seperately
electricity_data["total_clean_electricity"] = electricity_data[[
    "biofuel_electricity", 
    "hydro_electricity", 
    "low_carbon_electricity", 
    "nuclear_electricity", 
    "solar_electricity", 
    "wind_electricity"
]].sum(axis=1)

electricity_data["total_dirty_electricity"] = electricity_data[[
    "coal_electricity",
    "gas_electricity",
    "oil_electricity"
]].sum(axis=1)

# Count the number of missing values in each column.
missing_values = electricity_data.isnull().sum()

# configure print to show all columns
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

##### END OF ELECTRICITY DATA CLEANING #####





##### GREENHOUSE GAS EMISSIONS DATA CLEANING #####
# Filter the original data for greenhouse gas emissions.
greenhouse_gas_columns = [
    "country", 
    "iso_code",
    "year", 
    "population",
    "gdp",
    "greenhouse_gas_emissions", 
    "primary_energy_consumption",
    "energy_per_gdp", # Primary energy consumption per GDP
]

greenhouse_gas_data = (
    original_data[greenhouse_gas_columns]
    .loc[(original_data['country'].isin(countries)) & (original_data['year'] < 2021) & (original_data['year'] >= 2000)].copy(deep=True)
)

### GET GDP PER CAPITA DATA ###
# Load the original CSV file
gdp_per_country_temp = pd.read_csv("data/GDPpc.csv")

# Extract metadata
region_row = gdp_per_country_temp.iloc[0]  # First row contains region info
code_row = gdp_per_country_temp.iloc[1]    # Second row contains country codes

# Extract GDP data starting from row 2
gdp_data = gdp_per_country_temp.iloc[2:].copy()
gdp_data.columns = region_row.index  # Use the original column names
gdp_data.rename(columns={gdp_data.columns[0]: 'Year'}, inplace=True)

# Convert to long format
gdp_per_country = gdp_data.melt(id_vars='Year', var_name='Country', value_name='GDP_per_capita')

# Add metadata: region and country code
gdp_per_country['Region'] = gdp_per_country['Country'].map(region_row)
gdp_per_country['Country_Code'] = gdp_per_country['Country'].map(code_row)

# Clean data types
gdp_per_country['Year'] = gdp_per_country['Year'].astype(int)
gdp_per_country['GDP_per_capita'] = gdp_per_country['GDP_per_capita'].replace({',': ''}, regex=True).astype(float)
gdp_per_country['GDP_per_capita'] *= 0.62 # Conversion rate from international $ to GBP £ in 2011.
gdp_per_country = gdp_per_country[['Year', 'Country', 'GDP_per_capita']]

# Chnage country with name "Russian Federation" to "Russia" and "TFYR of Macedonia" to "North Macedonia" and "Republic of Moldova" to "Moldova"
gdp_per_country['Country'] = gdp_per_country['Country'].replace("Russian Federation", "Russia")
gdp_per_country['Country'] = gdp_per_country['Country'].replace("TFYR of Macedonia", "North Macedonia")
gdp_per_country['Country'] = gdp_per_country['Country'].replace("Republic of Moldova", "Moldova")

### END OF GET GDP PER COUNTRY DATA ###

# Merge GDP per capita data with greenhouse gas data.
greenhouse_gas_data = pd.merge(
    greenhouse_gas_data, gdp_per_country, 
    how='left', 
    left_on=['year', 'country'], 
    right_on=['Year', 'Country']
)
greenhouse_gas_data.drop(columns=['Year', 'Country'], inplace=True)

greenhouse_gas_data["gdp"] = greenhouse_gas_data["GDP_per_capita"] * greenhouse_gas_data["population"]
greenhouse_gas_data["energy_per_gdp"] = greenhouse_gas_data["primary_energy_consumption"] / greenhouse_gas_data["gdp"] # accurate stand in for energy_per_gdp
greenhouse_gas_data.fillna(0)

##### END OF GREENHOUSE GAS EMISSIONS DATA CLEANING  #####





##### RENEWABLES VS FOSSIL FUEL DATA CLEANING #####

elec_energy_consumption_columns = ['country', 'year'] + [
    f"{energy_type}_elec_per_capita" for energy_type in ['solar', 'wind', 'hydro', 'coal', 'oil', 'gas']
]

elec_energy_comparison = (
    original_data[elec_energy_consumption_columns]
    .loc[(original_data['country'].isin(countries)) & (original_data['year'] < 2021) & (original_data['year'] >= 2000)].copy(deep=True)
)

##### END OF RENEWABLES VS FOSSIL FUEL DATA CLEANING #####





##### ENERGY AFFORDABILITY & EQUITY DATA CLEANING #####

columns = [
    'country', 'year',
    'energy_per_capita', # Primary energy consumption per capita - Measured in kilowatt-hours per person.
    "energy_per_gdp", # Primary energy consumption per GDP - Measured in kilowatt-hours per international-$.

    "population",
    "primary_energy_consumption",
]

#energy_affordability_and_equity 
energy_affordability_and_equity = (
    original_data[columns]
    .loc[(original_data['country'].isin(countries)) & (original_data['year'] < 2021) & (original_data['year'] >= 2000)].copy(deep=True)
)

energy_affordability_and_equity = pd.merge(
    energy_affordability_and_equity, gdp_per_country, 
    how='left', 
    left_on=['year', 'country'], 
    right_on=['Year', 'Country']
)

df = energy_affordability_and_equity

energy_affordability_and_equity["gdp"] = energy_affordability_and_equity["GDP_per_capita"] * energy_affordability_and_equity["population"]
energy_affordability_and_equity["energy_per_gdp"] = (
    energy_affordability_and_equity["primary_energy_consumption"] # Measured in TWh
    / energy_affordability_and_equity["gdp"] # Meausred in GBP £
) # accurate stand in for energy_per_gdp
energy_affordability_and_equity.fillna(0)

##### END OF ENERGY AFFORDABILITY & EQUITY DATA CLEANING #####

# Save the cleaned data to a CSV file if it doesn't already exist.
if not path.exists('data/electricity_data.csv'):
    electricity_data.to_csv('data/electricity_data.csv', index=False)

if not path.exists('data/EU_USA_data.csv'):
    EU_USA_data = original_data.loc[(original_data['country'].isin(countries)) & (original_data['year'] < 2021) & (original_data['year'] >= 2000)].copy(deep=True)
    EU_USA_data.to_csv('data/EU_USA_data.csv', index=False)

if not path.exists('data/greenhouse_gas_data.csv'):
    greenhouse_gas_data.to_csv('data/greenhouse_gas_data.csv', index=False)

if not path.exists('data/electricity_energy_comparison.csv'):
    elec_energy_comparison.to_csv('data/electricity_energy_comparison.csv', index=False)

if not path.exists('data/energy_affordability_and_equity.csv'):
    energy_affordability_and_equity.to_csv('data/energy_affordability_and_equity.csv', index=False)