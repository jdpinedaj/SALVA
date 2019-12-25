#!/usr/bin/env python
__author__ = "Javier Moreno, Juan D. Pineda-Jaramillo, Esteban Silva-Villa"
__copyright__ = "Copyright 2019, SALVA"
__credits__ = [
    "Juan Diego Pineda Jaramillo, Esteban Silva Villa, Javier Andres Moreno Garzon"]
__status__ = "Prototype"

# Libraries
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import numpy as np
# ==========================

# Custom code
import apitransit as apt
import read_db as rdb
import constants
# ==========================

# Reading constants
token = constants.MAPBOXTOKEN
days = constants.DAYS
months = constants.MONTHS
hours = constants.HOURS
localdatapath = constants.LOCALDATAPATH
sqlcoord = constants.SQLCOORD
sqlgral = constants.SQLGRAL
heatmapstyle = constants.HEATMAPSTYLE
reversecolorscale = constants.REVERSECOLORSCALE
logoimg = constants.LOGO
# ==========================

# App initialize
app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)
server = app.server
app.config["suppress_callback_exceptions"] = False
# ==========================

# Loading initial data from database
'''
df_coord = pd.read_sql(sqlcoord, rdb.getCon(), parse_dates=['fecha_homologada', 'hora_homologada'])
df_geral = pd.read_sql(sqlgral, rdb.getCon(), parse_dates=['fecha', 'hora'])
'''
# ==========================

# Loading initial data from local files
df_coord = pd.read_csv(localdatapath+'final1_coord_accidents.csv',
                       sep='|', parse_dates=['fecha_homologada', 'hora_homologada'])
df_geral = pd.read_csv(localdatapath+'final1_gral_accidents.csv',
                       sep='|', parse_dates=['fecha_accidente', 'hora_accidente'])
df_clusters = pd.read_csv(localdatapath+'accidents_cluster.csv', sep='|')
# ==========================

# Applying transformations to initial data
df_coord['fecha_homologada'] = pd.to_datetime(
    df_coord['fecha_homologada'], format='%Y-%m-%d')
df_coord['hora_homologada'] = pd.to_datetime(
    df_coord['hora_homologada'], format='%H:%M:%S')
df_coord['dayweek'] = df_coord['fecha_homologada'].dt.dayofweek
df_coord['YEAR'] = df_coord['fecha_homologada'].dt.year
df_coord['HOUR'] = df_coord['hora_homologada'].dt.hour
df_coord['name_day_week'] = df_coord['fecha_homologada'].dt.day_name()
df_coord['name_day_week'] = pd.Categorical(
    df_coord['name_day_week'], categories=days, ordered=True)
df_coord["monthname"] = df_coord['fecha_homologada'].dt.strftime("%B")
df_coord['monthname'] = pd.Categorical(
    df_coord['monthname'], categories=months, ordered=True)

df_geral['fecha_accidente'] = pd.to_datetime(
    df_geral['fecha_accidente'], format='%h-%m-%d')
df_geral['hora_accidente'] = pd.to_datetime(
    df_geral['hora_accidente'][df_geral['hora_accidente'] != 'None'], format='%H:%M:%S')
df_geral['dayweek'] = df_geral['fecha_accidente'].dt.dayofweek
df_geral['YEAR'] = df_geral['fecha_accidente'].dt.year
df_geral['HOUR'] = df_geral['hora_accidente'].dt.hour
df_geral['name_day_week'] = df_geral['fecha_accidente'].dt.day_name()
df_geral['name_day_week'] = pd.Categorical(
    df_geral['name_day_week'], categories=days, ordered=True)
df_geral["monthname"] = df_geral['fecha_accidente'].dt.strftime("%B")
df_geral['monthname'] = pd.Categorical(
    df_geral['monthname'], categories=months, ordered=True)
# ==========================

# Builders


def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Img(src=app.get_asset_url(logoimg)),
            #html.H6("Accident Analysis in Medellín"),
        ],
    )


def build_graph_title(title):
    return html.P(className="graph-title", children=title)
# ==========================

# Interactive Map Application


