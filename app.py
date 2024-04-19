import pandas as pd 
import dash
from dash import Dash, dcc, html, callback
from dash.dependencies import Input, Output, State
import plotly.express as px
from dash import dash_table
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots

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
    'Auckland': '#C3BA27',
    'Biarritz': '#929292',
    'Berlin': '#FDA929',
    'Reykjavik': '#A9C7FC',
    'Vancouver': '#F0CBFD'
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


#table 
df_locations = pd.read_csv('./data/staging_location.csv')
population = [3677472, 25764, 706012, 136894, 1695200]
df_locations['population'] = population
table = dash_table.DataTable(df_locations.to_dict('records'),
                                  [{"name": i, "id": i} for i in df_locations.columns],
                               style_data={'font-family': "Helvetica", 'color': 'white','backgroundColor': "", 'font-size':'12px'},
                              style_header={'font-family': "Helvetica",'font-size':'12px',
                                  'backgroundColor': 'rgb(210, 210, 210)',
                                  'color': 'black','fontWeight': 'bold'}, 
                                     style_table={ 
                                         'minHeight': '400px', 'height': '400px', 'maxHeight': '400px',
                                         'minWidth': '600px', 'width': '600px', 'maxWidth': '600px',
                                         'marginLeft': 'auto', 'marginRight': '200px',
                                         'marginTop': 0, 'marginBottom': "30px"}
                                     )

#plots :

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
              ,height=800
              ,hover_name='avg_temp_c'
             ,color='avg_temp_c'
                ,color_continuous_scale='YlOrRd'
                ,range_color=[0, 25]
             ,animation_frame='city'
             ,text_auto=False
             ,range_y = (-3,22)
             ) 
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
                 title='Temperature distribution')

bar_temp.update_layout(**custom_template)
bar_temp.update_layout(showlegend=False)
fig_bar_season = dcc.Graph(figure=bar_temp)  


#TEMPERATURE BOXPLOT --------------------------
temp_cities = pd.read_csv('./data/mart_temp_monthly.csv')
temp_cities.sort_values(by='city', inplace=True)
box_temp = px.box(temp_cities,
                     y="avg_temp_c",
                     x='city',
                     color='city',
                     color_discrete_map=grey_colors,
                     height=800,
                     width=900,
                 title='Temperature distribution')
box_temp.update_layout(**custom_template)
box_temp.update_traces(line=dict(color='black', width=0.5))
# Add annotations for max and min temperatures
for city in temp_monthly['city'].unique():
    max_temp = temp_monthly[temp_monthly['city'] == city]['avg_temp_c'].max()
    min_temp = temp_monthly[temp_monthly['city'] == city]['avg_temp_c'].min()
    box_temp.add_annotation(x=city, y=max_temp, text=f"Max: {max_temp}°C", showarrow=True, font=dict(color='black'))
    box_temp.add_annotation(x=city, y=min_temp, text=f"Min: {min_temp}°C", showarrow=True, font=dict(color='black'))
box_temp.update_layout(showlegend=False)
fig_box = dcc.Graph(figure=box_temp)





# Create your Dash application instance
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Apply your custom CSS styles
app.css.append_css({"external_url": custom_css})

# Define your layout
app.layout = html.Div([
    html.H2([html.Span('WHERE WOULD BE AN IDEAL PLACE TO LIVE?')],
            style={'margin': '20px', 'width': '300px'}),
    html.Div('TIMEFRAME : 12.04.2023 — 11.04.2024',
             style={'margin': '20px', 'width': '300px'}),  # Set margin directly using the 'style' attribute
    html.Div([
        dcc.Markdown('''
        AUCKLAND — NEW ZEALAND  
        BERLIN — GERMANY  
        BIARRITZ — FRANCE  
        REYKJAVIK — ICELAND  
        VANCOUVER — CANADA  
        ''', dangerously_allow_html=True, style={'margin': '20px', 'width': '300px'})
    ]), table
    ,map_locations,
    fig_box
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
