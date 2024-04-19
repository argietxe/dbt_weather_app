import pandas as pd 
import dash
from dash import Dash, dcc, html, callback
from dash.dependencies import Input, Output, State
import plotly.express as px
from dash import dash_table
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Define your custom CSS styles
custom_css = '''
body {
    background-color: #f0f0f0; 
    color: #333; 
    font-family: "Helvetica", sans-serif;
}

h1, h2, h3, h4, h5, h6 {
    font-family: "Helvetica", sans-serif;
    color: black;
    margin-top: 20px;
    margin-bottom: 10px;
}
'''

# custome template
custom_template = {
    "paper_bgcolor": "white",  # Background color white
    "plot_bgcolor": "white",   # Background color white
    "font": {"color": "black", "size": 10},  # Ticks black and small
    "xaxis": {
        "showgrid": True,       # Grid visible
        "gridcolor": "#F0F0F0", # Very light grey
        "gridwidth": 0.5        # Very thin grid
    },
    "yaxis": {
        "showgrid": True,       # Grid visible
        "gridcolor": "#F0F0F0", # Very light grey
        "gridwidth": 0.5        # Very thin grid
    }
}

# custom color mappings
custom_colors = {
    'Auckland': '#C6082C', #C3BA27
    'Biarritz': '#C3921E', #929292
    'Berlin': '#230A2A', #FDA929
    'Reykjavik': '#8D2013', #A9C7FC
    'Vancouver': '#013C40' #F0CBFD
}

# custom_black
grey_colors = {
    'Auckland': '#A9A9A9',
    'Biarritz': '#A9A9A9',
    'Berlin': '#A9A9A9',
    'Reykjavik': '#A9A9A9',
    'Vancouver': '#A9A9A9'
    }

#for season color
season_colors = {
    'Winter': '#C7E2E7', #C3BA27
    'Spring': '#8A73A1', #929292
    'Summer': '#C3921E', #FDA929
    'Autumn': '#8D2013', #A9C7FC
}


#TABLE ----------------------------------- 
df_locations = pd.read_csv('./data/staging_location.csv')
population = [3677472, 25764, 706012, 136894, 1695200]
df_locations['population'] = population
table = dash_table.DataTable(df_locations.to_dict('records'),
                                  [{"name": i, "id": i} for i in df_locations.columns],
                               style_data={'font-family': "Helvetica", 'color': 'black','backgroundColor': "", 'font-size':'12px'},
                              style_header={'font-family': "Helvetica",'font-size':'12px',
                                  'backgroundColor': 'rgb(210, 210, 210)',
                                  'color': 'black','fontWeight': 'bold'}, 
                                     style_table={ 
                                         'minHeight': '400px', 'height': '400px', 'maxHeight': '400px',
                                         'minWidth': '600px', 'width': '600px', 'maxWidth': '600px',
                                         'marginLeft': '20px', 'marginRight': 'auto',
                                         'marginTop': 0, 'marginBottom': "30px"}
                                     )

#PLOTS:

#MAP -----------------------------------------
data_loc = df_locations 
px.set_mapbox_access_token('pk.eyJ1IjoiYXJnaXR4dSIsImEiOiJja2J3MzB5eWkwOWFzMnNsYjFyMWp0ZHJ5In0.ZgK1pLqzTStbmRem7ykywA')
map_s = px.scatter_mapbox(data_loc, 
                        lat="lat", 
                        lon="lon", 
                        hover_name="city",
                        custom_data=['region', 'country'],
                        hover_data={'lat': False, 'lon':False,'country':True, 'region':True, 'population': True}, #to custom the data shoving while hovering
                        size='population',
                        size_max=30,
                        color_discrete_sequence=['#A52A2A'],
                        opacity = 0.93,
                        zoom=0.7,
                        center={'lat': 30, 'lon': 13.4}, 
                        mapbox_style='stamen-toner',
                       height=700,
                       width=1000)
map_locations = dcc.Graph(figure=map_s)


