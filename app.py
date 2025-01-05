from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import pycountry_convert as pc

# Initialize the Dash app
app = Dash(__name__)

# Load the data
df_orig = pd.read_csv("data/ref_country_orig.csv")
df_asylm = pd.read_csv("data/ref_country_asylm.csv")

# Melt the data to convert wide format to long format
df_orig = df_orig.melt(id_vars=["country"], var_name="Year", value_name="Refugees_origin")
df_asylm = df_asylm.melt(id_vars=["country"], var_name="Year", value_name="Refugees_asylum")

# Convert 'Year' column to integer
df_orig["Year"] = df_orig["Year"].astype(int)
df_asylm["Year"] = df_asylm["Year"].astype(int)

# Drop rows with NaN values in 'Refugees'
df_orig.dropna(subset=["Refugees_origin"], inplace=True)
df_asylm.dropna(subset=["Refugees_asylum"], inplace=True)

# Merge the datasets on 'country' and 'Year'
df_combined = pd.merge(df_orig, df_asylm, on=["country", "Year"], how="inner")

# Map regions dynamically
def get_region(country_name):
    try:
        alpha2 = pc.country_name_to_country_alpha2(country_name)
        continent_code = pc.country_alpha2_to_continent_code(alpha2)
        continent_name = {
            "AF": "Africa",
            "AS": "Asia",
            "EU": "Europe",
            "NA": "North America",
            "SA": "South America",
            "OC": "Oceania",
            "AN": "Antarctica",
        }
        return continent_name.get(continent_code, "Other")
    except:
        return "Other"

df_combined["region"] = df_combined["country"].apply(get_region)

# Define dropdown options
years = sorted(df_combined["Year"].unique())
countries = sorted(df_combined["country"].unique())
regions = sorted(df_combined["region"].unique())

# Layout
app.layout = html.Div([
    html.H1("Refugee Dashboard", style={"textAlign": "center"}),

    dcc.Tabs([
        # Page 1: Country of Origin
        dcc.Tab(label="Country of Origin", children=[
            html.H2("Country of Origin"),
            dcc.Dropdown(
                id="year-dropdown-origin",
                options=[{"label": str(year), "value": year} for year in years],
                multi=True,
                placeholder="Select Year(s)"
            ),
            dcc.Dropdown(
                id="country-dropdown-origin",
                options=[{"label": country, "value": country} for country in countries],
                multi=True,
                placeholder="Select Country(s)"
            ),
            dcc.Dropdown(
                id="region-dropdown-origin",
                options=[{"label": region, "value": region} for region in regions],
                multi=True,
                placeholder="Select Region(s)"
            ),
            dcc.Graph(id="origin-graph")
        ]),

        # Page 2: Country of Asylum
        dcc.Tab(label="Country of Asylum", children=[
            html.H2("Country of Asylum"),
            dcc.Dropdown(
                id="year-dropdown-asylum",
                options=[{"label": str(year), "value": year} for year in years],
                multi=True,
                placeholder="Select Year(s)"
            ),
            dcc.Dropdown(
                id="country-dropdown-asylum",
                options=[{"label": country, "value": country} for country in countries],
                multi=True,
                placeholder="Select Country(s)"
            ),
            dcc.Dropdown(
                id="region-dropdown-asylum",
                options=[{"label": region, "value": region} for region in regions],
                multi=True,
                placeholder="Select Region(s)"
            ),
            dcc.Graph(id="asylum-graph")
        ]),

        # Page 3: Cross Analysis
        dcc.Tab(label="Cross Analysis", children=[
            html.H2("Cross Analysis of Origin and Asylum"),
            dcc.Dropdown(
                id="year-dropdown-cross",
                options=[{"label": str(year), "value": year} for year in years],
                multi=True,
                placeholder="Select Year(s)"
            ),
            dcc.Dropdown(
                id="country-dropdown-cross",
                options=[{"label": country, "value": country} for country in countries],
                multi=True,
                placeholder="Select Country(s)"
            ),
            dcc.Dropdown(
                id="region-dropdown-cross",
                options=[{"label": region, "value": region} for region in regions],
                multi=True,
                placeholder="Select Region(s)"
            ),
            dcc.Graph(id="cross-analysis-graph")
        ])
    ])
])

# Callbacks
@app.callback(
    Output("origin-graph", "figure"),
    [
        Input("year-dropdown-origin", "value"),
        Input("country-dropdown-origin", "value"),
        Input("region-dropdown-origin", "value"),
    ],
)
def update_origin_graph(selected_years, selected_countries, selected_regions):
    filtered_df = df_combined.copy()
    if selected_years:
        filtered_df = filtered_df[filtered_df["Year"].isin(selected_years)]
    if selected_countries:
        filtered_df = filtered_df[filtered_df["country"].isin(selected_countries)]
    if selected_regions:
        filtered_df = filtered_df[filtered_df["region"].isin(selected_regions)]

    fig = px.bar(
        filtered_df,
        x="country",
        y="Refugees_origin",
        color="region",
        title="Refugees by Country of Origin",
    )
    return fig


@app.callback(
    Output("asylum-graph", "figure"),
    [
        Input("year-dropdown-asylum", "value"),
        Input("country-dropdown-asylum", "value"),
        Input("region-dropdown-asylum", "value"),
    ],
)
def update_asylum_graph(selected_years, selected_countries, selected_regions):
    filtered_df = df_combined.copy()
    if selected_years:
        filtered_df = filtered_df[filtered_df["Year"].isin(selected_years)]
    if selected_countries:
        filtered_df = filtered_df[filtered_df["country"].isin(selected_countries)]
    if selected_regions:
        filtered_df = filtered_df[filtered_df["region"].isin(selected_regions)]

    fig = px.bar(
        filtered_df,
        x="country",
        y="Refugees_asylum",
        color="region",
        title="Refugees by Country of Asylum",
    )
    return fig


@app.callback(
    Output("cross-analysis-graph", "figure"),
    [
        Input("year-dropdown-cross", "value"),
        Input("country-dropdown-cross", "value"),
        Input("region-dropdown-cross", "value"),
    ],
)
def update_cross_analysis(selected_years, selected_countries, selected_regions):
    filtered_df = df_combined.copy()
    if selected_years:
        filtered_df = filtered_df[filtered_df["Year"].isin(selected_years)]
    if selected_countries:
        filtered_df = filtered_df[filtered_df["country"].isin(selected_countries)]
    if selected_regions:
        filtered_df = filtered_df[filtered_df["region"].isin(selected_regions)]

    fig = px.scatter(
        filtered_df,
        x="Refugees_origin",
        y="Refugees_asylum",
        color="region",
        size="Refugees_origin",
        hover_name="country",
        title="Bubble Chart of Refugee Volumes",
    )
    return fig

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
