import streamlit as st
import streamlit.components.v1 as components

import fastf1 as ff1
from fastf1.ergast import Ergast
from fastf1 import plotting
from fastf1 import utils

import seaborn as sns

from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
from matplotlib import cm
import matplotlib.patches as mpatches

import datetime as dt
import numpy as np
import pandas as pd

# the misc_mpl_mods option enables minor grid lines which clutter the plot
#ff1.plotting.setup_mpl(color_scheme='fastf1') #color_scheme='official' or 'fastf1'

#ff1.Cache.clear_cache('cache')
#ff1.Cache.enable_cache('cache')

#Compound names are BLOCKED LETTERS

#Streamlit display components
st.title("Formula 1 Fuel-corrected race pace analysis")

st.text("In motor racing, towards the end of the race, cars get lighter as fuel is consumed, so how should we compare these laps? There is a normalization process called fuel correction, which renders different lap times set by cars more comparable. However, fuel consumption data per car per lap is logically unavailable for us fans, so assumptions have to be made.\n")
st.text("The first assumption aim to simplified fuel consumption in each car, where every car will start the race with the maximum fuel allowance, and end the race with the minimum allowed level. The current F1's regulation allows each car to hold 110kg of fuel, and a minimum of 5kg of reserve at the end for random check, thus 105kg to be used. \n")
st.text("Consequently, the fuel consumption rate (fcr) can be calculate for each circuit, based on its length, by dividing 105 kg of fuel to the circuit length: \n")

st.latex(r'''
    fcr = \frac{105}{length}
''')

st.text("The second assumption is that 1kg of fuel slows the car down by 0.03s (weff), based on this reddit thread: ")
st.page_link("https://www.reddit.com/r/F1Technical/comments/11oskuy/computation_of_fuelcorrected_lap_time", label = "Reddit", icon  ="🌎")

st.text("The laptime adjustment of a specific lap can be made by substracting the lap time by the product of the difference between the total lap of the GP (N) and the current lap number (n°), the fcr and the weight effect (weff) :")
st.latex(r'''
    Laptime(FC) = Laptime - (N - n°) * fcr * weff
''')

st.caption("Disclaimer: Argument can be made for this approach to be called 'adjusted based on assumption' rather than 'fuel corrected'.\n")

st.header("Choose the year and the GP from the side bar on the left to obtain each driver tyre strategies and a boxplot of their non-normalized race pace")

year = st.sidebar.radio(
    'Select the year', (2024, 2025)
)

#Get the schedule of the chosen year
schedule = Ergast().get_race_schedule(season=year)

event = st.sidebar.selectbox(
    'Select the GP', schedule['raceName'])

session = ff1.get_session(year, event, 'Race')
session.load()
all_laps = session.laps.pick_wo_box().pick_quicklaps().copy(deep=False)
all_laps['LapTime(s)'] = all_laps['LapTime'].dt.total_seconds()

##TYRE STRATEGIES
laps = session.laps
drivers = session.drivers # Get the list of driver numbers
drivers = [session.get_driver(driver)["Abbreviation"] for driver in drivers] # Convert driver numbers to letter abbreviations

stints = laps[["Driver", "Stint", "Compound", "FreshTyre", "TyreLife"]]
stints = stints.groupby(["Driver", "Stint", "Compound", "FreshTyre"]) #group the laps first by driver, then stint number, then compound and finally tyre status (new/used)
stints = stints.count().reset_index() #count the number of laps in each group
stints['TyreStatus'] = stints.apply(lambda row: f"{row.Compound}, {row.FreshTyre}", axis=1) # create new data column "TyreStatus" from columns "Compound" and "FreshTyre"

# create entries for legendbox
hardnew = mpatches.Rectangle((0, 0), 1, 1, color='#cacaca', label='HARD new')
hardused = mpatches.Rectangle((0, 0), 1, 1, color='#f0f0ec', label='HARD used')
mednew = mpatches.Rectangle((0, 0), 1, 1, color='#ffd12e', label='MEDIUM new')
medused = mpatches.Rectangle((0, 0), 1, 1, color='#f5e5ba', label='MEDIUM used')
softnew = mpatches.Rectangle((0, 0), 1, 1, color='#da291c', label='SOFT new')
softused = mpatches.Rectangle((0, 0), 1, 1, color='#ff8181', label='SOFT used')
internew = mpatches.Rectangle((0, 0), 1, 1, color='#43b02a', label='INTER new')
interused = mpatches.Rectangle((0, 0), 1, 1, color='#9de38d', label='INTER used')
wetnew = mpatches.Rectangle((0, 0), 1, 1, color='#0067ad', label='WET new')
wetused = mpatches.Rectangle((0, 0), 1, 1, color='#76b2db', label='WET used')
colourcode = [hardnew, hardused, mednew, medused, softnew, softused, internew, interused, wetnew, wetused]