#TEMPERATURE BAR PLOT MONTH--------------------
temp_monthly = pd.read_csv('./data/mart_temp_monthly.csv')
iso_code = pd.read_csv('./data/iso_codes.csv')
temp_monthly = temp_monthly.merge(iso_code, on='country', how='inner')
temp_monthly.head()
custom_dict_months = {'January  ':10, 'February ':11, 'March    ':12, 'April    ':1 
                    ,'May      ':2, 'June     ':3, 'July     ':4, 'August   ':5
                     ,'September':6, 'October  ':7, 'November ':8, 'December ':9}
temp_monthly= temp_monthly.sort_values(by='month_of_year', key=lambda x: x.replace(custom_dict_months))
warming_stripes = px.bar(data_frame=temp_monthly
              ,x='month_of_year'
              ,y='avg_temp_c'
              ,height=400
              ,width=400
              ,hover_name='avg_temp_c'
             ,color='avg_temp_c'
                ,color_continuous_scale='greys'
                ,range_color=[0, 25]
             ,animation_frame='city'
             ,text_auto=False
             ,range_y = (-3,22)
             ) 
warming_stripes.update_layout(**custom_template)
warming_stripes.update_yaxes(title_text="Average Temperature (°C)")
fig_bar_month =  dcc.Graph(figure=warming_stripes)



#TEMPERATURE BAR PLOT SEASONS------------------
#read data
temp_season = pd.read_csv('./data/mart_temp_season.csv')
temp_season.sort_values(by='city', inplace=True)
custom_dict_season = {'Winter':1 
                    ,'Spring':2, 'Summer':3, 'Autumn':4}
temp_season= temp_season.sort_values(by='season_name', key=lambda x: x.replace(custom_dict_season))
bar_temp = px.bar(temp_season,
                     y="avg_temp_c",
                     x='city',
                     color='season_name',
                      barmode='group',
                     color_discrete_map=season_colors,
                     height=400,
                     width=900,
                 title='Temperature Distribution per Season')

bar_temp.update_layout(**custom_template)
bar_temp.update_layout(showlegend=False)
bar_temp.update_yaxes(title_text="Average Temperature (°C)")
fig_bar_season = dcc.Graph(figure=bar_temp)  


#TEMPERATURE BOXPLOT MONTHLY ------------------------
temp_cities = pd.read_csv('./data/mart_temp_monthly.csv')
temp_cities.sort_values(by='city', inplace=True)
box_temp = px.box(temp_cities,
                     y="avg_temp_c",
                     x='city',
                     color='city',
                     color_discrete_map=grey_colors,
                     height=800,
                     #width=1000,
                 title='Distribution in a Year')
box_temp.update_layout(**custom_template)
box_temp.update_traces(line=dict(color='black', width=0.5))
box_temp.update_yaxes(title_text="Average Temperature (°C)")
box_temp.update_xaxes(title_text="City")
# Add annotations for max and min temperatures
for city in temp_monthly['city'].unique():
    max_temp = temp_monthly[temp_monthly['city'] == city]['max_temp_c'].max()
    min_temp = temp_monthly[temp_monthly['city'] == city]['min_temp_c'].min()
    box_temp.add_annotation(x=city, y=max_temp, text=f"Max: {max_temp}°C", showarrow=True, font=dict(color='black'))
    box_temp.add_annotation(x=city, y=min_temp, text=f"Min: {min_temp}°C", showarrow=True, font=dict(color='black'))
box_temp.update_layout(showlegend=False)
fig_temp_box = dcc.Graph(figure=box_temp)



#BARPLOT TEMPERATURE YEAR ------------------------------------------------------
temp_year = pd.read_csv('./data/prep_forecast_day.csv', parse_dates=['date'])
bar_temp_y = px.line(temp_year,
                     y="avg_temp_c",
                     x='date',
                     color='city',
                      #barmode='group',
                     color_discrete_map=custom_colors,
                     height=600,
                 title='Temperature distribution')

bar_temp_y.update_traces(marker_line_width = 0,
                  selector=dict(type="bar"))

