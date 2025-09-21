import streamlit as st
import streamlit.components.v1 as components

import fastf1 as ff1
from fastf1.ergast import Ergast
from fastf1 import plotting
from fastf1 import utils

import datetime as dt
import pandas as pd
import numpy as np

import seaborn as sns

#%matplotlib inline
from matplotlib import pyplot as plt

#Streamlit display components
st.header("Formula 1 Aerodynamic analysis")
st.caption("Inspired by fdataanalysis \nhttps://www.instagram.com/fdataanalysis")

st.text("This analysis looks at the relevant aerodynamic properties of each team's car. It uses their best lap of the session.\n")
st.text("Assuming different engines always deliver the same power output in their respective fastest lap of the session, then we can separate the team performance by the aerodynamics of their cars.\n")
st.text("The following scatterplot uses the best lap for each team based on telemetry data. It shows their top speed versus mean speed.\n")
st.text("From left to right, mean lap speed increases. Higher mean speed means lower lap time: teams on the left are slower, those on the right are quicker.\n")
st.text("Going from the bottom to the top, we have an increase in top speed: the cars at the bottom have high drag, while those at the top have low drag\n")
st.caption("Disclaimer: The mean speed is calculated by taking the lap time divided by the track length\n")

st.text("Choose the year, the circuit and the session to analyze, and be patient for the plot to appears :D\n")
st.text("The option of Sprint Qualifying appears but will only obviously works for event with a sprint shootout session")

year = st.selectbox(
    'Select the year', (2024, 2025)
)

#It would be best to to able to select this schedule and 
schedule = Ergast().get_race_schedule(season=year)

#more track can be added into this dictionary to expand the GP roster in earlier year are to be added. For the moment, I stay with 2024 and 2025's GP

track_length_data ={
'GP' : ['Australian Grand Prix','Chinese Grand Prix','Japanese Grand Prix','Bahrain Grand Prix','Saudi Arabian Grand Prix','Miami Grand Prix','Emilia Romagna Grand Prix','Monaco Grand Prix','Spanish Grand Prix',
'Canadian Grand Prix','Austrian Grand Prix','British Grand Prix','Belgian Grand Prix','Hungarian Grand Prix','Dutch Grand Prix','Italian Grand Prix','Azerbaijan Grand Prix','Singapore Grand Prix','United States Grand Prix',
'Mexico City Grand Prix','São Paulo Grand Prix','Las Vegas Grand Prix','Qatar Grand Prix','Abu Dhabi Grand Prix'],
'Track length (m)': [5278, 5451, 5807, 5412, 6174, 5412, 4909, 3337, 4675, 4361, 4318, 5891, 7004, 4381, 4259, 5793, 6003, 4940, 5513, 4304, 4309, 6201, 5419, 5281]
}
track_length_data = pd.DataFrame(track_length_data)


event = st.selectbox(
    'Select the GP', schedule['raceName'])
    
sess = st.selectbox(
    'Select the session', ('FP1', 'FP2', 'FP3', 'Qualifying','Sprint Qualifying')
)

session = ff1.get_session(year, event, sess)
session.load()

#Select the fastest lap of a specific team and get the car telemetry data for that lap.
team1_lap = session.laps.pick_teams("Red Bull Racing").pick_fastest()
team1_data = team1_lap.get_car_data().add_distance()
team2_lap = session.laps.pick_teams("Ferrari").pick_fastest()
team2_data = team2_lap.get_car_data().add_distance()
team3_lap = session.laps.pick_teams("McLaren").pick_fastest()
team3_data = team3_lap.get_car_data().add_distance()
team4_lap = session.laps.pick_teams("Mercedes").pick_fastest()
team4_data = team4_lap.get_car_data().add_distance()
team5_lap = session.laps.pick_teams("Haas F1 Team").pick_fastest()
team5_data = team5_lap.get_car_data().add_distance()
team6_lap = session.laps.pick_teams("Aston Martin").pick_fastest()
team6_data = team6_lap.get_car_data().add_distance()
if (year <= 2023):
    team7_lap = session.laps.pick_teams("Alfa Romeo").pick_fastest()
