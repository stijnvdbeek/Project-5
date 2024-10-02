import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
import pandas as pd
import numpy as np
from IPython.display import display
import warnings
import streamlit as st

# Functies van Constraints importeren
from Constraint_functions import *


# Inladen van data
df_omloopplanning, df_dienstregeling = load_data()

# Converteer tijd kolommen naar datetime objecten voor makkelijke bewerking
df_omloopplanning['starttijd'] = pd.to_datetime(df_omloopplanning['starttijd datum'], errors='coerce')
df_omloopplanning['eindtijd'] = pd.to_datetime(df_omloopplanning['eindtijd datum'], errors='coerce')


# Omloopplanning checken:

# Voer de controle uit
#df_omloopplanning, df_dienstregeling = check_omloopplanning(df_omloopplanning, df_dienstregeling)

# Print resultaten
#omloop_txt, omloop_flase_df, dienst_txt, dienst_false_df = Results_check_omloopplanning(df_omloopplanning, df_dienstregeling)

# Accu percentage controleren:

#df_var_bus, filtered_df, min_SOC_per_omloopnummer, df_omloopplanning = Check_accu(df_omloopplanning)

# Oplaad tijd controle

#error, opladen_df, niet_lang_genoeg_opgeladen_df = Check_oplaad_tijd(df_omloopplanning)


# Streamlit paginas maken

st.set_page_config(
    page_title="Startpagina",
    page_icon= "🏠"
    )

st.title("Startpagina")
st.sidebar("test")