import streamlit as st

import fastf1 as ff1
from fastf1.ergast import Ergast
import fastf1.plotting

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from matplotlib.collections import LineCollection
from scipy.ndimage import gaussian_filter1d

#Header display and select box
st.header("Formula 1 Hotlap comparison")
st.text("This analysis compares the quickest qualifying lap between two drivers over the circuit map.\n")
st.text("The color of each corner indicates the faster driver over that corner.\n")
st.text("The table at the end compares the time gained over every corner, feel free to sort by corner number or by the time gained.\n")

#Year and event selection
year = st.selectbox(
'Select the year', (2022,2023,2024,2025,2026))

#It would be best to to able to select this schedule and 
schedule = Ergast().get_race_schedule(season=year)

col1, col2 = st.columns(2)

with col1:
    event = st.selectbox(
    'Select the Grand Prix, and then the type of qualifying session :', schedule['raceName'])

with col2:
    session_type = st.selectbox(
    'Please only select Sprint for track with sprint qualifying session :', ('FP1','FP2','FP3','Sprint Qualifying','Qualifying')
)

#Load the session
session = ff1.get_session(year, event, session_type)
session.load()

#Print out the qualifying result

#fastf1.plotting.setup_mpl(color_scheme='fastf1') #color_scheme='official' or 'fastf1'

all_laps = session.laps.pick_quicklaps()
all_laps = all_laps.dropna(subset=[
    'LapTime',
    'Sector1Time',
    'Sector2Time',
    'Sector3Time'
])

drivers = pd.unique(all_laps['Driver'])

all_laps['LapTime(s)'] = all_laps['LapTime'].dt.total_seconds()
all_laps['Sector1(s)'] = all_laps['Sector1Time'].dt.total_seconds()
all_laps['Sector2(s)'] = all_laps['Sector2Time'].dt.total_seconds()
all_laps['Sector3(s)'] = all_laps['Sector3Time'].dt.total_seconds()
#drivers = pd.unique(all_laps['Driver']) # all drivers
#teams = pd.unique(all_laps['Team']) # all teams
ult = all_laps['Sector1(s)'].min() + all_laps['Sector2(s)'].min() + all_laps['Sector3(s)'].min() # Ultimate lap (combination of best three sector times)

df = []
for driver in drivers:

    driver_laps = all_laps.pick_drivers(driver)

    s1 = driver_laps['Sector1(s)'].min()
    s2 = driver_laps['Sector2(s)'].min()
    s3 = driver_laps['Sector3(s)'].min()

    df.append({
        'Driver': driver,
        'S1_delta': s1 - all_laps['Sector1(s)'].min(),
        'S2_delta': s2 - all_laps['Sector2(s)'].min(),
        'S3_delta': s3 - all_laps['Sector3(s)'].min(),
        'Total_delta': (s1 - all_laps['Sector1(s)'].min()) +
                       (s2 - all_laps['Sector2(s)'].min()) +
                       (s3 - all_laps['Sector3(s)'].min()),
        'Gap_PB_ideal':
            driver_laps.pick_fastest()['LapTime(s)'] -
            (s1 + s2 + s3)
    })
    
df = pd.DataFrame(df)
df = df.sort_values(by='Total_delta', ascending=False)
   
fig1, ax = plt.subplots(figsize=(8, 8))

ax.set_title(
    f"{session.event.year} {session.event['EventName']}, {session.name}\nIdeal vs actual laptimes")

plt.barh(y=df['Driver'], width=df['S1_delta'], left=0, color='#FF0000', label='Gap to best-overall S1 time', fill=True)
plt.barh(y=df['Driver'], width=df['S2_delta'], left=(df['S1_delta']), color='#00A1FF', label='Gap to best-overall S2 time', fill=True)
plt.barh(y=df['Driver'], width=df['S3_delta'], left=(df['S1_delta'] + df['S2_delta']), color='#FFEA00', label='Gap to best-overall S3 time', fill=True)
plt.scatter(x=df['Total_delta'], y=df['Driver'], color='#C900FF', label='Ideal PB', zorder=2)
plt.plot((df['Total_delta']+df['Gap_PB_ideal']), df['Driver'], color='#5EFF00', label='Actual PB', linestyle="--", marker="o", zorder=1)
plt.legend()
plt.xlabel(f"Gap (s) from ideal personal-best lap to \"ultimate\" lap ({ult} s)")
plt.grid(linestyle='--', color='#808080', which='major', axis='x') #major grid lines settings
plt.minorticks_on() #show minor grid lines
plt.grid(linestyle='--', color='#404040', which='minor', axis='x', linewidth = 0.5) #minor grid lines settings    

# Display in Streamlit
st.pyplot(fig1)

#Driver selection
col1, col2 = st.columns(2)

with col1:
    driver1 = st.selectbox("First driver", drivers)

with col2:
    if driver1:
        remaining_options = [x for x in drivers if x != driver1]
        driver2 = st.selectbox("Second driver", remaining_options)

lap1 = session.laps.pick_driver(driver1).pick_fastest()
lap2 = session.laps.pick_driver(driver2).pick_fastest()

tel1 = lap1.get_telemetry().add_distance()
tel2 = lap2.get_telemetry().add_distance()