else:
    team7_lap = session.laps.pick_teams("Kick Sauber").pick_fastest()
team7_data = team7_lap.get_car_data().add_distance()
team8_lap = session.laps.pick_teams("Alpine").pick_fastest()
team8_data = team8_lap.get_car_data().add_distance()
if (year <= 2023):
    team9_lap = session.laps.pick_teams("AlphaTauri").pick_fastest()
elif (year == 2024):
    team9_lap = session.laps.pick_teams("RB").pick_fastest()
else:
    team9_lap = session.laps.pick_teams("Racing Bulls").pick_fastest()
team9_data = team9_lap.get_car_data().add_distance()
team10_lap = session.laps.pick_teams("Williams").pick_fastest()
team10_data = team10_lap.get_car_data().add_distance()

#Reserve to add more rosters
teams_2025 = ['Red Bull', 'Ferrari', 'McLaren', 'Mercedes', 'Haas', 'Aston Martin', 'Sauber', 'Alpine', 'Racing Bulls', 'Williams']
teams_2024 = ['Red Bull', 'Ferrari', 'McLaren', 'Mercedes', 'Haas', 'Aston Martin', 'Sauber', 'Alpine', 'RB', 'Williams']
#teams_2023 = ['Red Bull', 'Ferrari', 'McLaren', 'Mercedes', 'Haas', 'Aston Martin', 'Alfa Romeo', 'Alpine', 'AlphaTauri', 'Williams']
#teams_2022 = ['Red Bull', 'Ferrari', 'McLaren', 'Mercedes', 'Haas', 'Aston Martin', 'Alfa Romeo', 'Alpine', 'AlphaTauri', 'Williams']

if (year > 2024):
    teams = teams_2025
elif (year == 2024):
    teams = teams_2024

#Create a dictionary for laptimes
laptimes = {
    'team': teams,
    'lt' : [team1_lap, team2_lap, team3_lap, team4_lap, team5_lap, team6_lap, team7_lap, team8_lap, team9_lap, team10_lap]   
    }

#Create a dictionary for telemetry data
telemetry = {
    'team': teams,
    'tele' : [team1_data, team2_data, team3_data, team4_data, team5_data, team6_data, team7_data, team8_data, team9_data, team10_data]   
    }

#Access the dictionary with the key as the name of the event to get the corresponding track length
track_length = track_length_data.loc[track_length_data['GP'] == event, 'Track length (m)'].values[0]

#Create a list to store the results
results = []

#Iterate over each team_laptimes
for name, lt in zip(laptimes['team'], laptimes['lt']): #(name, lt) = ('Red Bull Racing', rbr_lap), ('Ferrari': fer_lap) etc.
    lt['LapTime(s)'] = lt['LapTime'].total_seconds()
    results.append(
        {
            'Team': name,
            'Mean speed (km/h)': (track_length/lt['LapTime(s)']*3.6).tolist()
        }
    )

#Convert dictionnary to DataFrame
results = pd.DataFrame(results)

#Iterate over each team_lap_telemetry
v_max = []
for name, df in zip(telemetry['team'] , telemetry['tele']): #(name, df) = ('Red Bull Racing', rbr_data), ('Ferrari': fer_data) etc.
    v_max.append(
        df['Speed'].max().tolist()
    )

#Add column "Top speed" to the DataFrame, then display completed DataFrame
results['Top speed (km/h)'] = v_max
print(results.sort_values(by='Mean speed (km/h)', ascending=False))

#Create the figure
fig, ax = plt.subplots(figsize=(10, 10))

#Make a color palette associating team names to hex codes
team_palette = {team: ff1.plotting.get_team_color(team, session=session) for team in teams}

