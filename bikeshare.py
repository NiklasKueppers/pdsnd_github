import numpy as np
import pandas as pd
import time

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

#### other functions #####

#check data type and print first/last rows
def check_type(input):
    print(input.dtypes)
    print(input.head(5))
    print(input.tail(5))

# Load all csvs and append them
def load_data():
    data1 = pd.read_csv('Data\chicago.csv')
    data1['City'] = ['chicago'] * data1.shape[0]
    data2 = pd.read_csv('Data\\new_york_city.csv')
    data2['City'] = ['ny'] * data2.shape[0]
    data3 = pd.read_csv('Data\washington.csv')
    data3['City'] = ['washington'] * data3.shape[0]

    data = data1.append(data2, ignore_index=True, sort=True)
    data = data.append(data3, ignore_index=True, sort=True)
    return data

# Arrange data
def arrange_data(data):
    #this is not nicly done currently
    data.drop(['Unnamed: 0'], axis=1, inplace=True)

    data['Start Time'] = pd.to_datetime(data['Start Time'])
    data['End Time'] = pd.to_datetime(data['End Time'])
    data['Mid Time'] = (data['Start Time']
                        + pd.to_timedelta(data['Trip Duration']/2, unit='s'))

    # Extract hour/days/month & delete timestamps
    data['Hour'] = data['Mid Time'].dt.hour
    data['Day'] = data['Mid Time'].dt.weekday_name
    data['Month'] = data['Mid Time'].dt.month

    data.drop(['Start Time', 'End Time', 'Mid Time'], axis=1, inplace=True)

    # add NaN if Gender is not available
    if 'Gender' not in data.columns:
        data['Gender'] = np.empty((data.shape[0], 1))
        data['Gender'] = np.nan

    # add Birth Year if not available & replace with 0
    if 'Birth Year' in data.columns:
        data['Birth Year'] = np.nan_to_num(data['Birth Year']).astype(int)
    else:
        data['Birth Year'] = np.zeros((data.shape[0], 1), dtype=int)

    #data.drop(['Start Station', 'End Station'], axis=1, inplace=True)
    return data

# Group by Gender
def groupby_gender(sorted_data):
    try:
        grbg = sorted_data.groupby(['Gender']).size()
        grbg['No Value'] = sorted_data.shape[0]-sum(grbg)

    except Exception as e:
        grbg = pd.Series([0, 0], index=['Female', 'Male'])
        grbg['No Value'] = sorted_data.shape[0]

    return grbg

# Group by User Type
def groupby_user(sorted_data):
    try:
        grbu = sorted_data.groupby(['User Type']).size()
        if sorted_data.shape[0]-sum(grbu) > 0:
            grbu['No Value'] = sorted_data.shape[0]-sum(grbu)

    except Exception as e:
        grbu = pd.Series([0, 0], index=['Customer', 'Subscriber'])
        grbu['No Value'] = sorted_data.shape[0]

    return grbu





# Load data
data = load_data()
# Arrange Data
data = arrange_data(data)

# Load some css sheet (see Dash Docu)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Init App (see Dash Docu)
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# User defined Colors
colors = {
        'text': '#009999',
        'mark': '#990000',
        'nrml' : '#009988',
        'pie1' : '#cc6110',
        'pie2' : '#6b9900',
        'grey' : '#aebfbd'
        }

# Some more css (might be uneccessary...)
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

####### HTML Body (maybe) ########
app.layout = html.Div(children=[
    html.H1(children='Explore US Bikeshare Data',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
    ),
    html.Label('Choose City:'),
    dcc.Dropdown(
        id='city_menu',
        options=[
            {'label': 'New York City', 'value': 'ny'},
            {'label': 'Washington', 'value': 'washington'},
            {'label': 'Chicago', 'value': 'chicago'}
        ],
        value='washington'
    ),
    html.Div([
        html.Div(
            dcc.Graph(id='1'), className="four columns"
        ),
        html.Div(
            dcc.Graph(id='2'), className="four columns"
        ),
        html.Div(
            dcc.Graph(id='3'), className="four columns"
        )
    ]),
    html.Hr(),
    html.Div([
        html.Div(
            dcc.Graph(id='4', className="four columns")
        ),
        html.Div(
            dcc.Graph(id='5', className="four columns")
        ),
        html.Div(
            html.H6(id='text', className="four columns")
        )
    ]),
    html.Hr(),
    html.Div([
        html.Div(
            dcc.Graph(id='6', className="nine columns")
        ),
        html.Div(
            html.H6(id='text1', className="three columns")
        )
    ])
])

####### End of HTML Body #######


####### Update all Figures & Text #######

# is there a way to update all figures at once?
# update of figure is repetitive, how can this be improved?

# Update Figure 1
@app.callback(
    dash.dependencies.Output('1', 'figure'),
    [dash.dependencies.Input('city_menu', 'value')])

def update_figure1(selected_city):
    sorted_data = data.loc[data['City'] == selected_city]
    grbh = sorted_data.groupby(['Hour']).size()
    clrs = [colors['mark'] if grbh[i] == max(grbh) else colors['nrml']
                for i in grbh.index.values]
    return {
        'data': [
            {'x': grbh.index.values, 'y': grbh.values,
             'type': 'bar',
             'name': 'hourly',
             'marker': dict(color=clrs)
             }
        ],
        'layout':{
            'title': 'Hourly Trips',
            'yaxis': {'title': 'Number of Trips'}
        }
    }


# Update Figure 2
@app.callback(
    dash.dependencies.Output('2', 'figure'),
    [dash.dependencies.Input('city_menu', 'value')])

