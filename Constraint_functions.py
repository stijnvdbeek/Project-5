import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
import pandas as pd
import numpy as np
from IPython.display import display
import warnings
import os

# Functie om data in te laden

def load_data(path_omloopplanning,path_dienstregeling):

    # Zet de Excel bestanden in DataFrames
    df_omloopplanning = pd.read_excel(path_omloopplanning, engine='openpyxl')
    df_dienstregeling = pd.read_excel(path_dienstregeling, engine='openpyxl')
    return df_omloopplanning, df_dienstregeling

# Waarschuwingen negeren
warnings.filterwarnings('ignore')


# Functie die diensten matcht met de dienstregeling
# En de resultaten leveren:

def check_omloopplanning(omloop_df, dienst_df):

    # Voeg een nieuwe kolom toe om de correctheid te markeren
    omloop_df['correct'] = False

    # Filter alleen op dienstritten in omloopplanning
    dienst_ritten_omloop = omloop_df[omloop_df['activiteit'] == 'dienst rit']
    
    for idx, row in dienst_ritten_omloop.iterrows():
        # Filter voor de overeenkomstige rijen in de dienstregeling
        dienst_rows = dienst_df[
            (dienst_df['startlocatie'] == row['startlocatie']) &
            (dienst_df['eindlocatie'] == row['eindlocatie']) &
            (dienst_df['buslijn'] == row['buslijn'])
        ]
        
        for _, dienst_row in dienst_rows.iterrows():
            # Maak een vertrektijd datetime object
            if pd.isna(row['starttijd']):
                print(f"Skipping row {idx} because of NaT (Not a Time)")
                continue
            
            vertrektijd = pd.to_datetime(f"{row['starttijd'].date()} {dienst_row['vertrektijd'].strip()}")
            
            # Controleer of de starttijd overeenkomt met de dienstregeling
            if vertrektijd == row['starttijd']:
                omloop_df.at[idx, 'correct'] = True
                break

    # Controleer of alle ritten in de dienstregeling aanwezig zijn in de omloopplanning
    dienst_df['found_in_omloop'] = False

    for idx, row in dienst_df.iterrows():
        try:
            omloop_rows = omloop_df[
                (omloop_df['startlocatie'] == row['startlocatie']) &
                (omloop_df['eindlocatie'] == row['eindlocatie']) &
                (omloop_df['buslijn'] == row['buslijn']) &
                (omloop_df['starttijd'].dt.time == pd.to_datetime(f"{row['vertrektijd']}").time()) &
                (omloop_df['activiteit'] == 'dienst rit')
            ]
        except ValueError as e:
            print(f"Error in row {idx}: {str(e)}")
            continue

        if not omloop_rows.empty:
            dienst_df.at[idx, 'found_in_omloop'] = True

    return omloop_df, dienst_df

# De resultaten terug geven

def Results_check_omloopplanning(df_omloopplanning, df_dienstregeling):

    # Deel 1: Resultaten van omloopplanning controleren
    filtered_df = df_omloopplanning[df_omloopplanning['activiteit'] == 'dienst rit']
    false_count = filtered_df['correct'].value_counts().get(False, 0)
    omloop_txt = "Amount not allowed jobs: " + str(false_count)
    if false_count > 0:
        false_rows = filtered_df[filtered_df['correct'] == False]
        omloop_flase_df =false_rows[['startlocatie', 'eindlocatie', 'starttijd', 'eindtijd', 'buslijn', 'correct']]

    # Deel 2: Resultaten van dienstregeling controleren
    not_found_count = df_dienstregeling['found_in_omloop'].value_counts().get(False, 0)
    dienst_txt = "Amount of missing jobs(according to dienst): " + str(not_found_count)
    if not_found_count > 0:
        not_found_rows = df_dienstregeling[df_dienstregeling['found_in_omloop'] == False]
        dienst_false_df = not_found_rows[['startlocatie', 'eindlocatie', 'vertrektijd', 'buslijn']]


    return omloop_txt, omloop_flase_df, dienst_txt, dienst_false_df

# Functie voor het controleren van de energie niveau's:

