import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
import pandas as pd
import numpy as np

df = pd.read_excel('4. Verbeterde omloopplanning.xlsx', engine='openpyxl')
# Convert starttijd and eindtijd to datetime for proper plotting
df['starttijd datum'] = pd.to_datetime(df['starttijd datum'])
df['eindtijd datum'] = pd.to_datetime(df['eindtijd datum'])

# Assign a color to each unique activity
df['actieviteitBuslijn'] = df['activiteit'] + ' ' + df['buslijn'].fillna(' ').astype(str)
activities = df['actieviteitBuslijn'].unique()

# Use the updated method to get the colormap
cmap = plt.colormaps.get_cmap('turbo')
colors = [cmap(i / len(activities)) for i in range(len(activities))]

color_dict = {activity: colors[i] for i, activity in enumerate(activities)}

# Create the Gantt chart
fig, ax = plt.subplots(figsize=(18, 9))

for idx, row in df.iterrows():
    ax.barh(row['omloop nummer'], 
            row['eindtijd datum'] - row['starttijd datum'], 
            left=row['starttijd datum'], 
            color=color_dict[row['actieviteitBuslijn']],
            edgecolor='black')

# Format x-axis for time
ax.xaxis_date()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))


# Format Y-axis for jumps of one
ax.set_yticks(np.arange(0, 21, 1))

# Create legend
legend_elements = [Patch(facecolor=color_dict[activity], label=activity) for activity in activities]
ax.legend(handles=legend_elements, title="Activiteit", bbox_to_anchor=(1.05, 1), loc='upper left')

# Set labels and title
ax.set_xlabel('Tijd')
ax.set_ylabel('Omloop nummer')
ax.set_title('Omloopplanning Gantt Chart')

plt.tight_layout()
plt.savefig('Omloopplanning_Gantt.png')
