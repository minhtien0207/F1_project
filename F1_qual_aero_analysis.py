import streamlit as st
import streamlit.components.v1 as components

import fastf1 as ff1
from fastf1.ergast import Ergast
from fastf1 import plotting
from fastf1 import utils

import datetime as dt
import pandas as pd
import numpy as np
from adjustText import adjust_text

import seaborn as sns

#%matplotlib inline
from matplotlib import pyplot as plt
import matplotlib.patheffects as path_effects

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
    'Select the year', (2022, 2023, 2024, 2025, 2026)
)
#It would be best to to able to select this schedule and 
schedule = Ergast().get_race_schedule(season=year)

event = st.selectbox(
    'Select the GP', schedule['raceName'])
    
sess = st.selectbox(
    'Select the session', ('FP1', 'FP2', 'FP3', 'Qualifying','Sprint Qualifying')
)

session = ff1.get_session(year, event, sess)
session.load()

track_length_data ={
'GP' : ['Australian Grand Prix','Chinese Grand Prix','Japanese Grand Prix','Bahrain Grand Prix','Saudi Arabian Grand Prix','Miami Grand Prix','Emilia Romagna Grand Prix','Monaco Grand Prix','Spanish Grand Prix',
'Canadian Grand Prix','Austrian Grand Prix','British Grand Prix','Belgian Grand Prix','Hungarian Grand Prix','Dutch Grand Prix','Italian Grand Prix','Azerbaijan Grand Prix','Singapore Grand Prix','United States Grand Prix',
'Mexico City Grand Prix','São Paulo Grand Prix','Las Vegas Grand Prix','Qatar Grand Prix','Abu Dhabi Grand Prix'],
'Track length (m)': [5278, 5451, 5807, 5412, 6174, 5412, 4909, 3337, 4675, 4361, 4318, 5891, 7004, 4381, 4259, 5793, 6003, 4940, 5513, 4304, 4309, 6201, 5419, 5281]
}
track_length_data = pd.DataFrame(track_length_data)

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
if (year == 2026):
    team7_lap = session.laps.pick_teams("Audi").pick_fastest()
elif (year <= 2023):
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
if (year >= 2026):
    team11_lap = session.laps.pick_teams("Cadillac").pick_fastest()
    team11_data = team11_lap.get_car_data().add_distance()

#Reserve to add more rosters
teams_2026 = ['Red Bull', 'Ferrari', 'McLaren', 'Mercedes', 'Haas', 'Aston Martin', 'Audi', 'Alpine', 'Racing Bulls', 'Williams', 'Cadillac']
teams_2025 = ['Red Bull', 'Ferrari', 'McLaren', 'Mercedes', 'Haas', 'Aston Martin', 'Sauber', 'Alpine', 'Racing Bulls', 'Williams']
teams_2024 = ['Red Bull', 'Ferrari', 'McLaren', 'Mercedes', 'Haas', 'Aston Martin', 'Sauber', 'Alpine', 'RB', 'Williams']
teams_2023 = ['Red Bull', 'Ferrari', 'McLaren', 'Mercedes', 'Haas', 'Aston Martin', 'Alfa Romeo', 'Alpine', 'AlphaTauri', 'Williams']
teams_2022 = ['Red Bull', 'Ferrari', 'McLaren', 'Mercedes', 'Haas', 'Aston Martin', 'Alfa Romeo', 'Alpine', 'AlphaTauri', 'Williams']

if (year == 2026):
    teams = teams_2026
elif (year == 2025):
    teams = teams_2025
elif (year == 2024):
    teams = teams_2024
elif (year == 2023):
    teams = teams_2023
elif (year == 2022):
    teams = teams_2022

#Create a dictionary for laptimes
if (year < 2026):
    laptimes = {
    'team': teams,
    'lt' : [team1_lap, team2_lap, team3_lap, team4_lap, team5_lap, team6_lap, team7_lap, team8_lap, team9_lap, team10_lap]   
    }
else:
    laptimes = {
    'team': teams,
    'lt' : [team1_lap, team2_lap, team3_lap, team4_lap, team5_lap, team6_lap, team7_lap, team8_lap, team9_lap, team10_lap, team11_lap]   
    }

