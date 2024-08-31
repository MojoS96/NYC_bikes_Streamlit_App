################################################ NYC BIKES DASHBOARD #####################################################

!pip install -r 'requirements_nycbikes_venv.txt'

import streamlit as st
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px  # Import Plotly Express
import matplotlib.pyplot as plt
from streamlit_keplergl import keplergl_static
from keplergl import KeplerGl
from datetime import datetime as dt
from numerize.numerize import numerize
from PIL import Image

########################### Initial settings for the dashboard ####################################################

st.set_page_config(page_title='NYC CitiBike Strategy Dashboard', layout='wide')
st.title("NYC CitiBike Strategy Dashboard")

# Define side bar
st.sidebar.title("Chapter Selector")
page = st.sidebar.selectbox(
    'Select a chapter of the analysis to navigate to',
    ["Intro page", "Weather component and bike usage",
     "Most popular stations",
     "Interactive map with aggregated bike trips", "Recommendations"])

########################## Import data ###########################################################################################

df = pd.read_csv('reduced_data_to_plot_7.csv', index_col=False)
df2 = pd.read_csv('reduced_data_to_plot.csv', index_col=0)
top20 = pd.read_csv('top20.csv', index_col=0)
top50_routes = pd.read_csv('aggregated_trips.csv', index_col=0)
top_round_routes = pd.read_csv('top_round_routes.csv', index_col=0)
top_point_routes = pd.read_csv('top_point_routes.csv', index_col=0)

######################################### DEFINE THE PAGES #####################################################################

### Intro page

if page == "Intro page":
    st.markdown("#### This dashboard aims at providing helpful insights on the expansion problems that CitiBikes currently faces in the New York City area.")
    st.markdown("Right now, Citi bikes runs into a situation where customers complain about bikes not being available at certain times. This analysis will look at the potential reasons behind this. The dashboard is separated into 4 chapters:")
    st.markdown("- Most popular stations")
    st.markdown("- Weather component and bike usage")
    st.markdown("- Interactive map with aggregated bike trips")
    st.markdown("- Recommendations")
    st.markdown("The dropdown menu on the left 'Chapter Selector' will take you to the different aspects of the analysis our team looked at.")

    myImage = Image.open("Citi_Bike_Ride_experience_Hero_3x.webp")  # source: https://citibikenyc.com/how-it-works
    st.image(myImage)

### Create the dual axis line chart page ###

elif page == 'Weather component and bike usage':

    fig_2 = make_subplots(specs=[[{"secondary_y": True}]])

    fig_2.add_trace(go.Scatter(
        x=df['date'],
        y=df['bike_rides_daily'],
        name='Daily bike rides',
        marker={'color': 'blue'}), secondary_y=False)

    fig_2.add_trace(go.Scatter(
        x=df['date'],
        y=df['avgTemp'],
        name='Daily temperature',
        marker={'color': 'orange'}), secondary_y=True)

    fig_2.update_layout(title='Daily bike trips and temperatures in NYC 2022', height=600)

    st.plotly_chart(fig_2, use_container_width=True)
    st.markdown("Based on how closely the two variables plotted mirror each other there is an easily identifiable correlation between the rise and drop of temperatures and their relationship with the frequency of bike trips taken daily. As temperatures plunge, so does bike usage. With this knowledge, we can infer that the inventory shortage problem that is sometimes felt by the customers may be more widespread in the warmer months, approximately from May to October. This date range also aligns nicely with often held assumptions that late spring to early fall is the peak season for tourism (international, as opposed to domestic which also peaks during US Thanksgiving and Christmas) (Additional reading about Tourism seasonality: https://www.seathecity.com/when-is-the-best-time-to-visit-new-york-city/#:~:text=Peak%20Tourist%20Season,at%20all%20the%20wonderful%20attractions.)")

### Most popular stations page