def update_figure2(selected_city):
    sorted_data = data.loc[data['City'] == selected_city]
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday',
            'Saturday', 'Sunday']
    grbd = sorted_data.groupby(['Day']).size().reindex(days)
    clrs = [colors['mark'] if grbd[i] == max(grbd) else colors['nrml']
                for i in grbd.index.values]
    return {
        'data': [
            {'x': grbd.index.values, 'y': grbd.values,
             'type': 'bar',
             'name': 'daily',
             'marker': dict(color=clrs)
             }
        ],
        'layout':{
            'title': 'Daily Trips',
            'yaxis': {'title': 'Number of Trips'}
        }
    }


# Update Figure 3
@app.callback(
    dash.dependencies.Output('3', 'figure'),
    [dash.dependencies.Input('city_menu', 'value')]
)

def update_figure3(selected_city):
    sorted_data = data.loc[data['City'] == selected_city]
    grbm = sorted_data.groupby(['Month']).size()
    clrs = [colors['mark'] if grbm[i] == max(grbm) else colors['nrml']
                for i in grbm.index.values]
    return {
        'data': [
            {'x': grbm.index.values, 'y': grbm.values,
             'type': 'bar',
             'name': 'monthly',
             'marker': dict(color=clrs)
             }
        ],
        'layout':{
            'title': 'Monthly Trips',
            'yaxis': {'title': 'Number of Trips'}
        }
    }


# Update Figure 4
@app.callback(
    dash.dependencies.Output('4', 'figure'),
    [dash.dependencies.Input('city_menu', 'value')]
)

def update_figure4(selected_city):
        sorted_data = data.loc[data['City'] == selected_city]
        grbg = groupby_gender(sorted_data).sort_values(ascending=False)
        clrs = [colors['pie1'] if grbg.index[i] == 'Female'
                else (colors['pie2'] if grbg.index[i] == 'Male'
                    else colors['grey']) for i in range(grbg.shape[0])]
        #print(clrs)
        return {
            'data': [
                {'values': grbg.values,
                 'labels': grbg.index.values,
                 'type': 'pie',
                 'marker': dict(colors=clrs)
                }
            ],
            'layout':{
                'title': 'Gender'
            }
        }


# Update Figure 5
@app.callback(
    dash.dependencies.Output('5', 'figure'),
    [dash.dependencies.Input('city_menu', 'value')]
)

def update_figure5(selected_city):
        sorted_data = data.loc[data['City'] == selected_city]
        grbu = groupby_user(sorted_data)
        clrs = [colors['pie1'] if grbu.index[i] == 'Subscriber'
                else (colors['pie2'] if grbu.index[i] == 'Customer'
                    else colors['grey']) for i in range(grbu.shape[0])]
        return {
            'data': [
                {'values': grbu.values,
                 'labels': grbu.index.values,
                 'type': 'pie',
                 'marker': dict(colors=clrs)
                }
            ],
            'layout':{
                'title': 'User Type'
            }
        }

# Update Text
@app.callback(
    dash.dependencies.Output('text', 'children'),
    [dash.dependencies.Input('city_menu', 'value')]
)

def update_text(selected_city):
        sorted_data = data.loc[data['City'] == selected_city]
        ttl_time = int(round(sorted_data['Trip Duration'].sum() / 3600))
        avg_time= int(round(sorted_data['Trip Duration'].mean() / 60))
        grbst = sorted_data.groupby(['Start Station'], sort=True)\
                    .size().reset_index(name='count')\
                    .sort_values(['count'], ascending=False)\
                    .head(1)
        grbes = sorted_data.groupby(['End Station'], sort=True)\
                    .size().reset_index(name='count')\
                    .sort_values(['count'], ascending=False)\
                    .head(1)
        grbcmb = sorted_data.groupby(['Start Station','End Station'])\
                    .size().reset_index(name='count')\
                    .sort_values(['count'], ascending=False)\
                    .head(1)

        return (html.P("Total Travel Time: " + str(ttl_time) + " hours"),
                html.P("Average Travel Time: " + str(avg_time)+ " minutes"),
                html.P("Most popular start station:\t "
                    + grbst['Start Station'].iloc[0]),
                html.P("Most popular end station:\t "
                    + grbes['End Station'].iloc[0]),
                html.P("Most common trip from:\t "
                    + grbcmb['Start Station'].iloc[0]),
                html.P("To: \t" + grbcmb['End Station'].iloc[0])
                )

# Update Figure 6
@app.callback(
    dash.dependencies.Output('6', 'figure'),
    [dash.dependencies.Input('city_menu', 'value')]
)

def update_figure6(selected_city):
        sorted_data = data.loc[data['City'] == selected_city]
        grba = sorted_data.groupby(['Birth Year']).size()
        grba = grba[grba.index.values != 0]
        clrs = [colors['mark'] if grba[i] == max(grba) else colors['nrml']
                    for i in grba.index.values]
        return {
            'data': [
                {'x': grba.index.values, 'y': grba.values,
                 'type': 'bar',
                 'name': 'age',
                 'marker': dict(color=clrs)
                 }
            ],
            'layout':{
                'title': 'Customer Age',
                'yaxis': {'title': 'Number of Customers'}
            }
        }

@app.callback(
    dash.dependencies.Output('text1', 'children'),
    [dash.dependencies.Input('city_menu', 'value')]
)

def update_text1(selected_city):
    sorted_data = data.loc[data['City'] == selected_city]
    grba = sorted_data.groupby(['Birth Year']).size()
    grba = grba[grba.index.values != 0]

    if grba.empty:
        return (
            html.P("No Data Available")
        )
    else:
        return (
            html.P("Oldest Customer is born in: " \
                    + str(min(grba.index.values))),
            html.P("Youngest Customer is born in: " \
                    + str(max(grba.index.values)))
        )





###### start server at local host #######
if __name__ == '__main__':
    app.run_server(debug=True)
