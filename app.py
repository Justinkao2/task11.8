from dash import Dash, html, dcc             
from dash.dependencies import Input, Output  
import plotly.express as px                 
import pandas as pd 
from sklearn.preprocessing import MinMaxScaler


raw_df = pd.read_csv('world-happiness-report-2021.csv')
df_group = raw_df.groupby('Regional indicator').agg(
    ladder_score = ('Ladder score', 'mean'),         
	social_support = ('Social support', 'mean'),
    healthy_life_expectancy = ('Healthy life expectancy','mean'),
    freedom_to_make_life_choices = ('Freedom to make life choices', 'mean')
)
df_group = df_group.reset_index()

# make the columns range in [0,1]
df_group_scaled = df_group.copy()
scaler = MinMaxScaler(feature_range=(0.1, 1))
df_group_scaled[['ladder_score', 'social_support', 'healthy_life_expectancy', 'freedom_to_make_life_choices']] = scaler.fit_transform(df_group[['ladder_score', 'social_support', 'healthy_life_expectancy', 'freedom_to_make_life_choices']])

df_long = df_group_scaled.melt(
    id_vars='Regional indicator', 
    value_vars=['ladder_score', 'social_support', 'healthy_life_expectancy', 'freedom_to_make_life_choices'], 
    var_name='Indicator', 
    value_name='Value')


df= df_long.sort_values(by=['Indicator', 'Value'], ascending=[True, False])
sorted_regions_by_indicator = df.groupby('Indicator')['Regional indicator'].apply(list).to_dict()
colors = ["#D9796F", "#E89C71", "#E8B47F", "#D9C386", "#A8C68F", "#85B9B0", "#7CA7C4", "#7F8DB7", "#6C7A9C", "#5D6A82"]


app = Dash(__name__)

server = app.server

app.layout = html.Div([
    
    html.H2("Interactive Regional Indicators Dashboard"),

    dcc.Dropdown(
        id='dropdown', 
        options=[{'label': region, 'value': region} for region in df['Regional indicator'].unique()],
        value='East Asia',  
        multi=True 
    ),

    dcc.RangeSlider(
        id='slider',
        min=0,
        max=1,
        step=0.05,
        value=[0.2,0.8]  #default
    ),

    dcc.Graph(id='graph') 
])

@app.callback(
    Output('graph', 'figure'),   
    [Input('dropdown', 'value'), Input('slider', 'value')]  
)

def update_chart(selected_regions, value_range):
    if isinstance(selected_regions, str):
        selected_regions = [selected_regions]

    filtered_df = df[df['Regional indicator'].isin(selected_regions)]
    filtered_df = filtered_df[(filtered_df['Value'] >= value_range[0]) & (filtered_df['Value'] <= value_range[1])]
    
    fig = px.bar(
        filtered_df,
        x="Indicator",
        y="Value",
        color='Regional indicator',
        labels={"Value": 'Score', 'Regional indicator': 'Region'},
        barmode='group',
        color_discrete_sequence=colors,
        category_orders={'Regional indicator': sorted_regions_by_indicator}
    )
    
    fig.update_layout(
        legend_title_text='Region',  
        barmode='stack',
        font=dict(size=12),
        hovermode="x unified"
    )
    
    return fig


if __name__ == '__main__':
    app.run(debug=True)