fig, ax = plt.subplots(figsize=(10, 10), facecolor='white')
plt.title(f"{session.event.year} {session.event['EventName']}\nTyre strategies")

for driver in drivers:
    driver_stints = stints.loc[stints["Driver"] == driver]
    previous_stint_end = 0
    for idx, row in driver_stints.iterrows():
        if row["TyreStatus"]=='HARD, True': tyrecolour ='#cacaca'
        elif row["TyreStatus"]=='HARD, False': tyrecolour ='#f0f0ec'
        elif row["TyreStatus"]=='MEDIUM, True': tyrecolour ='#ffd12e'
        elif row["TyreStatus"]=='MEDIUM, False': tyrecolour ='#f5e5ba'
        elif row["TyreStatus"]=='SOFT, True': tyrecolour ='#da291c'
        elif row["TyreStatus"]=='SOFT, False': tyrecolour ='#ff8181'
        elif row["TyreStatus"]=='INTERMEDIATE, True': tyrecolour ='#43b02a'
        elif row["TyreStatus"]=='INTERMEDIATE, False': tyrecolour ='#9de38d'
        elif row["TyreStatus"]=='WET, True': tyrecolour ='#0067ad'
        else: tyrecolour ='#76b2db'
        # each row contains the compound name and stint length - we can use these information to draw horizontal bars
        plot = plt.barh(
            y=driver,
            width=row["TyreLife"],
            left=previous_stint_end,
            color=tyrecolour,
            edgecolor="black",
            fill=True
        )
        previous_stint_end += row["TyreLife"]
        ax.bar_label(plot, label_type='center')

plt.xlabel("Lap Number")
plt.legend(handles = colourcode, ncol = 5, bbox_to_anchor = (0.075, -0.55, 0.8, 0.5), loc = 'upper center')
#ax.legend(handles = colourcode, bbox_to_anchor = (1, 0.5), loc = 'center left', labelspacing = 1.2)
ax.xaxis.set_ticks(np.arange(start=10, stop=session.total_laps, step=10))
ax.xaxis.grid(True, which='major', linestyle='--', color='black')
ax.set_axisbelow(True)
ax.invert_yaxis() # invert y-axis so drivers that finish higher are closer to the top
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
plt.tight_layout()

st.pyplot(fig)

##NON-NORMALIZE RACE PACE:
# Convert sector-/laptimes to seconds
session.laps['TimeSeconds'] = session.laps['LapTime'].dt.total_seconds() #Sector1Time, Sector2Time, Sector3Time, LapTime

# Exclude in-/outlaps - 2 options -> exclude slow laps (e.g. laps under SC/VSC/red flag)
secondsamp = session.laps.loc[(session.laps['PitOutTime'].isnull() & session.laps['PitInTime'].isnull())].pick_quicklaps()

# Pick specific drivers/teams
#driverslist = ['VER', 'NOR', 'PIA', 'RUS', 'LEC']
#teamslist = ['Red Bull Racing', 'Mercedes', 'Ferrari', 'McLaren']
finalsamp = secondsamp.pick_drivers(drivers) #pick_drivers(driverslist), pick_teams(teamslist)

# order the drivers/teams from the fastest (lowest median lap time) to slowest
peckingorder = (
    finalsamp[["Driver", "TimeSeconds"]] #"Driver", "Team"
    .groupby("Driver") #"Driver", "Team"
    .mean()["TimeSeconds"] #median() for sorting by median (specific stint/compound), mean() for sorting by mean (race overall)
    .sort_values()
    .index
)

colourcode = {driver: ff1.plotting.get_driver_color(driver, colormap='official', session=session) for driver in peckingorder} # use if fastf1 colours are preferred
#colourcode = {team: fastf1.plotting.get_team_color(team, colormap='official', session=session) for team in peckingorder} # use if fastf1 colours are preferred

fig, ax = plt.subplots(figsize=(10, 10))
sns.boxplot(data=finalsamp,
            x="Driver", # set x-label: "Driver","Team"
            y="TimeSeconds", # set y-label
            hue = "Driver", # "Driver", "Team"
            order = peckingorder,
            palette = colourcode,
            whiskerprops=dict(color="gray"),
            boxprops=dict(edgecolor="white"),
            medianprops=dict(color="white"),
            capprops=dict(color="white"),
            showmeans=True, meanline=True, meanprops=dict(color='white', linestyle='--'), # show/hide means
            showfliers= False, flierprops=dict(markerfacecolor='white', markeredgecolor='white') # show/hide outliers & set colour (fill, border)
)
ax.set_title(f"{session.event.year} {session.event['EventName']}\n{session.name} pace comparison")
ax.set(ylabel = 'Lap time (secs)')
ax.yaxis.grid(True)
ax.set(xlabel=None) # x-label is redundant - "Driver"/"Team" will not be shown

plt.minorticks_on() #show minor grid lines
plt.grid(linestyle='--', color='#404040', which='minor', axis='y', linewidth = 0.5)
plt.plot([], [], '--', linewidth=1, color='black', label='mean')
plt.plot([], [], '-', linewidth=1, color='black', label='median')
plt.legend(loc = 'best')

