import streamlit as st
import fastf1 as ff1
from fastf1.ergast import Ergast
from fastf1 import plotting
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

# Setup
ff1.plotting.setup_mpl(color_scheme='fastf1')
#ff1.Cache.enable_cache('cache')

# Streamlit UI
st.title("Formula 1 Fuel-Corrected Race Pace Analysis")
st.markdown("""
In motor racing, cars get lighter as fuel is consumed. **Fuel correction** normalizes lap times by accounting for fuel weight.
This app assumes:
- **Fuel consumption rate (fcr):** `105 kg / race length` (110 kg max fuel - 5 kg reserve).
- **Weight effect (weff):** 1 kg of fuel slows the car by **0.03 seconds** ([source](https://www.reddit.com/r/F1Technical/comments/11oskuy/computation_of_fuelcorrected_lap_time)).

The fuel-corrected laptime is calculated as:
""")
st.latex(r'''Laptime(FC) = Laptime - (N - n°) \times fcr \times weff''')
st.caption("Disclaimer: This is an approximation, not official data.")

# Sidebar inputs
year = st.sidebar.selectbox('Select the year', [2024, 2025, 2026])
schedule = Ergast().get_race_schedule(season=year)
event = st.sidebar.selectbox('Select the GP', schedule['raceName'])

# Load session data
@st.cache_data
def load_session(year, event):
    try:
        session = ff1.get_session(year, event, 'Race')
        session.load()
        return session
    except Exception as e:
        st.error(f"Failed to load session: {e}")
        return None

session = load_session(year, event)
if session is None:
    st.stop()

# Preprocess laps
all_laps = session.laps.pick_wo_box().pick_quicklaps().copy(deep = False)
all_laps['LapTime(s)'] = all_laps['LapTime'].dt.total_seconds()

# Tyre strategies visualization
st.header("Tyre Strategies")
drivers = [session.get_driver(driver)["Abbreviation"] for driver in session.drivers]
stints = all_laps[["Driver", "Stint", "Compound", "FreshTyre", "TyreLife"]].groupby(["Driver", "Stint", "Compound", "FreshTyre"]).count().reset_index()
stints['TyreStatus'] = stints.apply(lambda row: f"{row.Compound}, {row.FreshTyre}", axis=1)

# Tyre color mapping
tyre_colors = {
    'HARD, True': '#cacaca', 'HARD, False': '#f0f0ec',
    'MEDIUM, True': '#ffd12e', 'MEDIUM, False': '#f5e5ba',
    'SOFT, True': '#da291c', 'SOFT, False': '#ff8181',
    'INTERMEDIATE, True': '#43b02a', 'INTERMEDIATE, False': '#9de38d',
    'WET, True': '#0067ad', 'WET, False': '#76b2db'
}

# Plot tyre strategies
fig, ax = plt.subplots(figsize=(10, 10), facecolor='white')
plt.title(f"{session.event.year} {session.event['EventName']}\nTyre Strategies")

for driver in drivers:
    driver_stints = stints.loc[stints["Driver"] == driver]
    previous_stint_end = 0
    for _, row in driver_stints.iterrows():
        tyre_colour = tyre_colors.get(row["TyreStatus"], '#808080')
        plot = plt.barh(
            y=driver, width=row["TyreLife"], left=previous_stint_end,
            color=tyre_colour, edgecolor="black", fill=True
        )
        previous_stint_end += row["TyreLife"]
        ax.bar_label(plot, label_type='center')

# Legend and formatting
legend_patches = [
    mpatches.Rectangle((0, 0), 1, 1, color=color, label=status)
    for status, color in tyre_colors.items()
]
plt.legend(handles=legend_patches, ncol=5, bbox_to_anchor=(0.075, -0.55, 0.8, 0.5), loc='upper center')
ax.xaxis.set_ticks(np.arange(10, session.total_laps, 10))
ax.xaxis.grid(True, which='major', linestyle='--', color='black')
ax.set_axisbelow(True)
ax.invert_yaxis()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
plt.tight_layout()
st.pyplot(fig)