def Check_accu(df_omloopplanning,batterijslijtage):

    # Toevoegen gebruikte kW kolom:

    # Nieuwe kolom 'duur' toevoegen die het verschil tussen eindtijd en starttijd aangeeft
    df_omloopplanning['duur'] = df_omloopplanning['eindtijd'] - df_omloopplanning['starttijd']

    # De kolom 'duur' converteren naar minuten
    df_omloopplanning['duur_minuten'] = df_omloopplanning['duur'].dt.total_seconds() / 60

    # De kolom 'duur_minuten' converteren naar uren
    df_omloopplanning['duur_uren'] = df_omloopplanning['duur_minuten'] / 60

    # energieverbruik kolom: de eenheid is kWh --> dus NIET kWh per gereden kilometer

    # Totale gebruikte kilowatturen (kWh) berekenen en opslaan in een nieuwe kolom 'totale_kWh'
    df_omloopplanning['gebruikt_kW'] = df_omloopplanning['duur_uren'] * df_omloopplanning['energieverbruik']

    #

    max_batt_capa = 300 # kW
    SOC_start = 0.9 # factor
    SOC_min = 0.1 # factor
    #batterijslijtage = 0.85 # Afhankelijk van de leeftijd van de bus is dat zo’n 85%-95% van de maximale capaciteit 
    SOH =  max_batt_capa * batterijslijtage # De SOH is de maximale capaciteit van een specifieke bus

    SOC_ochtend = SOH * SOC_start # De SOC geeft aan hoeveel procent de bus nog geladen is. 100% is daarbij gelijk aan de SOH van de bus.
    SOC_minimum = SOH * SOC_min # De veiligheidsmarge van 10% heeft ook betrekking op de SOH

    # DataFrame maken
    data = {
        'Parameter': ['Max Batterij Capaciteit', 'SOC Start', 'SOC Minimum', 'Batterij Slijtage', 'SOH', 'SOC Ochtend', 'SOC Minimum'],
        'Waarde': [max_batt_capa, SOC_start, SOC_min, batterijslijtage, SOH, SOC_ochtend, SOC_minimum],
        'Eenheid': ['kW', 'Factor', 'Factor', 'Factor', 'kW (MBC * BS)', 'kW (SOH * SOC S)', 'kW (SOH * SOC M)']
    }

    df_var_bus = pd.DataFrame(data)

    # Initialiseren van de kolommen voor SOC
    df_omloopplanning['SOC_beginrit'] = 0.0
    df_omloopplanning['SOC_eindrit'] = 0.0

    # Berekenen van SOC_beginrit en SOC_eindrit per rit
    huidige_omloop = None
    huidige_SOC = SOC_ochtend

    for index, row in df_omloopplanning.iterrows():
        if row['omloop nummer'] != huidige_omloop:
            huidige_omloop = row['omloop nummer']
            huidige_SOC = SOC_ochtend
        
        # SOC_beginrit instellen
        df_omloopplanning.at[index, 'SOC_beginrit'] = huidige_SOC
        
        # SOC_eindrit berekenen
        huidige_SOC -= row['gebruikt_kW']
        df_omloopplanning.at[index, 'SOC_eindrit'] = huidige_SOC

        # Controle of nodig is
        if huidige_SOC < SOC_minimum:
            print(f"Waarschuwing: SOC onder de minimum veiligheidsmarge voor omloop nummer {huidige_omloop} bij index {index}.")

    # Toevoegen van nieuwe kolom die aangeeft of SOC_eindrit boven SOC_minimum is
    df_omloopplanning['SOC_above_min'] = df_omloopplanning['SOC_eindrit'] > SOC_minimum

    # Fliteren als de accu onder het minimum komt
    filtered_df = df_omloopplanning[df_omloopplanning['SOC_above_min'] == False]

    # Berekenen van de laagste SOC_eindrit per omloopnummer
    min_SOC_per_omloopnummer = df_omloopplanning.groupby('omloop nummer')['SOC_eindrit'].min().reset_index()
    min_SOC_per_omloopnummer.columns = ['omloop nummer', 'min_SOC_eindrit']

    return df_var_bus, filtered_df, min_SOC_per_omloopnummer, df_omloopplanning


# Functie om oplaad tijd te controleren:

def Check_oplaad_tijd(df_omloopplanning):
    # Filter de rijen waarbij 'activiteit' gelijk is aan 'opladen'
    opladen_df = df_omloopplanning[df_omloopplanning['activiteit'] == 'opladen']
    error = 'Geen error'

    # Controleren of er rijen met 'opladen' zijn gevonden
    if opladen_df.empty:
        error = "Geen rijen gevonden waarbij de 'activiteit' gelijk is aan 'opladen'."
    else:
        # Voeg een nieuwe kolom toe die aangeeft of de 'duur_minuten' groter is dan 15
        opladen_df['lang_genoeg_opgeladen'] = opladen_df['duur_minuten'] > 15
        
        #print("Rijen waarbij de 'activiteit' gelijk is aan 'opladen':")
        # Display de relevante kolommen inclusief de nieuwe kolom
        opladen_df = opladen_df[['activiteit', 'energieverbruik', 'duur_minuten', 'SOC_above_min', 'lang_genoeg_opgeladen']]

        # Filter de rijen waarbij 'lang_genoeg_opgeladen' False is
        niet_lang_genoeg_opgeladen_df = opladen_df[opladen_df['lang_genoeg_opgeladen'] == False]
        
    return error, opladen_df, niet_lang_genoeg_opgeladen_df

# Functie om een gantt chart te maken van de omloopplanning

def Gantt_chart(df):

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

    if os.path.exists("Omloopplanning_Gantt.png"):
        os.remove("Omloopplanning_Gantt.png")

    plt.tight_layout()
    plt.savefig('Omloopplanning_Gantt.png')
    return ax