plt.tight_layout()
st.pyplot(fig)

drivs = st.sidebar.multiselect(
    'Select drivers to compared their fuel-corrected race pace', (drivers))
 
#FEATURE TO BE ADDED AFTERWARD??? 
#compound = st.sidebar.radio(
#    'Select tyres to compared' , pd.unique(stints['Compound']))

##FUEL CONSUMPTION CORRECTION ANALYSIS
weight_eff = 0.03
fuel_cons_rate = 105 / session.total_laps

df = all_laps.pick_drivers(drivs).reset_index()
df['LapTime(s)'] = df['LapTime'].dt.total_seconds()
#teams = ['Red Bull Racing', 'McLaren', 'Ferrari', 'Mercedes']
#df = session.laps.pick_teams(teams).pick_wo_box().pick_quicklaps().reset_index()

#Create new dataframe containing the additional data on Laptime (FC)
df['LapTime(FC)'] = df["LapTime(s)"] - ((session.total_laps - df["LapNumber"])*fuel_cons_rate*weight_eff)
laps = pd.DataFrame({'Driver': df['Driver'], 'Team': df['Team'], 'LapNumber': df['LapNumber'], 'Compound': df['Compound'], 'Stint':df['Stint'], 'TyreLife': df['TyreLife'], 'LapTime(s)': df['LapTime(FC)']})

#DRAW SCATTER PLOT:
fig, ax = plt.subplots(figsize=(10, 10))
plt.suptitle(f"{session.event.year} {session.event['EventName']}, {session.name}\n Tyre degradration analysis - all stint (separated regression line for each stint)") #, {compound} compound
sns.scatterplot(data = df,
                #    = laps - normal & fuel-corrected: race overall
                #    = laps.loc[laps['Compound']==compound] - fuel-corrected: specific compound/stint
                x = "LapNumber",
                # = "LapNumber" - normal & fuel-corrected: race overall
                # = "TyreLife" - fuel-corrected: specific compound/stint
                y = "LapTime(FC)",
                ax = ax,
                hue = 'Driver',
                #   = "Compound" - normal: different compounds of one driver only
                #   = grouping   - normal: multiple drivers comparison
                #   = 'Driver'   - fuel corrected
                palette = ff1.plotting.get_driver_color_mapping(session=session),
                #       = fastf1.plotting.get_compound_mapping(session=session)           - normal: different compounds of one driver only
                #       = fastf1.plotting.get_driver_color_mapping(session=session)       - normal & fuel-corrected: multiple drivers on specific compound/stint
                #       = colourcode                                                      - normal: multiple drivers on different compounds
                #       = [fastf1.plotting.get_driver_color('LEC', session=session), 'w'] - fuel-corrected: example of customization
                s = 50, # dot size
                linewidth = 0, # disable dot border
                legend = 'auto',
                style = 'Driver'
               )


#Get the number of stints for chosen driver, group by driver and count their unique tyre stints:
tyre_stints = stints[stints['Driver'].isin(drivs)].groupby('Driver')['Stint'].nunique()

#DRAW REGRESSION LINE:
for dri in drivs:
    n = tyre_stints.loc[dri]
    style = plotting.get_driver_style(identifier=dri, style= ['color','linestyle'],session = session)
    for i in range (1,n+1):
        sns.regplot(data = df[(laps['Driver']==dri)&(laps['Stint']==i)], #AND-criteria for analysis of specific compound/stint: .loc[(driver) & (compound/stint)]
            x = "LapNumber",
            # = 'LapNumber'
            # = 'TyreLife',
            y = "LapTime(FC)",
            color= ff1.plotting.get_driver_color(dri, session=session),
            line_kws= style,
            scatter = False, #scatter points not drawn, avoiding overlap with scatterplot above
            ci = None # confidence interval band not displayed
           )

ax.set_xlabel("Tyre age (laps)") #raace overall analysis: "Lap Number"; specific compound/stint analysis: "Tyre Age (laps)"
ax.set_ylabel("Fuel-corrected laptime (secs)")
#ax.yaxis.set_ticks(np.arange(np.floor(laps['LapTime(s)'].min()), np.ceil(laps['LapTime(s)'].max()), 0.2))
plt.grid(linestyle='--', color='#808080', which='major', axis='both') #major grid lines settings
plt.minorticks_on() #show minor grid lines
plt.grid(linestyle='--', color='#404040', which='minor', axis='both', linewidth = 0.5) #minor grid lines settings
plt.legend(loc = 'best') # set location of legend in subplot
sns.despine(left=True, bottom=True)
plt.tight_layout()
st.pyplot(fig)

st.caption("Disclaimer: In the event that two drivers from the same team are selected, the second selected driver will always have points not represented as circles, and its regression line will be displayed as a dashed line.\n")


