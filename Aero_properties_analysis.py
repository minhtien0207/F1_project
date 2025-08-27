import fastf1 as ff1
from fastf1 import plotting
from fastf1 import utils

import seaborn as sns

from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
from matplotlib import cm

import datetime as dt
import numpy as np
import pandas as pd

#Let's look at the Aero properties of 10 F1 car, based on the lastest GP to date, the Hungary grand prix.
#It is a scatterplot of the ten teams, considering the best lap for each. This mean I have to access telemetry data
#The mean and top speeds from that lap and plot the team as a dot on the chart. 
#Going from left to right, we have an increase in the mean lap speed, which means a lower laptime: teams on the left are 'slow', those on the right 'quick'. Going from the bottom to the top, we have an increase in top speed: the cars at the bottom have high drag, while those at the top have low drag.

# load a session and its telemetry data
qual = ff1.get_session(2025, 'Hungary Grand Prix', 'Q')
qual.load()

#Select the fastest lap of a specific team and get the car telemetry data for that lap. (A for loop would be better, but i don't know how, lmao =)))
rbr_laps = qual.laps.pick_teams("Red Bull Racing").pick_fastest()
rbr_data = rbr_laps.get_car_data().add_distance()

fer_laps = qual.laps.pick_teams("Ferrari").pick_fastest()
fer_data = fer_laps.get_car_data().add_distance()

mcl_laps = qual.laps.pick_teams("McLaren").pick_fastest()
mcl_data = mcl_laps.get_car_data().add_distance()

mer_laps = qual.laps.pick_teams("Mercedes").pick_fastest()
mer_data = mer_laps.get_car_data().add_distance()

haas_laps = qual.laps.pick_teams("Haas F1 Team").pick_fastest()
haas_data = haas_laps.get_car_data().add_distance()

ast_laps = qual.laps.pick_teams("Aston Martin").pick_fastest()
ast_data = ast_laps.get_car_data().add_distance()

ksb_laps = qual.laps.pick_teams("Kick Sauber").pick_fastest()
ksb_data = ksb_laps.get_car_data().add_distance()

alp_laps = qual.laps.pick_teams("Alpine").pick_fastest()
alp_data = alp_laps.get_car_data().add_distance()

rb_laps = qual.laps.pick_teams("Racing Bulls").pick_fastest()
rb_data = rb_laps.get_car_data().add_distance()

wil_laps = qual.laps.pick_teams("Williams").pick_fastest()
wil_data = wil_laps.get_car_data().add_distance()

team_2024 = ['Red Bull Racing', 'Ferrari', 'McLaren', 'Mercedes', 'Haas F1 Team','Aston Martin', 'Kick Sauber', 'Alpine', 'Racing Bulls', 'Williams']
data = ['rbr_data','fer_data','mcl_data','mer_data','haas_data','ast_data','ksb_data','alp_data','rb_data','wil_data']

#Create a dictionary 
dataframes = {
    'Red Bull Racing': rbr_data,
    'Ferrari': fer_data,
    'McLaren': mcl_data,
    'Mercedes': mer_data,
    'Haas F1 Team': haas_data,
    'Aston Martin': ast_data,
    'Kick Sauber': ksb_data,
    'Alpine': alp_data,
    'Racing Bulls': rb_data,
    'Williams': wil_data,
}

# Create a list to store the results
results = []

# Iterate over each team_lap_dataframe
for name, df in dataframes.items():
    results.append(
        {
            'Team': name,
            'Top speed (km/h)': df['Speed'].max().tolist(),
            'Mean speed (km/h)': df['Speed'].mean().tolist()
        }
    )

#Convert dictionnary to DataFrame
results = pd.DataFrame(results)

# create the figure
fig, ax = plt.subplots(figsize=(10, 10))

# make a color palette associating team names to hex codes
team_palette = {team: ff1.plotting.get_team_color(team, session=qual)
                for team in team_2024}

# Scatter plot
for team, mean_speed, top_speed in zip(results['Team'], results['Mean speed (km/h)'], results['Top speed (km/h)']):
    color = team_palette.get(team, 'black')  # Default to black if team color not found
    plt.scatter(mean_speed, top_speed, color=color, label=team, s=100)

    # Annotate the team name
    plt.text(mean_speed - 0.1, top_speed + 0.1, team, fontsize=8)

# Calculate the center of the plot
center_x = (results['Mean speed (km/h)'].min() + results['Mean speed (km/h)'].max()) / 2
center_y = (results['Top speed (km/h)'].min() + results['Top speed (km/h)'].max()) / 2

# Arrows and labels for directions, centered
plt.arrow(center_x, center_y, 0, 2.8, head_width=0.1, head_length=0.1, fc='gray', ec='gray')
plt.arrow(center_x, center_y, 0, -2.8, head_width=0.1, head_length=0.1, fc='gray', ec='gray')
plt.arrow(center_x, center_y, 2.8, 0, head_width=0.1, head_length=0.1, fc='gray', ec='gray')
plt.arrow(center_x, center_y, -2.8, 0, head_width=0.1, head_length=0.1, fc='gray', ec='gray')

# Labels for directions
plt.text(center_x, center_y + 3, 'Low Drag', ha='center', fontsize=10)
plt.text(center_x, center_y - 3.05, 'High Drag', ha='center', fontsize=10)
plt.text(center_x + 3, center_y - 0.15, 'Quick', va='center', fontsize=10)
plt.text(center_x - 3.15, center_y - 0.15, 'Slow', va='center', fontsize=10)

# Diagonal arrows for efficiency
plt.arrow(center_x, center_y, 3, 3, head_width=0.1, head_length=0.1, fc='gray', ec='gray')  # Top-right: High Efficiency
plt.arrow(center_x, center_y, -3, 3, head_width=0.1, head_length=0.1, fc='gray', ec='gray')  # Top-left: Low Efficiency
plt.arrow(center_x, center_y, -3, -3, head_width=0.1, head_length=0.1, fc='gray', ec='gray')  # Bottom-left: Low Efficiency
plt.arrow(center_x, center_y, 3, -3, head_width=0.1, head_length=0.1, fc='gray', ec='gray')  # Bottom-right: High downforce 

# Labels for diagonal directions
plt.text(center_x + 2.55, center_y + 3.1, 'High Efficiency', ha='left', va='bottom', fontsize=10)
plt.text(center_x - 2.35, center_y + 3.1, 'Low Downforce', ha='right', va='bottom', fontsize=10)
plt.text(center_x - 2.45, center_y - 3.1, 'Low Efficiency', ha='right', va='top', fontsize=10)
plt.text(center_x + 2.45, center_y - 3.1, 'High Downforce', ha='left', va='top', fontsize=10)

# Axis labels
plt.xlabel('Mean Speed (km/h)')
plt.ylabel('Top Speed (km/h)')

# Title
plt.title('Aero properties based on Hungary 2025 Qualification')

# Show plot
plt.grid(False)
plt.show()