#Create a dictionary for telemetry data
if (year < 2026):
    telemetry = {
        'team': teams,
        'tele' : [team1_data, team2_data, team3_data, team4_data, team5_data, team6_data, team7_data, team8_data, team9_data, team10_data]   
    }
else:
    telemetry = {
        'team': teams,
        'tele' : [team1_data, team2_data, team3_data, team4_data, team5_data, team6_data, team7_data, team8_data, team9_data, team10_data, team11_data]   
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

#Make a color palette associating team names to hex codes
team_palette = {team: ff1.plotting.get_team_color(team, session=session) for team in teams}

def boxed_text_field(ax, x, y, text, **kwargs):
    ax.text(
        x, y, text,
        color="white",
        bbox=dict(
        facecolor="gray",
        edgecolor="none",
        alpha=0.55,
        boxstyle="round,pad=0.35"
        ),
        **kwargs
    )

def boxed_text_axe(ax, x, y, text, **kwargs):
    ax.text(
        x, y, text,
        color="white",
        bbox=dict(
        facecolor="black",
        edgecolor="none",
        alpha=0.55,
        boxstyle="round,pad=0.35"
        ),
        **kwargs
    )

fig, ax = plt.subplots(figsize=(10, 8))

# Scatter plot
texts = []

for team, mean_speed, top_speed in zip(
        results['Team'],
        results['Mean speed (km/h)'],
        results['Top speed (km/h)']):

    color = team_palette.get(team, "black")

    ax.scatter(mean_speed, top_speed,
               s=120,
               color=color,
               edgecolor="black",
               linewidth=0.6,
               zorder=3)

    txt = ax.text(mean_speed, top_speed, team,
                  fontsize=9,
                  ha='center',
                  va='center')

    texts.append(txt)

adjust_text(
    texts,
    arrowprops=dict(arrowstyle="-", color='gray', lw=0.5),
    ax=ax
)    
# ----- CENTER -----
center_x = results['Mean speed (km/h)'].mean()
center_y = results['Top speed (km/h)'].mean()

ax.axvline(center_x, color='gray', linestyle='--', linewidth=1)
ax.axhline(center_y, color='gray', linestyle='--', linewidth=1)

# ----- QUADRANT LABELS -----
xmin, xmax = ax.get_xlim()
ymin, ymax = ax.get_ylim()

x_offset = (xmax - xmin) * 0.03
y_offset = (ymax - ymin) * 0.03

boxed_text_field(ax, xmax - x_offset, center_y, "Quick", ha="right", fontsize=9)
boxed_text_field(ax, xmin + x_offset, center_y, "Slow", ha="left", fontsize=9)

boxed_text_field(ax, center_x, ymax - y_offset, "Low Drag", ha="center", fontsize=9)
boxed_text_field(ax, center_x, ymin + y_offset, "High Drag", ha="center", fontsize=9)


# ----- DIAGONAL LABELS -----
boxed_text_axe(ax, center_x + (xmax-center_x)*0.55,
           center_y + (ymax-center_y)*0.55,
           "High Efficiency",
           fontsize=9)

boxed_text_axe(ax, center_x - (center_x-xmin)*0.55,
           center_y + (ymax-center_y)*0.55,
           "Low Downforce",
           fontsize=9,
           ha="right")

boxed_text_axe(ax, center_x - (center_x-xmin)*0.55,
           center_y - (center_y-ymin)*0.55,
           "Low Efficiency",
           fontsize=9,
           ha="right")

boxed_text_axe(ax, center_x + (xmax-center_x)*0.55,
           center_y - (center_y-ymin)*0.55,
           "High Downforce",
           fontsize=9)

# ----- STYLE -----
ax.grid(linestyle='-.', color='#CCCCCC')

ax.set_xlabel("Mean Speed (km/h)")
ax.set_ylabel("Top Speed (km/h)")

ax.set_title(
    f"{session.event.year} {session.event['EventName']} - {session.name}\n"
    "Aero Performance Map (Fastest Laps)"
)

plt.tight_layout()

st.pyplot(fig)

