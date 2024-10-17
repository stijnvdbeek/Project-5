# python -m streamlit run .\0_??_Startpagina.py

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
import pandas as pd
import numpy as np
from IPython.display import display
import warnings
import streamlit as st
import os
from datetime import time

# Functies van Constraints importeren
from Constraint_functions import *


# Inladen van data
#df_omloopplanning, df_dienstregeling = load_data()

# Converteer tijd kolommen naar datetime objecten voor makkelijke bewerking
#df_omloopplanning['starttijd'] = pd.to_datetime(df_omloopplanning['starttijd datum'], errors='coerce')
#df_omloopplanning['eindtijd'] = pd.to_datetime(df_omloopplanning['eindtijd datum'], errors='coerce')


# Omloopplanning checken:

# Voer de controle uit
#df_omloopplanning, df_dienstregeling = check_omloopplanning(df_omloopplanning, df_dienstregeling)

# Print resultaten
#omloop_txt, omloop_flase_df, dienst_txt, dienst_false_df = Results_check_omloopplanning(df_omloopplanning, df_dienstregeling)

# Accu percentage controleren:

#df_var_bus, filtered_df, min_SOC_per_omloopnummer, df_omloopplanning = Check_accu(df_omloopplanning,batterijslijtage)

# Oplaad tijd controle

#error, opladen_df, niet_lang_genoeg_opgeladen_df = Check_oplaad_tijd(df_omloopplanning)


# Streamlit paginas maken

st.set_page_config(
    page_title="Home",
    page_icon= "🏠"
    )

st.title("Settings 🏠")
st.sidebar.success('Choose a page')



path_omloopplanning = st.file_uploader('Upload omloopplanning: ', type='xlsx', accept_multiple_files= False)

Path_dienstregeling = st.file_uploader('Upload dienstregeling: ', type= 'xlsx', accept_multiple_files= False)

batterijslijtage = st.select_slider("Choose state of health value (for all busses):", options=[85, 90, 95])

#verbruik_marge = st.select_slider("Choose a marge for energy use (average KWH = 1.2)")

bereken = st.button('Calculate!')

if bereken:
    st.write('Calculating...')
    #inladen
    df_omloopplanning, df_dienstregeling = load_data(path_omloopplanning, Path_dienstregeling)

    df_omloopplanning['starttijd'] = pd.to_datetime(df_omloopplanning['starttijd datum'], errors='coerce')
    df_omloopplanning['eindtijd'] = pd.to_datetime(df_omloopplanning['eindtijd datum'], errors='coerce')
    
    #planning controleren
    df_omloopplanning, df_dienstregeling = check_omloopplanning(df_omloopplanning, df_dienstregeling)

    omloop_txt, omloop_flase_df, dienst_txt, dienst_false_df = Results_check_omloopplanning(df_omloopplanning, df_dienstregeling)
    st.header('Results:')

    if omloop_flase_df.shape[0] != 0:
        st.write(omloop_txt, ' ⛔')
        st.write(omloop_flase_df)
    else:
        st.markdown('**The omloopplanning fills all jobs:** ✅')
    
    if dienst_false_df.shape[0] != 0:
        st.write(dienst_txt, ' ⛔')
        st.write(dienst_false_df)
    else:
        st.markdown('**No missing jobs(according to dienstregeling):** ✅')

    # Accu percentage controleren

    df_var_bus, filtered_df, min_SOC_per_omloopnummer, df_omloopplanning = Check_accu(df_omloopplanning,batterijslijtage)
    if filtered_df.shape[0] != 0:
        st.write(f'Jobs with low battery: {filtered_df.shape[0]} ⛔ ')
        st.write(filtered_df)
    else:
        st.markdown("**No jobs with to low battery:** ✅")

    # Oplaat tijd controleren:

    error, opladen_df, niet_lang_genoeg_opgeladen_df = Check_oplaad_tijd(df_omloopplanning)

    if niet_lang_genoeg_opgeladen_df.shape[0] != 0:
        st.write(f'Times a bus in charching for a to short duration: {niet_lang_genoeg_opgeladen_df.shape[0]} ⛔')
        st.write(niet_lang_genoeg_opgeladen_df)
    else:
        st.markdown('**All busses charged for a minimal of 15 minutes:** ✅')
    
    Gantt_chart(df_omloopplanning)

    
    



