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

#An attempt to normalize race time by fuel consumption correction
#This is the based formula:
#Laptime (FC) = Laptime - (total lap of the GP - lap n°) * Fuel consumption rate * Weight effect
#This is based on the assumption that 1kg of fuel slow the car down by 0.03s (First assumption)
#The fuel consumption rate should be calculate by the maximum fuel in use (maximum 110kg, with 5kg in reserve at the end, so 105kg can be use) (Second assumption)
#Divide these 105kg of fuel by the number of laps of that GP will give the fuel rate consumption.

#Prepare a dataframe of all the GP.
schedule = ff1.get_event_schedule(2025)
schedule['EventName']

fuel_cons = {
    'GP': ['Australian Grand Prix','Chinese Grand Prix','Japanese Grand Prix','Bahrain Grand Prix','Saudi Arabian Grand Prix','Miami Grand Prix','Emilia Romagna Grand Prix','Monaco Grand Prix','Spanish Grand Prix','Canadian Grand Prix',
           'Austrian Grand Prix','British Grand Prix','Belgian Grand Prix','Hungarian Grand Prix','Dutch Grand Prix','Italian Grand Prix','Azerbaijan Grand Prix','Singapore Grand Prix','United States Grand Prix','Mexico City Grand Prix',
           'São Paulo Grand Prix','Las Vegas Grand Prix','Qatar Grand Prix','Abu Dhabi Grand Prix'],
    'Laps': [58,56,53,57,50,57,63,78,66,70,71,52,44,70,72,53,51,62,56,71,71,50,57,58]
}

fuel_cons = pd.DataFrame(fuel_cons)
fuel_cons['Rate'] = 105 / fuel_cons['Laps']

#First let's start with the graph display laptime of one driver, I'm gonna stay with Leclerc for now, and with a specific GP, still Bahrain 2024.
race = ff1.get_session(2024, 'Bahrain Grand Prix', 'R')
race.load()

laps = race.laps.pick_drivers('LEC').pick_quicklaps().reset_index()
# Seaborn doesn't have proper timedelta support,
# so we have to convert timedelta to float (in seconds)
laps["LapTime(s)"] = laps["LapTime"].dt.total_seconds()

#Apply the fuel corrected formula
laps['LapTime(FC)'] = laps["LapTime(s)"] - ((54 - laps["LapNumber"])*1.94*0.03)

laps['delta'] = laps["LapTime(s)"] - laps['LapTime(FC)']

fig, ax = plt.subplots(figsize=(8, 5))

ax.plot(laps['LapTime(s)'],label='LEC')
ax.plot(laps['LapTime(FC)'],label='LEC (FC)')

# add axis labels and a legend
ax.set_xlabel("Lap Number")
ax.set_ylabel("Lap Time(s)")
ax.set_title("Leclerc Bahrain 2024 GP race pace")
ax.legend()