#Scatter plot
for team, mean_speed, top_speed in zip(results['Team'], results['Mean speed (km/h)'], results['Top speed (km/h)']):
    color = team_palette.get(team, 'black')  # Default to black if team color not found
    plt.scatter(mean_speed, top_speed, color=color, label=team, s=100)
    plt.text(mean_speed - 0.1, top_speed + 0.1, team, fontsize=8) # Annotate the team name: plt.text(x coordinate, y coordinate, team name, fontsize)

#Calculate the center of the plot
center_x = np.round(((results['Mean speed (km/h)'].min() + results['Mean speed (km/h)'].max()) / 2) * 2) / 2
center_y = (results['Top speed (km/h)'].min() + results['Top speed (km/h)'].max()) / 2

#Arrows and labels for directions, centered
plt.arrow(center_x, center_y, 3.5, 0, head_width=0.1, head_length=0.1, fc='gray', ec='gray') # right: Quick
plt.arrow(center_x, center_y, -3.5, 0, head_width=0.1, head_length=0.1, fc='gray', ec='gray') # left: Slow
plt.arrow(center_x, center_y, 0, (results['Top speed (km/h)'].max() - center_y), head_width=0.1, head_length=0.1, fc='gray', ec='gray') # up: Low Drag
plt.arrow(center_x, center_y, 0, (center_y - results['Top speed (km/h)'].max()), head_width=0.1, head_length=0.1, fc='gray', ec='gray') # down: High Drag

#Labels for directions
plt.text(center_x + 3.5, center_y - 0.15, 'Quick', va='center', fontsize=10)
plt.text(center_x - 3.79, center_y - 0.15, 'Slow', va='center', fontsize=10)
plt.text(center_x, center_y + (results['Top speed (km/h)'].max() - center_y + 0.15), 'Low Drag', ha='center', fontsize=10)
plt.text(center_x, center_y - (center_y - results['Top speed (km/h)'].min() + 0.23), 'High Drag', ha='center', fontsize=10)

#Diagonal arrows for aero efficiency
plt.arrow(center_x, center_y, 3.5, (results['Top speed (km/h)'].max() - center_y), head_width=0.1, head_length=0.1, fc='gray', ec='gray')  # Top-right: High Efficiency
plt.arrow(center_x, center_y, -3.5, (results['Top speed (km/h)'].max() - center_y), head_width=0.1, head_length=0.1, fc='gray', ec='gray')  # Top-left: Low Downforce
plt.arrow(center_x, center_y, -3.5, (center_y - results['Top speed (km/h)'].max()), head_width=0.1, head_length=0.1, fc='gray', ec='gray')  # Bottom-left: Low Efficiency
plt.arrow(center_x, center_y, 3.5, (center_y - results['Top speed (km/h)'].max()), head_width=0.1, head_length=0.1, fc='gray', ec='gray')  # Bottom-right: High downforce

#Labels for diagonal directions
plt.text(center_x + 2.85, center_y + (results['Top speed (km/h)'].max() - center_y + 0.1), 'High Efficiency', ha='left', va='bottom', fontsize=10)
plt.text(center_x - 2.8, center_y + (results['Top speed (km/h)'].max() - center_y + 0.1), 'Low Downforce', ha='right', va='bottom', fontsize=10)
plt.text(center_x - 2.85, center_y - (center_y - results['Top speed (km/h)'].min() + 0.1), 'Low Efficiency', ha='right', va='top', fontsize=10)
plt.text(center_x + 2.8, center_y - (center_y - results['Top speed (km/h)'].min() + 0.1), 'High Downforce', ha='left', va='top', fontsize=10)

plt.xlabel('Mean Speed (km/h)')
plt.ylabel('Top Speed (km/h)')
plt.grid(linestyle='-.', color='#CCCCCC', which='major', axis='both')
plt.title(f"{session.event.year} {session.event['EventName']}, {session.name}\nAero performance - based on teams' fastest laps")

#Show plot
st.pyplot(fig)






