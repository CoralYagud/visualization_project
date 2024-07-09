import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash

# Load and preprocess data
def load_data():
    food_data = pd.read_csv('world food production.csv')
    trade_data = pd.read_csv('trade_israel.csv')
    need_data = pd.read_csv('israel_need.csv')

    food_data = food_data[(food_data['Year'] >= 1989) & (food_data['Year'] <= 2020)]
    trade_data = trade_data[(trade_data['Year'] >= 1989) & (trade_data['Year'] <= 2020)]

    food_data_melted = food_data.melt(id_vars=['Entity', 'Year'],
                                      var_name='Food Item',
                                      value_name='Production (tonnes)')
    food_data_melted['Food Item'] = food_data_melted['Food Item'].str.replace(' Production \\(tonnes\\)', '')
    food_data_melted['Food Item'] = food_data_melted['Food Item'].str.replace(' Production \\( tonnes\\)', '')

    trade_data = trade_data[(trade_data['PartnerISO3'] == 'ISR') & (trade_data['TradeFlowName'] == 'Export')]
    trade_data = trade_data[['ReporterName', 'Year', 'TradeValue in 1000 USD']]
    trade_data.rename(columns={'ReporterName': 'Entity', 'TradeValue in 1000 USD': 'Export Value'}, inplace=True)

    return food_data_melted, trade_data, need_data

food_data_melted, trade_data, need_data = load_data()

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server  # Add this line

