import pandas as pd 
import dash 
from dash import dcc, html, Input ,Output
import dash_bootstrap_components as dbc 
import plotly.express as px 
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Data Preprocessing 
data=pd.read_csv('KaggleV2-May-2016.csv')
coords_df = pd.read_csv("neighborhood_coordinates.csv") 

#explore data
data.head()
data.dtypes
data.describe(include='all')
data.isna().sum()
data.info()
data.shape

data['ScheduledDay']=pd.to_datetime(data['ScheduledDay'])
data['AppointmentDay']=pd.to_datetime(data['AppointmentDay'])
data['days_between']=(data['AppointmentDay']-data['ScheduledDay']).dt.days
data['appointment_weekday']=data['AppointmentDay'].dt.day_name()
data['scheduled_weekday']=data['ScheduledDay'].dt.day_name()
# 0 didn't show up , 1 show up 
data['No-show']=data['No-show'].map({'Yes': 0,'No':1})
data['Gender']=data['Gender'].map({'F': 'Female', 'M': 'Male'})

data['SMS_received'] = data['SMS_received'].astype(bool)
data['Scholarship'] = data['Scholarship'].astype(bool)

#remove duplicates if exists
data.drop_duplicates(inplace=True)

data['Age'].describe()
data['days_between'].describe()

# remove unvalid age 
data[data['Age']<0]
data=data[data['Age']>=0]
# remove days_between that is larger than zero
data=data[data['days_between']>=0]
#count how many chronic conditions each patient has
data['Hypertension']=data['Hipertension']
# data['Hipertension'].drop()
conditions = ['Diabetes','Hypertension','Alcoholism']
data['n_chronic'] = data[conditions].sum(axis=1)
# print(data.head())



#cards calculations
total_appointments=len(data['AppointmentDay'])
num_patients=data['PatientId'].nunique()
no_show_count=data[data['No-show']==0]['PatientId'].value_counts()
repeated_no_show= (no_show_count>1).sum()

######################################VISUALIZATION###########################

##GET THE NEIGHBORHOODS COORDINATES AND SAVE AS A CSV FILE 
# neighborhoods = data['Neighbourhood'].unique()
# #setup geocoder
# geolocator = Nominatim(user_agent="my_geocoder")

# #increase timeout
# geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=3, error_wait_seconds=5, swallow_exceptions=False)

# #store results
# coords = []
# for place in neighborhoods:
#     query = f"{place}, Vitória, Espírito Santo, Brazil"
#     location =geolocator.geocode(query, timeout=10)
#     if location:
#         coords.append((place, location.latitude, location.longitude))
#     else:
#         coords.append((place, None, None))

# #Save to CSV
# coords_df = pd.DataFrame(coords, columns=["Neighborhood", "Latitude", "Longitude"])
# coords_df.to_csv("neighborhood_coordinates.csv", index=False)
# print("Coordinates saved to neighborhood_coordinates.csv")

colors = [
    "#33C3F0", 
    "#FF4DA6", 
]

####Handicap chart#########
handcap_rate=data.groupby('Handcap')['No-show'].apply(lambda x:(x==0).mean()*100).reset_index(name='no_show_count')
handcap_rate['Handcap'] = handcap_rate['Handcap'].map({0: 'No Handicap', 1: 'Handicap'})
Handicap_fig=px.bar(handcap_rate,
                        x='Handcap',
                        y='no_show_count',
                        labels={'no_show_count': 'No-Show Rate (%)', 'Handicap': 'Handicap Status'},
                        title='No-Show Rate by Handicap',
                        color='Handcap',
                        color_discrete_sequence=['#33C3F0', '#FF4DA6'])
Handicap_fig.update_layout(
    template='plotly_dark',
    paper_bgcolor='#181830',
    plot_bgcolor='#181830',
    font_color='white',
    yaxis=dict(ticksuffix="%") 
)

#####chronic or not no show rate chart ##########
data['chronic_status']=data['n_chronic'].apply(lambda x :'Chronic Condition' if x>0 else 'No Chronic Condition')
chronic_rate=data.groupby('chronic_status')['No-show'].apply(lambda x:(x==0).mean()*100).reset_index(name='no_show_rate')
Chronic_fig=px.bar(chronic_rate,
                   x='chronic_status',
                   y='no_show_rate',
                   labels={'no_show_rate':'No-Show Rate (%)','chronic_status':'Chronic Condition Status'},
                   title='No-Show Rate : Chronic vs. Non-Chronic Conditions',
                    color_discrete_sequence=["#FF4DA6"] 
                   )