def perform_api_call(iniloc, endloc, tmode='driving'):
    directions = apt.directions_result(iniloc, endloc, tmode)
    row_list = []
    for i, direction in enumerate(directions):
        for leg in direction['legs']:
            for step in leg['steps']:
                row_list.append([i, step['start_location']['lat'],
                                 step['start_location']['lng']])
                row_list.append([i, step['end_location']['lat'],
                                 step['end_location']['lng']])
    res = pd.DataFrame(row_list, columns=('Id Route', 'latitud', 'longitud'))
    res = res.drop_duplicates(
        subset=["Id Route", "latitud", "longitud"]).reset_index()
    res = apt.getClusters(df_cluster=df_clusters, y='latitud',
                          x='longitud', df_eval=res, distance=0.08)
    return res
# ==========================

# Dataframes filters


def filter_df_coord(type_accident, day_accident, start_date, end_date, value):
    ok = (df_coord['clase'].isin(type_accident)) & \
        (df_coord['name_day_week'].isin(day_accident)) & \
        (df_coord['fecha_homologada'] >= pd.to_datetime(start_date)) & \
        (df_coord['fecha_homologada'] <= pd.to_datetime(end_date)) & \
        (df_coord['HOUR'] <= value[1]) & (df_coord['HOUR'] >= value[0])

    dff = df_coord[ok]

    return (dff)


def filter_df_geral(type_accident, day_accident, start_date, end_date, value):
    ok = (df_geral['clase_de_accidente'].isin(type_accident)) & \
        (df_geral['name_day_week'].isin(day_accident)) & \
        (df_geral['fecha_accidente'] >= pd.to_datetime(start_date)) & \
        (df_geral['fecha_accidente'] <= pd.to_datetime(end_date)) & \
        (df_geral['HOUR'] <= value[1]) & (df_geral['HOUR'] >= value[0])

    dff = df_geral[ok]

    return (dff)
# ==========================