# Layout
app.layout = html.Div([
    html.Div([
        html.Div([
            html.H1("War on the Plate",
                    style={
                        'color': 'white',
                        'fontSize': '40px',
                        'fontWeight': 'bold',
                        'margin': '10px 0',
                        'textShadow': '2px 2px 4px black'  # Adding shadow effect for black border
                    }),
            html.H3("Analyzing Israel's Vulnerability to Food Shortages Controlled by Global Market Leaders",
                    style={
                        'color': 'white',
                        'fontSize': '24px',
                        'margin': '0',
                        'textShadow': '2px 2px 4px black'  # Adding shadow effect for black border
                    }),
        ], style={
            'backgroundImage': 'url(/assets/War_on_the_Plate.jpg)',
            'backgroundSize': 'cover',
            'textAlign': 'center',
            'padding': '40px 0',
            'border': '5px solid silver',  # Changing border to black
            'borderRadius': '10px'
        }),
    ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center', 'marginBottom': '20px'}),
    html.Div([
        html.Label("Select Country:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='country-dropdown',
            options=[{'label': country, 'value': country} for country in food_data_melted['Entity'].unique()],
            value='Israel',
            style={'marginBottom': '10px'}
        ),
        html.Label("Select Food Item:", style={'fontSize': '16px', 'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='food-dropdown',
            options=[{'label': item, 'value': item} for item in food_data_melted['Food Item'].unique()],
            style={'marginBottom': '20px'}
        )
    ], style={'width': '50%', 'margin': '0 auto', 'padding': '20px', 'boxShadow': '0px 0px 15px rgba(0, 0, 0, 0.1)', 'borderRadius': '10px', 'backgroundColor': '#f9f9f9'}),
    html.Div([
        dcc.Graph(id='global-map', style={'marginBottom': '20px'}),
        dcc.Slider(
            id='year-slider',
            min=food_data_melted['Year'].min(),
            max=food_data_melted['Year'].max(),
            value=food_data_melted['Year'].min(),
            marks={str(year): str(year) for year in food_data_melted['Year'].unique()},
            step=None,
            tooltip={'placement': 'bottom', 'always_visible': True}
        ),
        html.Div([
            html.Button('Start', id='play-button', n_clicks=0, style={'margin-right': '10px', 'fontSize': '16px', 'padding': '10px', 'backgroundColor': '#000080', 'color': 'white', 'border': 'none', 'borderRadius': '5px'}),
            html.Button('Pause', id='stop-button', n_clicks=0, style={'margin-right': '10px', 'fontSize': '16px', 'padding': '10px', 'backgroundColor': '#000080', 'color': 'white', 'border': 'none', 'borderRadius': '5px'}),
        ], style={'textAlign': 'center', 'margin': '20px 0'}),
        dcc.Interval(
            id='interval-component',
            interval=800,  # in milliseconds
            n_intervals=0,
            disabled=True  # initially disabled
        ),
        dcc.Graph(id='country-line-chart')
    ], style={'textAlign': 'center', 'margin': '0 auto', 'width': '80%'}),
], style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#f4f4f4', 'padding': '20px'})

# Callbacks
@app.callback(
    [Output('global-map', 'figure'),
     Output('country-line-chart', 'figure')],
    [Input('country-dropdown', 'value'),
     Input('food-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_charts(selected_country, selected_food, selected_year):
    filtered_food_data = food_data_melted[(food_data_melted['Year'] == selected_year) & (food_data_melted['Food Item'] == selected_food)]
    country_food_data = food_data_melted[(food_data_melted['Entity'] == selected_country) & (food_data_melted['Food Item'] == selected_food)]
    filtered_trade_data = trade_data[(trade_data['Year'] == selected_year)]
    total_value_row = need_data[need_data['Category'] == selected_food]
    total_value = total_value_row['Total Value (tonnes)'].values[0] if not total_value_row.empty else None
    merged_data = pd.merge(filtered_food_data, filtered_trade_data, on=['Entity', 'Year'], how='left')

    fig_map = go.Figure(data=[
        go.Choropleth(
            locations=merged_data['Entity'],
            locationmode='country names',
            z=merged_data['Production (tonnes)'],
            colorscale='Viridis',
            marker_line_width=1,
            marker_opacity=0.8,
            marker_line_color=merged_data['Export Value'].apply(lambda x: 'green' if pd.notnull(x) else 'red'),
            showscale=True,
            visible=True
        ),
        go.Choropleth(
            locations=merged_data['Entity'],
            locationmode='country names',
            z=merged_data['Production (tonnes)'],
            colorscale='Viridis',
            marker_line_width=1,
            marker_opacity=0.8,
            showscale=True,
            visible=False
        ),
        go.Choropleth(
            locations=merged_data['Entity'],
            locationmode='country names',
            z=merged_data['Production (tonnes)'],
            colorscale=[[0, 'rgba(0,0,0,0)'], [1, 'rgba(0,0,0,0)']],
            marker_line_width=1,
            marker_opacity=0.8,
            marker_line_color=merged_data['Export Value'].apply(lambda x: 'green' if pd.notnull(x) else 'red'),
            showscale=False,
            visible=False
        )
    ])

    fig_map.update_layout(
        updatemenus=[
            dict(
                buttons=list([
                    dict(
                        args=[{'visible': [True, False, False]}, {'annotations[0].visible': True}],
                        label="Borders & Colors",
                        method="update"
                    ),
                    dict(
                        args=[{'visible': [False, False, True]}, {'annotations[0].visible': True}],
                        label="Borders Only",
                        method="update"
                    ),
                    dict(
                        args=[{'visible': [False, True, False]}, {'annotations[0].visible': False}],
                        label="Colors Only",
                        method="update"
                    )
                ]),
                direction="down",
                showactive=True,
            ),
        ],
        title={
        'text': f'Global Production and Exports to Israel of {selected_food} in {selected_year}',
        'font': {
            'family': 'Arial, sans-serif',
            'size': 24,
            'color': 'black'
        },
        'x': 0.5,
        'xanchor': 'center'
    },
        legend=dict(x=0.05, y=0, traceorder='normal', font=dict(size=12)),
        height=600,
        width=1200,
        annotations=[
            dict(
                x=0.05, y=0.01,
                xref='paper', yref='paper',
                text='<span style="color:green">⬤</span> Exporting to Israel<br>'
                     '<span style="color:red">⬤</span> Not Exporting to Israel<br>'
                     '<span style="color:blue">▯</span> Production (tonnes)',
                showarrow=False,
                align='left',
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='black',
                borderwidth=1,
                visible=True
            )
        ],
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    fig_line = go.Figure()

    fig_line.add_trace(go.Scatter(
        x=country_food_data['Year'],
        y=country_food_data['Production (tonnes)'],
        mode='lines+markers',
        name='Production',
        line=dict(color='blue'),
        text=country_food_data['Production (tonnes)'],
        hoverinfo='text'
    ))

    if selected_country == 'Israel' and total_value is not None:
        fig_line.add_trace(go.Scatter(
            x=country_food_data['Year'],
            y=[total_value] * len(country_food_data),
            mode='lines',
            name='Supply need',
            line=dict(color='Red', dash='dash')
        ))

    fig_line.update_layout(
            title={
        'text': f'Production of {selected_food} in {selected_country} Over Time',
        'font': {
            'family': 'Arial, sans-serif',
            'size': 24,
            'color': 'black'
        },
        'x': 0.5,
        'xanchor': 'center'
    },
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="date"
        ),
        yaxis=dict(title='Production (tonnes)'),
        hovermode='x unified',
        height=600,
        width=1200,
        paper_bgcolor='rgba(0,0,0,0)'  # Making the paper background transparent
    )

    return fig_map, fig_line

@app.callback(
    [Output('year-slider', 'value'),
     Output('interval-component', 'disabled')],
    [Input('interval-component', 'n_intervals'),
     Input('play-button', 'n_clicks'),
     Input('stop-button', 'n_clicks')],
    [State('year-slider', 'value'),
     State('year-slider', 'min'),
     State('year-slider', 'max')]
)
def update_slider(n_intervals, play_clicks, stop_clicks, current_year, min_year, max_year):
    ctx = dash.callback_context

    if not ctx.triggered:
        return current_year, True
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger == 'play-button':
        return min_year, False  # Reset to the beginning and start the interval

    if trigger == 'stop-button':
        return current_year, True  # Pause the interval

    if trigger == 'interval-component':
        if current_year < max_year:
            return current_year + 1, False
        else:
            return min_year, True  # Reset to the beginning and stop

    return current_year, True

# Run app
if __name__ == '__main__':
    print("Starting the app...")
    app.run_server(debug=True)