Chronic_fig.update_layout(
    template='plotly_dark',
    paper_bgcolor='#181830',
    plot_bgcolor='#181830',
    font_color='white',
    yaxis=dict(ticksuffix="%") )

#####sms chart ########
sms_counts=data.groupby(['SMS_received','No-show']).size().reset_index(name='count')
sms_counts['SMS_received'] = sms_counts['SMS_received'].map({True: 'Received SMS', False: 'No SMS'})
sms_counts['No-show'] = sms_counts['No-show'].map({1: 'Showed Up', 0: 'No Show'})
sms_fig = px.bar(
    sms_counts,
    x='SMS_received',
    y='count',
    color='No-show',
    barmode='group', 
    labels={'count':'Number of Appointments','SMS_received': 'SMS Reminder'},
    title='Show vs. No Show by SMS Reminder',
    color_discrete_map={'Showed Up': "#33C3F0", 'No Show': "#FF4DA6"}
)
sms_fig.update_layout(
    template='plotly_dark',
    paper_bgcolor='#181830',
    plot_bgcolor='#181830',
    font_color='white'
)

#no-show rate per weekday chart
appointments_rate =(data.groupby('appointment_weekday')['No-show'].apply(lambda x: (x == 0).mean() * 100).reset_index(name='no_show_rate')
)
day_fig = px.bar(
    appointments_rate,
    x='appointment_weekday',
    y='no_show_rate',
    labels={'no_show_rate': 'No-show Rate (%)', 'appointment_weekday': 'Appointment Weekday'},
    title='No-show Rate by Day of the Week',
    color_discrete_sequence=["#FF4DA6"] 
)
day_fig.update_layout(
    template='plotly_dark',
    paper_bgcolor='#181830',
    plot_bgcolor='#181830',
    font_color='white',
    yaxis=dict(ticksuffix="%") 
)


###scholarship chart###
scholarship_rate=(data.groupby('Scholarship')['No-show'].apply(lambda x:(x == 0).mean()* 100).reset_index(name='no_show_rate'))
scholarship_fig=px.bar(scholarship_rate,x='Scholarship',y='no_show_rate',
                       labels={'no_show_rate': 'No-show Rate (%)'},
                                title='No-show Rate by Scholarship',
                                color_discrete_sequence=["#FF4DA6"])
scholarship_fig.update_layout(
    template='plotly_dark',
    paper_bgcolor='#181830',
    plot_bgcolor='#181830',
    font_color='white',
    yaxis=dict(ticksuffix="%") 
)


###for neighboorhood map
no_show_stats = data.groupby('Neighbourhood')['No-show'].apply(
lambda x: (x == 0).mean() * 100).reset_index(name='no_show_rate')
merged_df = no_show_stats.merge(coords_df, left_on='Neighbourhood', right_on='Neighborhood')

#create app
app=dash.Dash(__name__,external_stylesheets=[dbc.themes.DARKLY])

