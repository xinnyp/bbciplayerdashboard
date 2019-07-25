import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import cufflinks as cf
import plotly.graph_objs as go
import dash_table

cf.set_config_file(world_readable=True, offline=True)

# Step 1. Launch the application
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True
server = app.server

# Step 2. Import the datasets
user_info = pd.read_csv('cleaned_user_info.csv')

web_usage = pd.read_csv('cleaned_web_usage.csv', parse_dates=['date'])
web_usage['date'] = web_usage.date.values.astype('datetime64[D]')
date_min = web_usage.date.min()
date_max = web_usage.date.max()

grouped = web_usage.groupby(['region']).agg({'session_id': pd.Series.nunique, 'play_time': 'sum'})
grouped = grouped.reset_index()
g2_features = grouped.columns[1:]
g2_opts = [{'label': i, 'value': i} for i in g2_features]

df_genre = pd.read_csv('genre_analysis.csv')

most_popular = pd.read_csv('iplayer_most_popular.csv')

trace_1 = go.Pie(labels=grouped.region, values=grouped.session_id,
                 name='session_id', showlegend=False)
layout2 = go.Layout(plot_bgcolor='rgb(26,26,26)',
                    paper_bgcolor='rgb(26,26,26)',
                    font_color='white',
                    hovermode='closest')
fig2 = go.Figure(data=[trace_1], layout=layout2)

# Step 3. Create a plotly figure
layout = cf.Layout(
    legend=dict(
        orientation='h',
        y=1,
        xanchor='center',
        x=0.4),
    margin={'t': 0},
    plot_bgcolor='rgb(26,26,26)',
    paper_bgcolor='rgb(26,26,26)',
    font_color='white',
    font_size=11
)

# aggregating the data for plotting
regions = user_info.groupby('region').count()['user_id'].reset_index()
regions = regions.iplot(kind='pie', labels='region', values='user_id', asFigure=True, legend=False, theme='space',
                        title='% of Users by Region')

user_age = user_info.groupby(['region', 'age_range']).count()['user_id'].unstack()
user_age = user_age.iplot(kind='bar', theme='space', asFigure=True, xTitle='age range', yTitle='number of users',
                          title='Age Demographic by Region')

ui_gender = user_info.groupby(['region', 'gender']).count()['user_id'].unstack()
ui_gender = ui_gender.iplot(kind='bar', asFigure=True, xTitle='gender', yTitle='number of users', theme='space',
                            title='Gender Demographic by Region', layout=layout)

genre_graph = df_genre.groupby(['region', 'genre_1']).sum()['session_counts'].unstack()
genre_graph = genre_graph.iplot(kind='bar', asFigure=True, xTitle='Genre', yTitle='number of sessions', theme='space',
                            title='Genres by Region', layout=layout)
# PAGE 2

web_usage_date_fig = web_usage.groupby(['date', 'region'])['session_id'].count().unstack().iplot(kind='scatter',
                                                                                                 asFigure=True,
                                                                                                 title='Sessions_by Day',
                                                                                                 layout=layout)

# Step 4. Create a Dash layout
app.layout = html.Div([
    html.Div(
        style={'backgroundColor': 'rgb(26,26,26)',
               'color': 'white', },
        children=
        [
            html.H3(children='BBC iPlayer Analysis | By Xinping Pan',
                    style={'backgroundColor': 'rgb(26,26,26)',
                           'color': 'white',
                           'padding': '0px 10px 10px 10px'},
                    className='nine columns'),
            html.Img(
                src="https://bbc-uploads.s3.amazonaws.com/eR4dsalRcPhqjkqdSg8rfs6t7t10daS729t0h6nnpnddRdokc2ott7qsibk.png",
                className='three columns',
                style={
                    'max-height': 'auto',
                    'max-width': '60px',
                    'float': 'right',
                    'position': 'relative',
                    'margin-top': 10,
                    'margin-right': 10
                },
            )
        ], className="row"
    ),
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(
            label='Regional User Breakdown',
            value='tab-1',
            className='custom-tab',
            selected_className='custom-tab--selected',
        ),
        dcc.Tab(
            label='Regional Viewing Trends',
            value='tab-2',
            className='custom-tab',
            selected_className='custom-tab--selected'
        ),
    ], parent_className='custom-tabs', className='custom-tabs-container', ),
    html.Div(id='tabs-content')
])


