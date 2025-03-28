from dash import Dash, html, dcc, callback, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

BOOTSTRAP_CSS = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"

df = pd.read_csv('fifa-wcf-data.csv')

win_counts = (
	pd.concat([
		df["Winners"].value_counts().rename("Wins"),
		df["Runners-up"].value_counts().rename("Runner Up")
	], axis=1, sort=False)
	.fillna(0)
	.reset_index()
)
win_counts.columns = ["Country", "Wins", "Runner Up"]


app = Dash(external_stylesheets = [BOOTSTRAP_CSS])

app.layout = html.Div(
    [
        html.H1("FIFA World Cup Winners & Runner-Ups", className="text-center mb-4"),
        
        # Filter Type Radio Buttons (all, country, year)
        html.Div([
            html.Label("Filter:", className="form-label", htmlFor="filter_type"),
            html.Div([
                dcc.RadioItems(
                    id="filter_type",
                    options=[
                        {"label": " Show All", "value": "all"},
                        {"label": " Filter by Country", "value": "country"},
                        {"label": " Filter by Year", "value": "year"}
                    ],
                    value="all",
                    inline=False,
                    inputClassName="form-check-input",
                    labelClassName="form-check-label",
                    className="radio-group"
                ),
            ], className="form-check mb-3")
        ], className="p-3 bg-light rounded"),
        
        # Country dropdown (initially hidden)
        html.Div([
            html.Label("Select a Country:", className="form-label", htmlFor="country_dropdown"),
            dcc.Dropdown(
                id="country_dropdown",
                options=[{"label": c, "value": c} for c in win_counts["Country"]],
                className="mb-2"
            )
        ], id="country_container", style={"display": "none"}),
        
        # Year dropdown (initially hidden)
        html.Div([
            html.Label("Select a Year:", className="form-label", htmlFor="year_dropdown"),
            dcc.Dropdown(
                id="year_dropdown",
                options=[{"label": y, "value": y} for y in df["Year"]],
                className="mb-2"
            )
        ], id="year_container", style={"display": "none"}),

        # Choropleth map
        dcc.Graph(id="worldcup_map", responsive=True, style={"height": "65vh"}),

    ], className="container-fluid")

# Radio Button/Filter Type callback
@callback(
    Output("country_container", "style"),
    Output("year_container", "style"),
    Output("country_dropdown", "value"),
    Output("year_dropdown", "value"),
    Input("filter_type", "value")
)
def toggle_dropdowns(filter_type):
    country_style = {"display": "none"}
    year_style = {"display": "none"}
    country_value = None
    year_value = None
    
    if filter_type == "country":
        country_style = {"display": "block"}
    elif filter_type == "year":
        year_style = {"display": "block"}
        
    return country_style, year_style, country_value, year_value

# Choropleth Map Callback
@callback(
    Output("worldcup_map", "figure"),
    Input("filter_type", "value"),
    Input("country_dropdown", "value"),
    Input("year_dropdown", "value")
)
def update_graph(filter_type, selected_country, selected_year):
    title = ""
    
    if filter_type == "year" and selected_year is not None:
        # Show winner and runner-up for selected year
        year_df = df[df["Year"] == selected_year]
        winner = year_df["Winners"].values[0]
        runner_up = year_df["Runners-up"].values[0]
        filtered_df = win_counts[(win_counts["Country"] == winner) | (win_counts["Country"] == runner_up)]
        title = f"FIFA World Cup {selected_year} - {winner} (Winner), {runner_up} (Runner-Up)"
    elif filter_type == "country" and selected_country is not None:
        # Show stats for selected country
        filtered_df = win_counts[win_counts["Country"] == selected_country]
        wins = int(filtered_df["Wins"].values[0])
        runner_ups = int(filtered_df["Runner Up"].values[0])
        title = f"{selected_country} - Total Wins: {wins}, Total Runner-Ups: {runner_ups}"
    else:
        # Default: Show all countries
        filtered_df = win_counts
        title = "FIFA World Cup Winners - All Countries"
    
    # Create choropleth map
    fig = px.choropleth(
        filtered_df,
        locations="Country",
        locationmode="country names",
        color="Wins",
        color_continuous_scale=px.colors.sequential.Greens,
        range_color=(0, filtered_df["Wins"].max()),
        title=title,
        labels={"Wins": "Number of Wins", "Runner Up": "Times Runner-Up"},
        hover_name="Country",
        hover_data={"Country": False, "Wins": True, "Runner Up": True},
        projection="natural earth",
    )
    
    fig.update_geos(
        showcoastlines=True,
        coastlinecolor="Black",
        showland=True,
        landcolor="LightGray",
        showocean=True,
        oceancolor="LightBlue",
        showlakes=False,
        countrycolor="Black",
        fitbounds="locations",
    )

    return fig

if __name__ == '__main__':
	app.run_server(debug=True)