########################create app layout ############################
app.layout = dbc.Container([
    html.H1("Medical Appointment Dashboard",
            style={'textAlign': 'center', 'color': '#F72585', 'marginBottom': '36px'}),
    dbc.Row([  # First Row
        # LEFT COLUMN: KPI cards and pie chart
        dbc.Col([
            # KPI cards row 
            dbc.Row([

                dbc.Col(dbc.Card([
                    dbc.CardHeader("Total Appointments", style={'color': 'yellow'}),
                    dbc.CardBody(html.H4(total_appointments,className='card-title'))
                ], color='dark',inverse=True,className='h-100'), width=4,className='h-100'),

                dbc.Col(dbc.Card([
                    dbc.CardHeader("Number of Patients", style={'color': 'cyan'}),
                    dbc.CardBody(html.H4(num_patients,className='card-title'))
                ], color='dark',inverse=True,className='h-100'), width=4,className='h-100'),

                dbc.Col(dbc.Card([
                    dbc.CardHeader("Repeated No-shows", style={'color': 'magenta'}),
                    dbc.CardBody(html.H4(repeated_no_show,className='card-title'))
                ], color='dark',inverse=True,className='h-100'), width=4,className='h-100'),

            ], className="mb-4",justify="around"),

            dbc.Row([  # Pie chart 
                dbc.Col(dcc.Graph(id='pie_fig'), width=12)
            ]),
        ], width=4, style={'minWidth': '340px','align':"stretch"}),

        # RIGHT COLUMN: age/gender
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Dropdown(id="gender-filter",
                                 options=[{"label": "Male", "value": "Male"}, {"label": "Female", "value": "Female"}],
                                 placeholder="Select Gender"),
                    dcc.Graph(id='age-distribution')
                ])
            ], className="mb-4"),
        ], width=8)
    ]),
    dbc.Row([ #second row 
            dbc.Col( dcc.Graph(id='Handicap-chart',figure=Handicap_fig), width=6,style={'height': '440px'}),

            dbc.Col( dcc.Graph(id="Chronic-chart",figure=Chronic_fig), width=6,style={'height': '440px'}),

        ],className='mb-4'),
    dbc.Row([ #third row 
            dbc.Col( dcc.Graph(id='sms-chart',figure=sms_fig), width=4,style={'height': '440px'}),

            dbc.Col( dcc.Graph(id="days-chart",figure=day_fig), width=4,style={'height': '440px'}),

            dbc.Col([html.H4("Chronic Conditions"),
                     dcc.Dropdown(id='chronic-filter',
                                  options=[{'label':condition,'value':condition} for condition in conditions]),
                dcc.Graph(id="chronic-chart")], width=4,style={'height':'400px'})
        ],className='mb-4'),

    dbc.Row([ #forh Row   
        
        dbc.Col([
            html.H4('ScholarShip Analysis'),
            dcc.Graph(id='Scholarship-chart',figure=scholarship_fig)
        ],width=4,style={'height': '440px'}),

            dbc.Col([
                html.H4('days between'),
                dcc.Slider(
                    id='days-between-slider',
                    min=data['days_between'].min(),
                    max=data['days_between'].max(),
                    step=6,
                    value=data['days_between'].mean(),
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
                dcc.Graph(id='days-between-chart')
            ],width=8,style={'height': '400px'})
    ],style={'marginTop': '60px'}),

    dbc.Row( # fifth Row 
        dbc.Col([
            html.H4('Neighborhood Map'),
            dcc.RadioItems(id="chart-type" ,
                            options=[{"label":"Geographic Chart","value":"geographic"},{"label":"Bar Chart","value":"bar"}],
                            value="geographic",
                            className='mb-3',
                            labelStyle={'display': 'inline-block', 'margin-right': '25px'}),
            dcc.Dropdown(id='neighborhood-filter',
                options=[{'label': n, 'value': n} for n in sorted(merged_df['Neighbourhood'].unique())],
            ),
            dcc.Graph(id='neighborhood-chart')
        ],style={'marginTop': '60px','height': '500px'})
    )

], fluid=True, style={'backgroundColor': '#181830', 'padding': '24px'})

#########################################handling callbacks############################
@app.callback(
    Output('age-distribution','figure'),
    Input('gender-filter','value')
)
def update_age_distribution(selected_gender):
    gender_colors = {'Female': '#FF4DA6', 'Male': '#33C3F0'}
    if selected_gender:
        df_filterd=data[data['Gender']==selected_gender]
    else:
        df_filterd=data
    fig = px.histogram(
        df_filterd,
        x='Age',
        nbins=30,
        color='Gender',
        title='Age Distribution by Gender',
        opacity=0.8,color_discrete_map=gender_colors
)
    fig.update_layout(
        paper_bgcolor="#1A1338",     
        plot_bgcolor="#1A1338")
    return fig


@app.callback(
        Output('pie_fig','figure'),
        Input('gender-filter','value')
)
def update_no_show(selected_gender):
    if selected_gender:
        df_filtered=data[data['Gender']==selected_gender]
    else:
        df_filtered=data
    pie_counts = df_filtered['No-show'].value_counts().reset_index()
    pie_counts['No-show'] = pie_counts['No-show'].map({1: 'Show', 0: 'No Show'})
    pie_fig = px.pie(
        pie_counts,
        values='count',
        names='No-show',
        hole=0.4,
        color='No-show',
        title="Show vs. No Show Rate",
        color_discrete_sequence=colors)

    pie_fig.update_layout(
        paper_bgcolor='#181830',
        plot_bgcolor='#181830',
        font_color='white'
    )
    return pie_fig


