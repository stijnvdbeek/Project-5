import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
import pandas as pd
import numpy as np
from IPython.display import display
import warnings

# Functies van Constraints importeren
from Constraint_functions import *


# Inladen van data
df_omloopplanning, df_dienstregeling = load_data()

# Converteer tijd kolommen naar datetime objecten voor makkelijke bewerking
df_omloopplanning['starttijd'] = pd.to_datetime(df_omloopplanning['starttijd datum'], errors='coerce')
df_omloopplanning['eindtijd'] = pd.to_datetime(df_omloopplanning['eindtijd datum'], errors='coerce')

# Voer de controle uit
df_omloopplanning, df_dienstregeling = check_omloopplanning(df_omloopplanning, df_dienstregeling)

# Print resultaten
print(Result_check_omloopplanning(df_omloopplanning))
print(Result_check_dienstregeling(df_dienstregeling))