bar_temp_y.update_layout(bargap=0,
                  bargroupgap = 0,
                 )
bar_temp_y.update_layout(**custom_template)
bar_temp_y.update_layout(showlegend=True)
fig_temp_y = dcc.Graph(figure=bar_temp_y)



#SUBLOT WEATHER CONDITIONS PER SEASON, INDEX CITIES ----------------------------
condition_text = pd.read_csv('./data/mart_condition_text_season.csv')
custom_dict = {'Winter':1, 'Spring':2, 'Summer':3, 'Autumn':4}
condition_text= condition_text.sort_values(by='season_name', key=lambda x: x.map(custom_dict))

sub = make_subplots(rows=2, cols=2)
sub.add_trace(go.Bar(               # Add bar trace to the subplot
    y=condition_text['season_name'],
    x=condition_text['sunny_days'],
    hovertext=condition_text['city'],
    #text=condition_text['season_name'],
    orientation='h',
    marker_color=[custom_colors[city] for city in condition_text['city']],  # Coloring by city
), row=1, col=1)

sub.add_trace(go.Bar(
    y=condition_text['season_name'],
    x=condition_text['cloudy_days'],
    hovertext=condition_text['city'],
    #text=condition_text['season_name'],
    orientation='h',
    marker_color=[custom_colors[city] for city in condition_text['city']],  # Coloring by city
), row=1, col=2)

sub.add_trace(go.Bar(
    y=condition_text['season_name'],
    x=condition_text['rainy_days'],
    hovertext=condition_text['city'],
    #text=condition_text['season_name'],
    orientation='h',
    marker_color=[custom_colors[city] for city in condition_text['city']],  # Coloring by city
), row=2, col=1)

sub.add_trace(go.Bar(
    y=condition_text['season_name'],
    x=condition_text['snowy_days'],
    hovertext=condition_text['city'],
    #text=condition_text['season_name'],
    orientation='h',
    marker_color=[custom_colors[city] for city in condition_text['city']],  # Coloring by city
), row=2, col=2)

sub.update_layout(
    width=1400,
    height=800,
    hovermode='closest',
    title={
        "text": "  ",
        "x": 0.5,  # Center the title
    },)

sub.update_xaxes(title_text="Sunny Days", row=1, col=1)     # Update x and y axes
sub.update_xaxes(title_text="Cloudy Days", row=1, col=2)
sub.update_xaxes(title_text="Rainy Days", row=2, col=1)
sub.update_xaxes(title_text="Snowy Days", row=2, col=2)
sub.update_layout(showlegend=False)
sub.update_layout(showlegend=False)
sub.update_layout(**custom_template)
sub_conditions = dcc.Graph(figure=sub) 

# LINEPLOT FOR SUNLIGHT -------------------------
sunlight_year = pd.read_csv('./data/sunlight_over_year.csv', parse_dates=['date','sunlight'])
sunlight = px.line(data_frame=sunlight_year
              ,x='date'
              ,y='sunlight'
              ,color='city'
              ,color_discrete_map=custom_colors
              ,height=800
              ,hover_name='date'
              ,markers=False
              ,title='from April 2023 to April 2024'
             ) 

sunlight.update_traces(line=dict(width=5)) #to change the thickness of the line
sunlight.update_layout(**custom_template)
line_sun = dcc.Graph(figure=sunlight) 

#DROPDOWN ------------------------------------------
dropdown_city = dcc.Dropdown(options=['Berlin', 'Biarritz', 'Auckland','Reykjavik','Vancouver'], value="Berlin", clearable=False) 

# Create your Dash application instance
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

# Apply your custom CSS styles
app.css.append_css({"external_url": custom_css})

