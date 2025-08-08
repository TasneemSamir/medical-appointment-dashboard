import pandas as pd 
import dash 
from dash import dcc, html, Input ,Output
import dash_bootstrap_components as dbc 
import plotly.express as px 

# Data Preprocessing 
# Load dataset
data=pd.read_csv('KaggleV2-May-2016.csv')

#explore data
# data.head()
# data.dtypes
# data.describe(include='all')
# data.isna().sum()
# data.info()
# data.shape

# Parse dates
data['ScheduledDay']=pd.to_datetime(data['ScheduledDay'])
data['AppointmentDay']=pd.to_datetime(data['AppointmentDay'])
data['days_between']=(data['AppointmentDay']-data['ScheduledDay']).dt.days
data['appointment_weekday']=data['AppointmentDay'].dt.day_name()
data['scheduled_weekday']=data['ScheduledDay'].dt.day_name()
# 0 didn't show up , 1 show up 
data['No-show']=data['No-show'].map({'Yes': 0,'No':1})
# convert to boolean
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

###visualization####
colors = [
    "#33C3F0", 
    "#FF4DA6", 
]

########pie chart #####
pie_counts = data['No-show'].value_counts()
pie_fig = px.pie(
    values=pie_counts.values,
    names=['Show', 'No Show'],
    hole=0.4,
    color=pie_counts.index,
    title="Show vs. No Show Rate",
    color_discrete_sequence=colors)

pie_fig.update_layout(
    paper_bgcolor='#181830',
    plot_bgcolor='#181830',
    font_color='white'
)

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

###showing by day of the week###
appointments_count=data.groupby(['appointment_weekday','No-show']).size().reset_index(name='p_count')
appointments_count['No-show'] = appointments_count['No-show'].map({1: 'Showed Up', 0: 'No Show'})
day_fig=px.bar(
    appointments_count,
    x='appointment_weekday',
    y='p_count',
    color='No-show',
    labels={'p_count':'Number of Appointments','appointment_weekday': 'appointment weekday'},
    title='Days of the week Analysis',
    color_discrete_map={'Showed Up': "#33C3F0", 'No Show': "#FF4DA6"}
)
day_fig.update_layout(
    template='plotly_dark',
    paper_bgcolor='#181830',
    plot_bgcolor='#181830',
    font_color='white'
)

###scholarship chart###
data['Show Status'] = data['No-show'].map({0: 'No Show', 1: 'Show'})
scholarship_counts=data.groupby(['Scholarship','Show Status']).size().reset_index(name='count')
fig=px.bar(
    scholarship_counts,
    x='Scholarship',
    y='count',
    color='Show Status',
    barmode='group',
    title='Show vs No Show Counts by Scholarship Status',
    labels={'Count': 'Number of Appointments', 'Scholarship Status': 'Scholarship Status'},
    color_discrete_map={'Show': '#33C3F0', 'No Show': '#FF4DA6'}
)
fig.update_layout(
    template='plotly_dark',
    paper_bgcolor='#181830',
    plot_bgcolor='#181830',
    font_color='white'
)

#####spider chart#########
#prepare data 
# def prepare_data(data,col):
#     return data.groupby(col,group_keys=False).apply(
#         lambda g :pd.Series({
#             'No Show Rate (%)': 100*(g['No-show']==0).mean(),
#             'Average Age': g['Age'].mean(),
#             'SMS Received (%)':100*(g['SMS_received']).mean(),
#             # 'Scholarship':100*g['Scholarship'].mean(),
#             'Avg Days Between':g['days_between'].mean()
#         })).reset_index()

# gender=prepare_data(data,'Gender')
# scholarship=prepare_data(data,'Scholarship')
# Sms=prepare_data(data,'SMS_received')

# scholarship['Scholarship']=scholarship['Scholarship'].map({True: 'Has Scholarship', False: 'No Scholarship'})
# Sms['SMS_received'] = Sms['SMS_received'].map({True: 'Received SMS', False: 'No SMS'})