elif page == 'Most popular stations':

    # Create the filter on the side bar
    with st.sidebar:
        season_filter = st.multiselect(label='Select the season', options=df['season'].unique(),
                                       default=df['season'].unique())

    df = df.query('season == @season_filter')

    # Define the total rides
    total_rides = float(df['bike_rides_daily'].count())
    st.metric(label='Total Bike Rides', value=numerize(total_rides))

    # Bar chart
    fig = go.Figure(go.Bar(x=top20['start_station_name'], y=top20['value'],
                           marker={'color': top20['value'], 'colorscale': 'Blues'}))
    fig.update_layout(
        title='Top 20 most popular bike stations in New York City',
        xaxis_title='Start stations',
        yaxis_title='Sum of trips',
        width=900, height=600
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("***As a disclaimer, for those that do not have an encyclopedic knowledge of the street names and intersections it's understandably quite difficult to put the following station names into context. I'd recommend skipping to the next section containing map data to better understand how these trip volumes look in real life.***")
    st.markdown(" ")
    st.markdown("From the bar chart, it is clear that there are some start stations that are more popular than others - in the top 3 we can see W 21 St & 6 Avenue (located in Midtown Manhattan), West St & Chambers St. (Found at the midway point of the Hudson Greenway Cycle Path) and Broadway & W 58 St. (Located on the Southwest corner of Central park). These 3 spots represent areas that combine a good mixture of popular tourist attractions as well as central locations which would be likely to have a constant usage stream by local residents going about their day-to-day commutes. There isn't a huge delta between the highest and lowest bars of the plot, which I believe is indicative of how interconnected the city is and how the main points of interest are fairly well spread out across multiple sections. This is a finding that we could cross-reference with the interactive map that you can access through the side bar select box. In the meantime, as an additional piece of context, I've included Google Streets map images of the popular stations to get an idea of the areas they serve.")

    ### Images of the most popular station streets ###
    myImage2 = Image.open("W21st.PNG")
    myImage3 = Image.open("ChambersSt.PNG")
    myImage4 = Image.open("Broadway.PNG")

    # Row 1: Names
    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("1. W 21 St & 6 Avenue:")
    with col2:
        st.write("2. West St & Chambers St:")
    with col3:
        st.write("3. Broadway & W 58 St:")

    # Row 2: Images
    col1, col2, col3 = st.columns(3)

    with col1:
        st.image(myImage2, use_column_width=True)
    with col2:
        st.image(myImage3, use_column_width=True)
    with col3:
        st.image(myImage4, use_column_width=True)

elif page == 'Interactive map with aggregated bike trips':

    ### Create the map ###
    st.write("Interactive map showing aggregated bike trips over New York City")

    path_to_html = "nyc_bikesv2_kepler.gl.html"

    # Read file and keep in variable
    with open(path_to_html, 'r') as f:
        html_data = f.read()

    ## Show in webpage
    st.header("Aggregated Bike Trips in New York City")
    st.components.v1.html(html_data, height=1000)
    st.markdown("#### Using the filter on the left-hand side of the map we can check whether the most popular start stations also appear in the most popular trips.")
    st.markdown("As you can see, usage within NYC is fairly spread out across different cultural centers throughout the city. There are arguably 3 primary hubs; The Hudson River Greenway, Central Park, and Midtown Manhattan (Which contains many tourist attractions such as the Empire State Building, MoMa, Times Square and many other PoIs)")
    st.markdown("One of the most interesting things that this map helps to highlight is the relationship between popular start locations and their endpoints. Sticking to the concept of the 'Hubs', the direction that people travel in also seems consistent among users and tells us a great deal about where we need to pick the bikes up from, and where they should be relocated back to at the end of the day. Looking at the Hudson River bike route specifically, *Most* of the journeys start near Tribeca / Rockefeller Park (Southern section of the map) which is shown by the quantity of ORANGE data points. The endpoints, in BLUE, tend to be further up the route north of the route starting point. This tells us that there is a strong portion of users that often do point-to-point journeys, rather than circuits, which will have an impact on available bike inventory at the most popular locations.")
    st.markdown("Whilst the map above is a fantastic source of information, allowing you to really dig deep into the geographical representation of popular routes it sadly doesn't provide callouts or weighting to indicate the most popular routes. Without trying to contradict myself too much, the major downfall of this visualization is that point-to-point routes have more visual presence than round trips. Point-to-point routes are incredibly popular, but round trips actually make up the majority of journeys. Please have a look at the charts and metrics to better understand the split.")
    
    value_point = top50_routes.loc[top50_routes['Trip_Type'] == 'Point-to-Point', 'value'].values[0]
    value_round = top50_routes.loc[top50_routes['Trip_Type'] == 'Round-Trip', 'value'].values[0]
    st.metric(label='### Qty. of Round Trips', value=value_round)
    st.metric(label='### Qty. of Point-to-Point Trips', value=value_point)

    # Sort the data and get the top 10 for each variable
    top10_round = top_round_routes.nlargest(10, 'value')
    top10_point = top_point_routes.nlargest(10, 'value')

    # Define common dimensions
    chart_height1 = 825
    chart_height2 = 800
    chart_width = 400

    # Create two columns for the bar charts
    col1, col2 = st.columns(2)

    # Bar chart for Category A
    with col1:
        fig_A = px.bar(top10_round, x='Route', y='value', title='Top 10 Round Trips', color_discrete_sequence=['#1f77b4'])
        fig_A.update_layout(height=chart_height1, width=chart_width)
        st.plotly_chart(fig_A, use_container_width=True)

    # Bar chart for Category B
    with col2:
        fig_B = px.bar(top10_point, x='Route', y='value', title='Top 10 Point-to-Point Trips', color_discrete_sequence=['#ff7f0e'])
        fig_B.update_layout(height=chart_height2, width=chart_width)
        st.plotly_chart(fig_B, use_container_width=True)

else:

    st.header("Conclusions and Recommendations")
    st.markdown("### Our analysis has shown that Citi Bikes should focus on the following objectives moving forward:")
    st.markdown("- Add more stations to the locations around the Hudson River Greenway route and other high traffic tourist locations like Central Park.")
    st.markdown("- Given the not insignificant quantity of point-to-point trips that occur in these tourist locations, I'd recommend offering casual users incentives to return bikes to the same station.")
    st.markdown("    - An example could be to run trials where 5% or 10% fare discounts are given contingent on returning a bike to a station within a set distance from the original station. This in turn could ensure a constant supply of bike inventory at, or near, to the high traffic areas. Additionally, it could help decrease operational overheads relating to restocking bikes at the end of each day.")
    st.markdown("- Ensure that bikes are fully stocked in all these stations during the warmer months in order to meet the higher demand, but provide a lower supply in winter and late autumn to reduce logistics costs.")

    st.header("Project Limitations")
    st.markdown("- The analysis performed for this presentation did not include a demographic analysis. Reviewing details like gender, age, and bike type could help us further pinpoint areas for operational improvements or increases in revenue.")
    st.markdown("- Initial attempts to review 'trip-time' were included, but given the complexity of the rental system it was hard to pinpoint how many of the values were legitimate. So as not to misrepresent this data, more effort should be taken in subsequent projects to review customer behaviors.")

    myImage5 = Image.open("shutterstock_1528044107-1024x683.jpg")  # source: https://secretnyc.co/nyc-greenway-expansion-project/
    st.image(myImage5)