# call backs
@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div(
            html.Div([
                html.Div(  # TOP GRAPH BLOCK
                    className='row',
                    style={'backgroundColor': 'rgb(26,26,26)',
                           'padding': '0px 10px 10px 10px'},
                    children=[
                        html.Div([
                            dcc.Graph(id='regions-graph',
                                      figure=regions)
                        ], className='five columns'),
                        html.Div([
                            dcc.Graph(id='gender-graph',
                                      figure=ui_gender)
                        ], className='seven columns')

                    ]),

                html.Div(  # BOTTOM GRAPH
                    className="row",
                    style={'backgroundColor': 'rgb(26,26,26)',
                           'padding': '0px 10px 10px 10px'},
                    children=
                    [
                        html.Div([
                            dcc.Graph(
                                id='map-graph',
                                figure=user_age
                            )
                        ], className='twelve columns'
                        ),
                    ]
                )
            ], className='twelve columns')
        )
    elif tab == 'tab-2':
        return html.Div(
            html.Div([
                html.Div([
                    # DROP DOWN
                    html.P([
                        dcc.Dropdown(id='opt', options=g2_opts,
                                     value=g2_opts[0]['value'])
                    ], style={'width': '400px',
                              'fontSize': '20px',
                              'padding-left': '100px', }),
                ], className='row'),

                # GRAPHS Top
                html.Div(className="row",
                         style={'backgroundColor': 'rgb(26,26,26)',
                                'padding': '0px 10px 10px 10px'},
                         children=
                         [  # REGIONAL OVERVIEW
                             html.Div([
                                 dcc.Graph(
                                     id='graph-1',
                                     figure=fig2
                                 )], className='six columns'
                             ),
                             html.Div([
                                 # IPlayer most popular
                                 dash_table.DataTable(
                                     id='datatable-filtering-fe',
                                     columns=[
                                         {"name": i, "id": i, "deletable": True} for i in most_popular.columns
                                     ],
                                     data=most_popular.to_dict('records'),
                                     filter_action="native",
                                     style_table={
                                         'maxHeight': '300px',
                                         'overflowY': 'scroll',
                                         'textOverflow': 'ellipsis',
                                         'color': 'white',
                                         'backgroundColor': 'rgb(26,26,26)',
                                         'fontWeight': 'bold'
                                     },
                                     style_as_list_view=True,
                                     style_header={'backgroundColor': 'rgb(26, 26, 26)'},
                                     style_cell={
                                         'backgroundColor': 'rgb(26,26,26)',
                                         'color': 'white',
                                     },
                                     style_filter={
                                         'backgroundColor': '#808080'
                                     },
                                 ),
                                 html.Div(id='datatable-filter-container')
                             ], className='six columns'
                             ),
                         ]
                         ),
                # GRAPHS MIDDLE
                html.Div(className="row",
                         children=
                         [  # IPLAYER usage OVERVIEW
                             html.Div([
                                 dcc.Graph(
                                     id='genre-graph',
                                     figure=genre_graph
                                 )
                             ], className='twelve columns'
                             ),
                         ],
                         ),
                # Regional Daily Graph
                html.Div(className="row",
                         children=
                         [
                             html.Div([
                                 dcc.Graph(
                                     id='daily-graph',
                                     figure=web_usage_date_fig
                                 )
                             ], className='twelve columns'
                             ),
                         ],
                         )
            ], className='twelve columns'),

        )


# Step 5. Add callback functions
@app.callback(Output('graph-1', 'figure'),
              [Input('opt', 'value')])
def update_figure(input1):
    trace_1 = go.Pie(labels=grouped.region, values=grouped[input1],
                     name=input1, hole=.3)
    layout_update = go.Layout(title='{} by region'.format(input1),
                              hovermode='closest',
                              plot_bgcolor='rgb(26,26,26)',
                              paper_bgcolor='rgb(26,26,26)',
                              font_color='white',
                              )
    fig2 = go.Figure(data=[trace_1], layout=layout_update)
    return fig2

@app.callback(
    Output('datatable-filter-container', "children"),
    [Input('datatable-filtering-fe', "data")])
def update_graph(rows):
    if rows is None:
        dff = most_popular
    else:
        dff = pd.DataFrame(rows)

    return html.Div()

if __name__ == '__main__':
    app.run_server(debug=True)
