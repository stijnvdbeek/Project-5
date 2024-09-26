import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
import pandas as pd

df = pd.read_excel('omloopplanning.xlsx', engine='openpyxl')
# Convert starttijd and eindtijd to datetime for proper plotting
df['starttijd datum'] = pd.to_datetime(df['starttijd datum'])
df['eindtijd datum'] = pd.to_datetime(df['eindtijd datum'])

# Assign a color to each unique activity
activities = df['activiteit'].unique()
colors = plt.cm.get_cmap('tab20', len(activities))

color_dict = {activity: colors(i) for i, activity in enumerate(activities)}

# Create the Gantt chart
fig, ax = plt.subplots(figsize=(10, 6))

for idx, row in df.iterrows():
    ax.barh(row['omloop nummer'], 
            row['eindtijd datum'] - row['starttijd datum'], 
            left=row['starttijd datum'], 
            color=color_dict[row['activiteit']],
            edgecolor='black')

# Format x-axis for time
ax.xaxis_date()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

# Create legend
legend_elements = [Patch(facecolor=color_dict[activity], label=activity) for activity in activities]
ax.legend(handles=legend_elements, title="Activiteit", bbox_to_anchor=(1.05, 1), loc='upper left')

# Set labels and title
ax.set_xlabel('Tijd')
ax.set_ylabel('Omloop nummer')
ax.set_title('Omloopplanning Gantt Chart')

plt.tight_layout()
plt.show()