# Define your layout
app.layout = html.Div([
    dbc.Row([
        html.H2([html.Span('WHERE WOULD BE AN IDEAL PLACE TO LIVE?')],
            style={'margin': '40px', 'width': '300px'}),
        html.Div('TIMEFRAME : 12.04.2023 — 11.04.2024',
             style={'margin': '40px', 'width': '1000px'}),  # Set margin directly using the 'style' attribute
        html.Div([
        dcc.Markdown('''        
            AUCKLAND — NEW ZEALAND  
            BERLIN — GERMANY  
            BIARRITZ — FRANCE  
            REYKJAVIK — ICELAND  
            VANCOUVER — CANADA  
            ''', dangerously_allow_html=True, style={'margin': '20px', 'width': '300px'})
    ], style={'margin': '20px', 'width':'40%', 'display':'inline-block'}),
        html.Div(table, style={'margin-right': '20px', 'width':'40%', 'display':'inline-block'}),
    ], style={'display': 'flex'}),
    map_locations,
    html.Div([
        html.H3([html.Span('TEMPERATURES')],
            style={'margin': '40px', 'width': '300px'}),
        dbc.Row([
            html.Div(fig_temp_box, style={'width':'70%', 'display':'inline-block'}),
            html.Div(fig_bar_month, style={'width':'60%', 'display':'inline-block', 'marginLeft': "900px"}),
        ]),
        dbc.Row([
            html.Div(fig_bar_season),
            html.Div(fig_temp_y, style={'width':'100%'}),
        ]),
        html.H3([html.Span('WHEATHER CONDITIONS')],
            style={'margin': '40px', 'width': '300px'}),
        dropdown_city,
        html.Div(sub_conditions),
    ]),
    html.Div([
        html.H3([html.Span('SUNLIGHT')],
            style={'margin': '40px', 'width': '300px'}),
        dbc.Row([
            html.Div(line_sun),
        ]),
    ]),
])


@callback(                            # or app@callback()    #you can make one callback influencing many figures too if you want.
    Output(sub_conditions, "figure"), 
    Input(dropdown_city, "value"))  

def update_subplot(city): 
    mask = condition_text["city"] == city # coming from the function parameter
    one_city = condition_text[mask]
    sub = make_subplots(rows=2, cols=2)
    sub.add_trace(go.Bar(              # Add bar trace to the subplot
        data=condition_text,
        y=condition_text['season_name'],
        x=condition_text['sunny_days'],
        hovertext=condition_text['city'],
        #text=condition_text['season_name'],
        orientation='h',
        marker_color=[custom_colors[city] for city in condition_text['city']],  # Coloring by city
    ), row=1, col=1)

    sub.add_trace(go.Bar(
        y=condition_text['season_name'],
        x=condition_text['cloudy_days'],
        hovertext=condition_text['city'],
        #text=condition_text['season_name'],
        orientation='h',
            marker_color=[custom_colors[city] for city in condition_text['city']],  # Coloring by city
    ), row=1, col=2)

    sub.add_trace(go.Bar(
        y=condition_text['season_name'],
        x=condition_text['rainy_days'],
        #hovertext=condition_text['city'],
        #text=condition_text['season_name'],
        orientation='h',
        marker_color=[custom_colors[city] for city in condition_text['city']],  # Coloring by city
    ), row=2, col=1)

    sub.add_trace(go.Bar(
        y=condition_text['season_name'],
        x=condition_text['snowy_days'],
        hovertext=condition_text['city'],
        text=condition_text['season_name'],
        orientation='h',
        marker_color=[custom_colors[city] for city in condition_text['city']],  # Coloring by city
    ), row=2, col=2)

    sub.update_layout(
        width=1000,
        height=800,
        hovermode='closest',
        title={
           "text": f"Weather condition in {city} ",
            "x": 0.5,  # Center the title
        },)

    sub.update_xaxes(title_text="Sunny Days", row=1, col=1)     # Update x and y axes
    sub.update_xaxes(title_text="Cloudy Days", row=1, col=2)
    sub.update_xaxes(title_text="Rainy Days", row=2, col=1)
    sub.update_xaxes(title_text="Snowy Days", row=2, col=2)
    sub.update_layout(showlegend=False)
    sub.update_layout(showlegend=False)
    sub.update_layout(**custom_template)

    return sub # whatever you are returning here is connected to the component property of
                       #the output which is figure

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