# Non-normalized race pace (boxplot)
st.header("Non-Normalized Race Pace")
secondsamp = all_laps.loc[(all_laps['PitOutTime'].isnull() & all_laps['PitInTime'].isnull())].pick_quicklaps()
finalsamp = secondsamp.pick_drivers(drivers)
peckingorder = finalsamp[["Driver", "TimeSeconds"]].groupby("Driver").mean()["TimeSeconds"].sort_values().index
colourcode = {driver: ff1.plotting.get_driver_color(driver, colormap='official', session=session) for driver in peckingorder}

fig, ax = plt.subplots(figsize=(10, 10))
sns.boxplot(
    data=finalsamp, x="Driver", y="TimeSeconds", hue="Driver", order=peckingorder,
    palette=colourcode, whiskerprops=dict(color="black"), boxprops=dict(edgecolor="black"),
    medianprops=dict(color="black"), capprops=dict(color="black"),
    showmeans=True, meanline=True, meanprops=dict(color='black', linestyle='--')
)
ax.set_title(f"{session.event.year} {session.event['EventName']}\nRace Pace Comparison (Outliers Hidden)")
ax.set(ylabel='Lap Time (secs)')
ax.yaxis.grid(True)
plt.minorticks_on()
plt.grid(linestyle='--', color='#404040', which='minor', axis='y', linewidth=0.5)
plt.plot([], [], '--', linewidth=1, color='black', label='mean')
plt.plot([], [], '-', linewidth=1, color='black', label='median')
plt.legend(loc='best')
plt.tight_layout()
st.pyplot(fig)

# Fuel-corrected race pace
st.header("Fuel-Corrected Race Pace")
drivs = st.sidebar.multiselect('Select drivers to compare', drivers)
if not drivs:
    st.warning("Please select at least one driver.")
    st.stop()

weight_eff = 0.03
fuel_cons_rate = 105 / session.total_laps
df = all_laps.pick_drivers(drivs).reset_index()
df['LapTime(s)'] = df['LapTime'].dt.total_seconds()
df['LapTime(FC)'] = df["LapTime(s)"] - ((session.total_laps - df["LapNumber"]) * fuel_cons_rate * weight_eff)
laps = pd.DataFrame({
    'Driver': df['Driver'], 'Team': df['Team'], 'LapNumber': df['LapNumber'],
    'Compound': df['Compound'], 'Stint': df['Stint'], 'TyreLife': df['TyreLife'],
    'LapTime(s)': df['LapTime(FC)']
})

# Scatter plot with regression lines
fig, ax = plt.subplots(figsize=(10, 10))
plt.suptitle(f"{session.event.year} {session.event['EventName']}, {session.name}\nTyre Degradation Analysis (Fuel-Corrected)")
sns.scatterplot(
    data=df, x="LapNumber", y="LapTime(FC)", ax=ax, hue='Driver',
    palette=ff1.plotting.get_driver_color_mapping(session=session),
    s=50, linewidth=0, legend='auto', style='Driver'
)

# Regression lines per stint
tyre_stints = stints[stints['Driver'].isin(drivs)].groupby('Driver')['Stint'].nunique()
for dri in drivs:
    n = tyre_stints.loc[dri]
    style = ff1.plotting.get_driver_style(identifier=dri, style=['color', 'linestyle'], session=session)
    for i in range(1, n + 1):
        sns.regplot(
            data=df[(laps['Driver'] == dri) & (laps['Stint'] == i)],
            x="LapNumber", y="LapTime(FC)",
            color=ff1.plotting.get_driver_color(dri, session=session),
            line_kws=style, scatter=False, ci=None
        )

ax.set_xlabel("Lap Number")
ax.set_ylabel("Fuel-Corrected Laptime (secs)")
plt.grid(linestyle='--', color='#808080', which='major', axis='both')
plt.minorticks_on()
plt.grid(linestyle='--', color='#404040', which='minor', axis='both', linewidth=0.5)
plt.legend(loc='best')
sns.despine(left=True, bottom=True)
plt.tight_layout()
st.pyplot(fig)

st.caption("""
Remark: If two drivers from the same team are selected, the regression line of the "second" driver (higher racing number) will be dashed.
""")