@app.callback(
    Output('chronic-chart','figure'),
    Input('chronic-filter','value')
)
def update_chronic_chart(selected_condition):
    if selected_condition:
        df_filtered = data[data[selected_condition] == 1]
    else:
        df_filtered = data[data[conditions].sum(axis=1) > 0]

    df_filtered['Show Status'] = df_filtered['No-show'].map({0: 'No Show', 1: 'Show'})
    total = len(df_filtered)
    rate_df = df_filtered.groupby('Show Status').size().reset_index(name='Count')
    rate_df['Rate (%)'] = (rate_df['Count'] / total) * 100

    fig = px.bar(
        rate_df,
        x='Show Status',
        y='Rate (%)',
        color='Show Status',
        color_discrete_map={'Show': '#33C3F0', 'No Show': '#FF4DA6'},
        title=f'Show vs No Show Rate for {selected_condition if selected_condition else "All Conditions"}',
        labels={'Rate (%)': 'Attendance Rate (%)', 'Show Status': 'Attendance'}
    )

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='#181830',
        plot_bgcolor='#181830',
        font_color='white',
        yaxis=dict(ticksuffix="%")
    )

    return fig



@app.callback(
    Output('days-between-chart', 'figure'),
    Input('days-between-slider', 'value')
)
def update_days_between_chart(max_days):
    filtered = data[data['days_between'] <= max_days].copy()
    filtered['Show Status'] = filtered['No-show'].map({0: 'No Show', 1: 'Show'})

    counts_df = filtered.groupby(['days_between', 'Show Status']).size().reset_index(name='Count')

    fig = px.line(
        counts_df,
        x='days_between',
        y='Count',
        color='Show Status',
        markers=True,
        color_discrete_map={'Show': '#33C3F0', 'No Show': '#FF4DA6'},
        title=f'Number of Patients Showing and Not Showing by Days Between Scheduling and Appointment (<= {max_days} days)',
        labels={'days_between': 'Days Between Scheduling and Appointment', 'Count': 'Number of Patients'}
    )

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='#181830',
        plot_bgcolor='#181830',
        font_color='white'
    )
    return fig


@app.callback(
    Output('neighborhood-chart', 'figure'),
    [Input('neighborhood-filter','value'),
    Input('chart-type','value')]
)
def update_neighborhood(selected_neighborhood,selected_chart):
    if selected_chart =='geographic':
        if selected_neighborhood:
            plot_df = merged_df[merged_df['Neighborhood'] == selected_neighborhood]
            zoom_level = 14  
            center_lat = plot_df['Latitude'].iloc[0]
            center_lon = plot_df['Longitude'].iloc[0]
        else:
            plot_df = merged_df.copy()
            zoom_level = 11 
            center_lat = plot_df['Latitude'].mean()
            center_lon = plot_df['Longitude'].mean()

        fig = px.scatter_mapbox(
            plot_df,
            lat="Latitude",
            lon="Longitude",
            size="no_show_rate",
            color="no_show_rate",
            color_continuous_scale=px.colors.sequential.Plasma,
            hover_name="Neighborhood",
            hover_data={"no_show_rate": True, "Latitude": False, "Longitude": False},
            zoom=zoom_level,
            height=700,
            size_max=30,
            range_color=[0,40]
        )

        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox_center={"lat": center_lat, "lon": center_lon},
            title="No-show Rate by Neighborhood",
            paper_bgcolor="#181830"
        )
    else:
        Neighbourhood_counts=data.groupby(['Neighbourhood','No-show']).size().reset_index(name='count')
        Neighbourhood_counts['No-show'] = Neighbourhood_counts['No-show'].map({1: 'Showed Up', 0: 'No Show'})
        fig = px.bar(
            Neighbourhood_counts,
            x='Neighbourhood',
            y='count',
            color='No-show',
            labels={'count':'Number of Appointments','Neighbourhood': 'Neighbourhood'},
            title='Show vs. No Show by Neighbourhood',
            color_discrete_map={'Showed Up': "#33C3F0", 'No Show': "#FF4DA6"})
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='#181830',
            plot_bgcolor='#181830',
            font_color='white'
        )
   

    return fig

if __name__ == '__main__':

    app.run(debug=True)