# App Main Layout
app.layout = html.Div(
    children=[
        html.Div(
            id="top-row",
            children=[
                html.Div(
                    className="row",
                    id="top-row-header",
                    children=[
                        html.Div(
                            id="header-container",
                            children=[
                                build_banner(),
                                # html.P(
                                #     id="instructions",
                                #     children="Select days and hours.........",
                                # ),
                                build_graph_title("Type of accident"),
                                dcc.Dropdown(
                                    id="type-accident",
                                    multi=True,
                                    value=('Choque',),
                                    options=[{'label': label.title(), 'value': label.title(
                                    )} for label in df_coord['clase'].unique()]
                                ),  # Dcc
                                build_graph_title("Day of accident"),
                                dcc.Dropdown(
                                    id="day-accident",
                                    multi=True,
                                    value=('Monday',),
                                    options=[
                                        {'label': label.title(), 'value': label.title()} for label in days]
                                ),  # Dcc
                                build_graph_title("Select Date Range"),
                                dcc.DatePickerRange(
                                    id="date-range",
                                    min_date_allowed=df_coord['fecha_homologada'].min(
                                    ),
                                    max_date_allowed=df_coord['fecha_homologada'].max(
                                    ),
                                    initial_visible_month=df_coord['fecha_homologada'].max(
                                    ),
                                    display_format="DD-MMM-YYYY",
                                    start_date=df_coord['fecha_homologada'].min(
                                    ),
                                    end_date=df_coord['fecha_homologada'].max()
                                ),
                                build_graph_title("Select an Hour Range"),
                                dcc.RangeSlider(
                                    id="hour-range",
                                    min=0,
                                    max=24,
                                    value=[0, 23],
                                    marks={str(h): {'label': str(h), 'style': {
                                        'color': 'white'}} for h in range(0, 24)},
                                    included=True
                                )  # dcc.
                            ],
                        )
                    ],
                ),
                html.Div(
                    className="row",
                    id="top-row-graphs",
                    children=[
                        # Heat map
                        html.Div(
                            id="heat-map",
                            children=[
                                #build_graph_title("Heat Map"),
                                dcc.Graph(
                                    id="heat-plot",
                                    figure={
                                        "layout": {
                                            "paper_bgcolor": "#192444",
                                            "plot_bgcolor": "#192444",
                                        }
                                    },
                                    config={"scrollZoom": True,
                                            "displayModeBar": True},
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            className="row",
            id="app-show-row",
            children=[
                # Accidents by time
                html.Div(
                    id="form-bar-container",
                    className="six columns",
                    children=[
                        html.H1('Accidents by Time'),
                        # build_graph_title(
                        #     "Accidents by time"),
                        dcc.Graph(
                            id="severity-types",
                            figure={}
                        ),
                        html.Div(id='Accidents by Time',
                                 className="six columns",)
                    ],
                ),
                html.Div([
                    html.H1('Cross-Correlations'),
                    dcc.Tabs(id="tabs-example", value='tab-3-example',
                             children=[
                                 dcc.Tab(label='By day per month',
                                         value='tab-1-example'),
                                 dcc.Tab(label='By hour per day',
                                         value='tab-2-example'),
                                 dcc.Tab(label='By severity per class',
                                         value='tab-3-example'),
                             ]
                             ),
                    html.Div(id='tabs-content-example',
                             className="six columns",)
                ])
            ],
        ),
        # Application Map
        html.Div(
            id="bottom-row",
            children=[
                html.Div(
                    className="row",
                    id="app-row-header",
                    children=[
                        html.Div(
                            id="app-header-container",
                            className="four columns",
                            children=[
                                html.H1(
                                    className="banner",
                                    id="app-instructions",
                                    children="Type start and end location for your travel",
                                ),
                                build_graph_title("Start location"),
                                dcc.Input(
                                    id="startlocation",
                                    placeholder='Enter a value...',
                                    type='text',
                                    value=''
                                ),  # Dcc
                                build_graph_title(
                                    "End location"),
                                dcc.Input(
                                    id="endlocation",
                                    placeholder='Enter a value...',
                                    type='text',
                                    value=''
                                ),  # Dcc
                                build_graph_title("Transportation mode"),
                                dcc.Dropdown(
                                    id="transportationmode",
                                    multi=False,
                                    value='driving',
                                    options=[
                                        {'label': 'Driving', 'value': 'driving'},
                                        {'label': 'Walking', 'value': 'walking'},
                                        {'label': 'Bicycling',
                                            'value': 'bicycling'},
                                        {'label': 'Transit', 'value': 'transit'},
                                    ],
                                ),
                                html.Button('Submit', id='button'),
                            ],
                        ),
                        html.Div(
                            # App Map
                            id="production-container",
                            className="eight columns",
                            children=[
                                #build_graph_title("App Map"),
                                dcc.Graph(
                                    id="app-plot",
                                    figure={
                                        "layout": {
                                            "paper_bgcolor": "#192444",
                                            "plot_bgcolor": "#192444",
                                        }
                                    },
                                    config={"scrollZoom": True,
                                            "displayModeBar": True},
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        # Application Accidents Probabilities
        html.Div(
            id="bottom-last-row",
            children=[
                html.Div(
                    className="row",
                    id="pred-row-header",
                    children=[
                        html.Div(
                            id="pred-header-container",
                            className="four columns",
                            children=[
                                html.H1(
                                    className="banner",
                                    id="pred-instructions",
                                    children="Choose prediction variables",
                                ),
                                build_graph_title("Accident type"),
                                dcc.Dropdown(
                                    id="value_1",
                                    multi=False,
                                    value=constants.TYPE_ACCIDENT[0],
                                    options=[{'label': constants.TYPE_ACCIDENT[k], 'value': v} for k, v in enumerate(constants.TYPE_ACCIDENT)],
                                ),
                                build_graph_title("Road type"),
                                dcc.Dropdown(
                                    id="value_2",
                                    multi=False,
                                    value=constants.TYPE_ROAD[0],
                                    options=[{'label': constants.TYPE_ROAD[k], 'value': v} for k, v in enumerate(constants.TYPE_ROAD)],
                                ),
                                build_graph_title("Roadways"),
                                dcc.Dropdown(
                                    id="value_3",
                                    multi=False,
                                    value=constants.NUMBER_ROADS[0],
                                    options=[{'label': constants.NUMBER_ROADS[k], 'value': v} for k, v in enumerate(constants.NUMBER_ROADS)],
                                ),
                                build_graph_title("Number of lanes"),
                                dcc.Dropdown(
                                    id="value_4",
                                    multi=False,
                                    value=constants.NUMBER_LANES[0],
                                    options=[{'label': constants.NUMBER_LANES[k], 'value':v} for k, v in enumerate(constants.NUMBER_LANES)],
                                ),
                                build_graph_title("Road status"),
                                dcc.Dropdown(
                                    id="value_5",
                                    multi=False,
                                    value=constants.STATUS_ROAD[0],
                                    options=[{'label': constants.STATUS_ROAD[k], 'value': v} for k, v in enumerate(constants.STATUS_ROAD)],
                                ),
                                build_graph_title("Traffic light"),
                                dcc.Dropdown(
                                    id="value_6",
                                    multi=False,
                                    value=constants.TRAFFIC_LIGHT[0],
                                    options=[{'label': constants.TRAFFIC_LIGHT[k], 'value': v} for k, v in enumerate(constants.TRAFFIC_LIGHT)],
                                ),
                                build_graph_title("Vertical signs"),
                                dcc.Dropdown(
                                    id="value_7",
                                    multi=False,
                                    value=constants.VERTICAL_SIGNALS[0],
                                    options=[{'label': constants.VERTICAL_SIGNALS[k], 'value': v} for k, v in enumerate(constants.VERTICAL_SIGNALS)],
                                ),
                                build_graph_title("Horizontal signs"),
                                dcc.Dropdown(
                                    id="value_8",
                                    multi=False,
                                    value=constants.HORIZONTAL_SIGNALS[0],
                                    options=[{'label': constants.HORIZONTAL_SIGNALS[k], 'value': v} for k, v in enumerate(constants.HORIZONTAL_SIGNALS)],
                                ),
                                build_graph_title("Speed brakers"),
                                dcc.Dropdown(
                                    id="value_9",
                                    multi=False,
                                    value=constants.SPEED_BREAKERS[0],
                                    options=[{'label': constants.SPEED_BREAKERS[k], 'value': v} for k, v in enumerate(constants.SPEED_BREAKERS)],
                                ),

                            ],
                        ),
                        html.Div(
                            # Correlation between variables and severity of accidents
                            id="production-pred",
                            className="eight columns",
                            children=[
                                build_graph_title("Select variables and click predict"),
                                html.Button('Predict', id='buttonpredict'),
                                html.Div(id="pred-text",
                                children=[html.P("Select variables and click Predict"),]
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ]
)
# =========================


# Callback for Barplot
@app.callback(
    dash.dependencies.Output('severity-types', 'figure'),
    [
        dash.dependencies.Input('type-accident', 'value'),
        dash.dependencies.Input('day-accident', 'value'),
        dash.dependencies.Input('date-range', 'start_date'),
        dash.dependencies.Input('date-range', 'end_date'),
        dash.dependencies.Input('hour-range', 'value')
    ]
)
def update_scatter_chart(type_accident, day_accident, start_date, end_date, value):
    dff = filter_df_geral(type_accident, day_accident,
                          start_date, end_date, value)

    count_inj = calc_nums_grav(
        type_accident, day_accident, start_date, end_date, dff, 'HERIDO')
    trace_inj = go.Bar(x=count_inj['fecha_accidente'],
                       y=count_inj['nro_radicado'], name='Injuries')

    count_sdn = calc_nums_grav(
        type_accident, day_accident, start_date, end_date, dff, 'SOLO DAÑOS')
    trace_sdn = go.Bar(x=count_sdn['fecha_accidente'],
                       y=count_sdn['nro_radicado'], name='Only Damages')

    count_dea = calc_nums_grav(
        type_accident, day_accident, start_date, end_date, dff, 'MUERTO')
    trace_dea = go.Bar(x=count_dea['fecha_accidente'],
                       y=count_dea['nro_radicado'], name='Deads')  # .title()

    return {
        'data': [trace_inj, trace_sdn, trace_dea],
        'layout': go.Layout(  # title='Severity_accident over time',
            height=400,
            yaxis={'title': "Number of accidents", 'titlefont': {
                'color': 'black', 'size': 14, }, 'tickfont': {'color': 'black'}},
            xaxis={'title': "Date", 'titlefont': {
                'color': 'black', 'size': 14}, 'tickfont': {'size': 12, 'color': 'black'}},
        )
    }


def calc_nums_grav(type_accident, day_accident, start_date, end_date, dff, grav_acc):
    cnt = dff.groupby(
        ['gravedad_accidente', 'fecha_accidente']).count().reset_index()
    cnt = cnt[cnt['gravedad_accidente'] == grav_acc]
    return (cnt)
# =========================

# Callback for HeatMap


@app.callback(
    dash.dependencies.Output('heat-plot', 'figure'),
    [
        dash.dependencies.Input('type-accident', 'value'),
        dash.dependencies.Input('day-accident', 'value'),
        dash.dependencies.Input('date-range', 'start_date'),
        dash.dependencies.Input('date-range', 'end_date'),
        dash.dependencies.Input('hour-range', 'value')
    ]
)
def update_accident_chart(type_accident, day_accident, start_date, end_date, value):
    dff = filter_df_coord(type_accident, day_accident,
                          start_date, end_date, value)
    z1 = dff[['latitud', 'longitud', 'HOUR']].groupby(
        ['latitud', 'longitud']).count().reset_index()
    z2 = dff[['latitud', 'longitud']].groupby(
        ['latitud', 'longitud']).count().reset_index()

    ht_mat = go.Densitymapbox(lat=z2['latitud'], lon=z2['longitud'],
                              z=z1['HOUR'], name='Inj, Dam, Dea',
                              colorscale=heatmapstyle,
                              autocolorscale=False,
                              reversescale=reversecolorscale,
                              )

    # pdb.set_trace()

    return {
        'data': [ht_mat],
        'layout': go.Layout(
            mapbox_style="stamen-terrain",
            mapbox_accesstoken=token,
            mapbox_zoom=12,
            margin={'t': 0, 'l': 0,
                    'r': 0, 'b': 30},
            mapbox_center={
                "lat": 6.246260, "lon": -75.575259}
        )
    }


# =========================

# Callback for TABS

@app.callback(
    dash.dependencies.Output('tabs-content-example', 'children'),
    [
        dash.dependencies.Input('tabs-example', 'value')
    ]
)
def render_content(value):
    # by severity
    if value == 'tab-3-example':
        grouped_df = df_geral.groupby(
            ["gravedad_accidente", "clase_de_accidente"])
        ht = pd.DataFrame(grouped_df.size().reset_index(name="Group_Count"))
        pt = pd.pivot_table(data=ht,
                            index='gravedad_accidente',
                            values='Group_Count',
                            columns='clase_de_accidente')

        ht_mat = go.Heatmap(z=pt, x=df_geral['clase_de_accidente'].unique(
        ), y=df_geral['gravedad_accidente'].unique(), colorscale=heatmapstyle, reversescale=reversecolorscale)

        return html.Div([
            #            html.H3('Tab content 1'),
            dcc.Graph(
                id='graph-3-tabs',
                figure={
                    'data': [ht_mat],
                    'layout': go.Layout(
                        #                        title='HeatMap Accidents',
                        #                        yaxis={'title': "Severity", 'titlefont': {'color': 'black', 'size': 14, },'tickfont': {'color': 'black'}},
                        xaxis={'title': "Class", 'titlefont': {
                            'color': 'black', 'size': 14}, 'tickfont': {'size': 12, 'color': 'black'}},
                    ),
                },
            )
        ])

# by hour
    elif value == 'tab-2-example':
        grouped_df2 = df_geral.groupby(["name_day_week", "HOUR"])
        ht2 = pd.DataFrame(grouped_df2.size().reset_index(name="Group_Count"))

        pt2 = pd.pivot_table(data=ht2,
                             columns='name_day_week',
                             values='Group_Count',
                             index='HOUR')

        heatmap_hour = go.Heatmap(z=pt2, x=days, y=hours,
                                  colorscale=heatmapstyle, reversescale=reversecolorscale)

        return html.Div([
            dcc.Graph(
                id='graph-2-tabs',
                figure={
                    'data': [heatmap_hour],
                    'layout': go.Layout(
                        xaxis={'title': "Days", 'titlefont': {
                            'color': 'black', 'size': 14}, 'tickfont': {'size': 12, 'color': 'black'}},
                    ),
                }
            )
        ])

# By week
    elif value == 'tab-1-example':
        grouped_df3 = df_geral.groupby(["name_day_week", "monthname"])
        ht3 = pd.DataFrame(grouped_df3.size().reset_index(name="Group_Count"))

        pt3 = pd.pivot_table(data=ht3,
                             index='name_day_week',
                             values='Group_Count',
                             columns='monthname')

        heatmap_month = go.Heatmap(
            z=pt3, x=months, y=days, colorscale=heatmapstyle, reversescale=reversecolorscale)

        return html.Div([
            #            html.H3('Tab content 1'),
            dcc.Graph(
                id='graph-1-tabs',
                figure={
                    'data': [heatmap_month],
                    'layout': go.Layout(
                        xaxis={'title': "Months", 'titlefont': {
                            'color': 'black', 'size': 14}, 'tickfont': {'size': 12, 'color': 'black'}},
                    )
                }
            )
        ])


# =========================

# Callback for Interactive Map
@app.callback(
    dash.dependencies.Output('app-plot', 'figure'),
    [
        dash.dependencies.Input('button', 'n_clicks'),
    ],
    [
        dash.dependencies.State('startlocation', 'value'),
        dash.dependencies.State('endlocation', 'value'),
        dash.dependencies.State('transportationmode', 'value'),
    ]
)
def update_app_map(n_clicks, startlocation, endlocation, value='driving'):
    print("otra cosa")
    print('The input value was "{}"-"{}"-"{}" and the button has been clicked {} times'.format(
        startlocation, endlocation, value, n_clicks))
    print("before if")
    print(startlocation == '' and endlocation == '')
    if (startlocation == '' or endlocation == ''):
        print("Doing nothing")
        return {
            'data': [go.Scattermapbox()],
            'layout': go.Layout(
                # mapbox_style="mapbox://styles/mapbox/light-v10",
                mapbox_style="stamen-terrain",
                mapbox_accesstoken=token,
                mapbox_zoom=12,
                margin={'t': 0, 'l': 0,
                        'r': 0, 'b': 30},
                mapbox_center={
                    "lat": 6.246260, "lon": -75.575259}
            )}
    else:
        print("Start API call")
        result = perform_api_call(startlocation, endlocation, value)
        print("Finish API call")
        print("Route")
        print(result)
        markers = result[result['Cluster'] > -1]
        print("Danger clusters")
        print(markers)

    figscat = go.Scattermapbox(name='Route Indication',
                               lat=result['latitud'],
                               lon=result['longitud'],
                               mode='lines',
                               line=dict(width=2, color='blue'),)

    figmarkers = go.Scattermapbox(name='Hotspots',
                                  lat=markers['latitud'],
                                  lon=markers['longitud'],
                                  mode='markers',
                                  text=markers['Weight'],
                                  marker=go.scattermapbox.Marker(
                                      size=14,
                                      autocolorscale=False,
                                      reversescale=reversecolorscale,
                                      cmin=0,
                                      cmax=1,
                                      colorbar_title='Accident hotspots',
                                      colorscale=heatmapstyle,
                                      color=markers['Weight'],
                                      opacity=0.8,

                                  ),)

    print("exiting function")
    return {
        'data': [figscat, figmarkers],
        'layout': go.Layout(
            # mapbox_style="mapbox://styles/mapbox/light-v10",
            mapbox_style="stamen-terrain",
            mapbox_accesstoken=token,
            mapbox_zoom=12,
            margin={'t': 0, 'l': 0,
                    'r': 0, 'b': 30},
            mapbox_center={
                "lat": result['latitud'][0], "lon": result['longitud'][0]}
        )
    }
# =========================


# Callback for Accident severity 
@app.callback(
    dash.dependencies.Output('pred-text', 'children'),
    [
        dash.dependencies.Input('buttonpredict', 'n_clicks'),
    ],
    [
        dash.dependencies.State('value_1', 'value'),
        dash.dependencies.State('value_2', 'value'),
        dash.dependencies.State('value_3', 'value'),
        dash.dependencies.State('value_4', 'value'),
        dash.dependencies.State('value_5', 'value'),
        dash.dependencies.State('value_6', 'value'),
        dash.dependencies.State('value_7', 'value'),
        dash.dependencies.State('value_8', 'value'),
        dash.dependencies.State('value_9', 'value'),
    ]
)
def update_pred_text(n_clicks, value_1, value_2, value_3, value_4, value_5, value_6, value_7, value_8, value_9):
    print("Update Pred Text")
    try:
        if (value_1 == '' or value_2 == '' or value_3 == '' or value_4 == ''or value_5 == ''or value_6 == ''or value_7 == ''or value_8 == ''or value_3 == ''):
            print("Doing nothing")
            return html.Div("Select variables and click Predict")
        else:
            print("Start API call")
            result = apt.predict_severity(np.stack([value_1,value_2,value_3,value_4,value_5,value_6,value_7,value_8,value_9]))
            print("Finish API call")
            print(result)
            output= "{0} {1} {2}".format("The probability of being a serious accident is: ", result,"%")    
        return html.Div(output)   
    except:
        return html.Div("Select variables and click Predict")
    
# =========================


# Running the server
if __name__ == "__main__":
    app.run_server(debug=True)
# =========================