# ---- DISTANCE AXIS ----
lap_length = tel1["Distance"].max()
distance = np.linspace(0, lap_length, 1800)

# ---- INTERPOLATE TIMES ----
t1 = np.interp(distance, tel1["Distance"], tel1["Time"].dt.total_seconds())
t2 = np.interp(distance, tel2["Distance"], tel2["Time"].dt.total_seconds())

delta = t2 - t1

# ---- SMOOTH DELTA ----
sigma = 6
delta = gaussian_filter1d(delta, sigma)

# ---- INTERPOLATE TRACK ----
x = np.interp(distance, tel1["Distance"], tel1["X"])
y = np.interp(distance, tel1["Distance"], tel1["Y"])

# ---- NORMALIZE TRACK ----
x = x - np.mean(x)
y = y - np.mean(y)

scale = max(np.max(np.abs(x)), np.max(np.abs(y)))
x = x / scale
y = y / scale


# ---- BUILD TRACK SEGMENTS ----
points = np.array([x, y]).T.reshape(-1,1,2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)

# ---- PLOT ----
fig, ax = plt.subplots(figsize=(8,8))

norm = plt.Normalize(-abs(delta).max(), abs(delta).max())

# ---- CORNER GAINS ----
circuit_info = session.get_circuit_info()

corner_distances = []

for _, corner in circuit_info.corners.iterrows():

    cx = corner["X"]
    cy = corner["Y"]

    # Find closest telemetry point
    dist_idx = np.argmin((tel1["X"] - cx)**2 + (tel1["Y"] - cy)**2)

    corner_distance = tel1["Distance"].iloc[dist_idx]

    corner_distances.append(corner_distance)
    
#Compute gains betwwen corners
corner_distances = np.array(corner_distances)

corner_delta = []

for d in corner_distances:
    idx = np.argmin(np.abs(distance - d))
    corner_delta.append(delta[idx])

corner_delta = np.array(corner_delta)

# Gain between corners
corner_gain = np.diff(corner_delta, prepend=0)

# ---- CORNER LABELS (NUMBER ONLY) ----
circuit_info = session.get_circuit_info()

offset = 0.06

corner_table = []

for i, corner in circuit_info.corners.iterrows():

    cx = corner["X"]
    cy = corner["Y"]

    # Normalize coordinates
    cx = cx - np.mean(tel1["X"])
    cy = cy - np.mean(tel1["Y"])

    cx = cx / scale
    cy = cy / scale

    # Find closest telemetry point
    idx = np.argmin((x - cx)**2 + (y - cy)**2)

    # Track direction
    dx = x[min(idx+1, len(x)-1)] - x[max(idx-1,0)]
    dy = y[min(idx+1, len(y)-1)] - y[max(idx-1,0)]

    length = np.sqrt(dx**2 + dy**2)
    dx /= length
    dy /= length

    # Perpendicular vector
    nx = -dy
    ny = dx

    # Label position
    lx = cx + nx * offset
    ly = cy + ny * offset

    # White dot at corner
    ax.scatter(cx, cy, color="white", s=8, zorder=5)

    gain = corner_gain[i]

    # Color depending on faster driver
    if gain > 0:
        color = "red"     # driver 1 faster
    else:
        color = "blue"    # driver 2 faster

    # Draw only the corner number
    ax.text(
        lx,
        ly,
        f"{int(corner['Number'])}",
        color="white",
        fontsize=9,
        ha="center",
        va="center",
        bbox=dict(
            facecolor=color,
            edgecolor="black",
            linewidth=0.5,
            alpha=0.9,
            pad=1
        )
    )

    # Save data for table
    corner_table.append({
        "Turn": int(corner["Number"]),
        "Delta (s)": round(gain, 3)
    })
lc = LineCollection(
    segments,
    cmap="coolwarm",
    norm=norm,
    linewidth=5
)

lc.set_array(delta)
ax.add_collection(lc)

# ---- LOCK AXIS LIMITS ----
ax.set_xlim(-1.1,1.1)
ax.set_ylim(-1.1,1.1)

ax.set_aspect("equal")
ax.axis("off")

# ---- COLORBAR ----
cbar = fig.colorbar(lc, ax=ax, shrink=0.75)
cbar.set_label("Delta (s)")

# ---- TITLE ----
ax.set_title(
    f"{year} {event} Qualifying\n{driver1} vs {driver2}",
    color="black"
)

# ---- DRIVER COLOR CAPTION ----
ax.text(
    0,
    -1.25,
    f"Red = {driver1} faster    |    Blue = {driver2} faster",
    ha="center",
    fontsize=10,
    bbox=dict(facecolor="white", alpha=0.8, edgecolor="none", pad=3)
)

st.pyplot(fig)

corner_df = pd.DataFrame(corner_table)

corner_df["Faster Driver"] = corner_df["Delta (s)"].apply(
    lambda x: driver1 if x > 0 else driver2
)

corner_df["Gain (s)"] = corner_df["Delta (s)"].abs()

corner_df = corner_df[["Turn", "Faster Driver", "Gain (s)"]]

st.subheader("Corner Time Gains")

st.dataframe(
    corner_df,
    use_container_width=True,
    hide_index=True
)