# profile_options = {
#     'Gender': (gender, 'Gender'),
#     'Scholarship': (scholarship, 'Scholarship'),
#     'SMS_received': (Sms, 'SMS Received (%)')
# }
#create app
app=dash.Dash(__name__,external_stylesheets=[dbc.themes.DARKLY])

#create app layout 
app.layout = dbc.Container([
    html.H1("Medical Appointment Dashboard",
            style={'textAlign': 'center', 'color': '#F72585', 'marginBottom': '36px'}),
    # html.H1('Patient Segment Behavioral Profiles', style={'textAlign': 'center', 'color': '#F72585', 'marginBottom': '36px'}),
    # dcc.Dropdown(
    #     id='segment-dropdown',
    #     options=[{'label': k, 'value': k} for k in profile_options.keys()],
    #     value='Gender',
    #     clearable=False
    # ),
    # dcc.Graph(id='radar-chart'),
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
                dbc.Col(dcc.Graph(figure=pie_fig), width=12)
            ]),
        ], width=4, style={'minWidth': '340px','align':"stretch"}),


        # RIGHT COLUMN: age/gender
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dcc.Dropdown(id="gender-filter",
                                 options=[{"label": "Male", "value": "M"}, {"label": "Female", "value": "F"}],
                                 placeholder="Select Gender"),
                    dcc.Graph(id='age-distribution')
                ])
            ], className="mb-4"),
        ], width=8)
    ]),

    dbc.Row([ #second row 
            dbc.Col( dcc.Graph(id='sms-chart',figure=sms_fig), width=4,style={'height': '440px'}),

            dbc.Col( dcc.Graph(id="days-chart",figure=day_fig), width=4,style={'height': '440px'}),

            dbc.Col([html.H4("Chronic Conditions"),
                     dcc.Dropdown(id='chronic-filter',
                                  options=[{'label':condition,'value':condition} for condition in conditions]),
                dcc.Graph(id="chronic-chart")], width=4,style={'height':'400px'})
        ],className='mb-4'),

    dbc.Row([ #Third Row   
        
        dbc.Col([
            html.H4('ScholarShip Analysis'),
            dcc.Graph(id='Scholarship-chart',figure=fig)
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

    dbc.Row( # forth Row 
        dbc.Col([
            html.H4('Neighborhood Map'),
            dcc.Dropdown(id='neighborhood-filter',
                options=[{'label':n,'value':n}for n in data['Neighbourhood'].unique()]
            ),
            dcc.Graph(id='neighborhood-chart')
        ],style={'marginTop': '60px','height': '400px'})
    )

], fluid=True, style={'backgroundColor': '#181830', 'padding': '24px'})


@app.callback(
    Output('age-distribution','figure'),
    Input('gender-filter','value')
)
def update_age_distribution(selected_gender):
    gender_colors = {'F': '#FF4DA6', 'M': '#33C3F0'}
    if selected_gender:
        df_filterd=data[data['Gender']==selected_gender]
        color_sequence = [gender_colors[selected_gender]]
    else:
        df_filterd=data
        color_sequence = [gender_colors['M'], gender_colors['F']]
    fig = px.histogram(
        df_filterd,
        x='Age',
        nbins=30,
        color='Gender',
        title='Age Distribution by Gender',
        opacity=0.8,color_discrete_sequence=color_sequence
)
    fig.update_layout(
        paper_bgcolor="#1A1338",     
        plot_bgcolor="#1A1338")
    return fig


@app.callback(
    Output('chronic-chart','figure'),
    Input('chronic-filter','value')
)
def update_chronic_chart(selected_condition):
    if selected_condition:
        df_filtered =data[data[selected_condition] == 1]
    else:
        df_filtered=data[data[conditions].sum(axis=1)>0]
    
    df_filtered['Show Status'] = df_filtered['No-show'].map({0: 'No Show', 1: 'Show'})
    counts_df = df_filtered.groupby('Show Status').size().reset_index(name='Count')
    
    fig = px.bar(
        counts_df,
        x='Show Status',
        y='Count',
        color='Show Status',
        color_discrete_map={'Show': '#33C3F0', 'No Show': '#FF4DA6'},
        title=f'Show vs No Show Counts for {selected_condition if selected_condition else "All Conditions"}',
        labels={'Count': 'Number of Appointments', 'Show Status': 'Attendance'}
    )
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='#181830',
        plot_bgcolor='#181830',
        font_color='white'
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

neighborhood_coords = {
    'REPÚBLICA': (-20.3194, -40.3378),
    'GOIABEIRAS': (-20.2667, -40.3000),
    'CONQUISTA': (-15.2795, -40.9658),  # Vitória da Conquista - different city
    'NOVA PALESTINA': (-20.2721, -40.2721),
    'SÃO CRISTÓVÃO': (-20.3194, -40.3378),
    'GRANDE VITÓRIA': (-20.3194, -40.3378),
    'JARDIM DA PENHA': (-20.3057, -40.3175),
    'SANTO ANDRÉ': (-20.3194, -40.3378),
    'SOLON BORGES': (-20.3194, -40.3378),
    'BONFIM': (-20.3194, -40.3378),
    'MARIA ORTIZ': (-20.3194, -40.3378),
    'JABOUR': (-20.3194, -40.3378),
    'ANTÔNIO HONÓRIO': (-20.3096, -40.3039),
    'RESISTÊNCIA': (-20.3194, -40.3378),
    'ILHA DE SANTA MARIA': (-20.3200, -40.3200),
    'JUCUTUQUARA': (-20.3337, -40.3505),
    'SANTO ANTÔNIO': (-20.3194, -40.3378),
    'BELA VISTA': (-20.3194, -40.3378),
    'MÁRIO CYPRESTE': (-20.3194, -40.3378),
    'PRAIA DO SUÁ': (-20.3215, -40.3125),
    'DA PENHA': (-20.3000, -40.3400),
    'ITARARÉ': (-20.3000, -40.3500),
    'ANDORINHAS': (-20.3194, -40.3378),
    'SÃO PEDRO': (-20.3194, -40.3378),
    'SÃO JOSÉ': (-20.3194, -40.3378),
    'REDENÇÃO': (-20.3194, -40.3378),
    'TABUAZEIRO': (-20.3194, -40.3378),
    'SANTOS DUMONT': (-20.3194, -40.3378),
    'MARUÍPE': (-20.3100, -40.3300),
    'CARATOÍRA': (-20.3194, -40.3378),
    'ARIOVALDO FAVALESSA': (-20.3194, -40.3378),
    'UNIVERSITÁRIO': (-20.3150, -40.3300),
    'SANTA MARTHA': (-20.3194, -40.3378),
    'JOANA D´ARC': (-20.3194, -40.3378),
    'CONSOLAÇÃO': (-20.3194, -40.3378),
    'SÃO BENEDITO': (-20.3194, -40.3378),
    'BOA VISTA': (-20.3194, -40.3378),
    'JARDIM CAMBURI': (-20.3050, -40.2900),
    'CENTRO': (-20.3194, -40.3378),
    'PARQUE MOSCOSO': (-20.3120, -40.3450),
    'SANTA CLARA': (-20.3194, -40.3378),
    'DO MOSCOSO': (-20.3194, -40.3378),
    'PRAIA DO CANTO': (-20.3256, -40.3113),
    'SANTA LÚCIA': (-20.3202, -40.3050),
    'BARRO VERMELHO': (-20.3194, -40.3378),
    'BENTO FERREIRA': (-20.3194, -40.3378),
    'FONTE GRANDE': (-20.3194, -40.3378),
    'SANTA TEREZA': (-20.3194, -40.3378),
    'GURIGICA': (-20.3194, -40.3378),
    'CRUZAMENTO': (-20.3194, -40.3378),
    'JESUS DE NAZARETH': (-20.3194, -40.3378),
    'ILHA DO PRÍNCIPE': (-20.3300, -40.3200),
    'SANTOS REIS': (-20.3194, -40.3378),
    'ILHA DAS CAIEIRAS': (-20.3500, -40.3300),
    'COMDUSA': (-20.3194, -40.3378),
    'MATA DA PRAIA': (-20.3200, -40.2550),
    'SANTA CECÍLIA': (-20.3194, -40.3378),
    'PIEDADE': (-20.3194, -40.3378),
    'DE LOURDES': (-20.3194, -40.3378),
    'MONTE BELO': (-20.3194, -40.3378),
    'VILA RUBIM': (-20.3194, -40.3378),
    'DO QUADRO': (-20.3194, -40.3378),
    'ESTRELINHA': (-20.3194, -40.3378),
    'FORTE SÃO JOÃO': (-20.3194, -40.3378),
    'ROMÃO': (-20.3194, -40.3378),
    'INHANGUETÁ': (-20.3194, -40.3378),
    'DO CABRAL': (-20.3194, -40.3378),
    'ENSEADA DO SUÁ': (-20.3200, -40.2550),
    'ILHA DO BOI': (-20.3210, -40.3220),
    'HORTO': (-20.3194, -40.3378),
    'NAZARETH': (-20.3194, -40.3378),
    'SANTA HELENA': (-20.3194, -40.3378),
    'FRADINHOS': (-20.3194, -40.3378),
    'SEGURANÇA DO LAR': (-20.3194, -40.3378),
    'SANTA LUÍZA': (-20.3194, -40.3378),
    'MORADA DE CAMBURI': (-20.3100, -40.2800),
    'PONTAL DE CAMBURI': (-20.3100, -40.2800),
    'ILHA DO FRADE': (-20.3100, -40.3200),
    'AEROPORTO': (-20.2581, -40.2864),  # Eurico de Aguiar Salles Airport
    'ILHAS OCEÂNICAS DE TRINDADE': (-20.5200, -29.3200)  # Trindade Island (offshore)
}
px.set_mapbox_access_token("your_token") 
data['Latitude'] = data['Neighbourhood'].map(lambda x: neighborhood_coords.get(x, (-20.3194, -40.3378))[0])
data['Longitude'] = data['Neighbourhood'].map(lambda x: neighborhood_coords.get(x, (-20.3194, -40.3378))[1])
no_show_rate_by_neighborhood = data.groupby('Neighbourhood')['No-show'].apply(lambda x: 100 * (x == 0).mean()).reset_index(name='No_Show_Rate')
plot_data = no_show_rate_by_neighborhood.merge(
    pd.DataFrame.from_dict(neighborhood_coords, orient='index', columns=['Latitude', 'Longitude']).reset_index().rename(columns={'index': 'Neighbourhood'}),
    on='Neighbourhood',
    how='left'
)
@app.callback(
    Output('neighborhood-chart', 'figure'),
    Input('neighborhood-filter', 'value')
)
def update_neighborhood_chart(selected_neighborhood):
    if selected_neighborhood:
        filtered_df = plot_data[plot_data['Neighbourhood'] == selected_neighborhood]
    else:
        filtered_df = plot_data

    fig = px.scatter_mapbox(
        filtered_df,
        lat='Latitude',
        lon='Longitude',
        size='No_Show_Rate',
        color='No_Show_Rate',
        hover_name='Neighbourhood',
        color_continuous_scale='Reds',
        size_max=30,
        zoom=11,
        title='No-Show Rates by Neighborhood'
    )

    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_center={"lat": -20.3194, "lon": -40.3378},
        paper_bgcolor='#1A1338',
        plot_bgcolor='#1A1338',
        font=dict(color='white')
    )
    return fig





# @app.callback(
#     Output('radar-chart', 'figure'),
#     Input('segment-dropdown', 'value')
# )
# def update_radar(selected_segment):
#     df, col_name = profile_options[selected_segment]
#     radar_df = df.melt(id_vars=[col_name], var_name='Metric', value_name='Value')
#     fig = px.line_polar(
#         radar_df, r='Value', theta='Metric', color=col_name,
#         line_close=True, markers=True,
#         title=f'Patient Behavioral Profile by {selected_segment}',
#         template='plotly_dark'
#     )
#     fig.update_layout(
#         polar=dict(radialaxis=dict(tickangle=45, showline=True, linewidth=2)),
#         paper_bgcolor='#181830',
#         font_color='white'
#     )
#     return fig



if __name__ == '__main__':
    app.run(debug=True)