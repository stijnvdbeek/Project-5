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

def Check_accu(path_omloopplanning, batterijslijtage : int, energieverbruik : int):

    # Inladen van data
    df_omloopplanning = pd.read_excel(path_omloopplanning, engine='openpyxl')

    # Converteer tijd kolommen naar datetime objecten voor makkelijke bewerking
    df_omloopplanning['starttijd'] = pd.to_datetime(df_omloopplanning['starttijd datum'])
    df_omloopplanning['eindtijd'] = pd.to_datetime(df_omloopplanning['eindtijd datum'])
    
    # Converteer tijd kolommen naar datetime objecten voor makkelijke bewerking
    df_omloopplanning['starttijd'] = pd.to_datetime(df_omloopplanning['starttijd datum'])
    df_omloopplanning['eindtijd'] = pd.to_datetime(df_omloopplanning['eindtijd datum'])
    
    # Verwijder de specifieke kolommen
    df_omloopplanningv2 = df_omloopplanning.copy()
    df_omloopplanningv2.drop(columns=['starttijd datum', 'eindtijd datum'], inplace=True)

    # Zet de kolom 'starttijd' om naar datetime-formaat
    df_omloopplanningv2['starttijd'] = pd.to_datetime(df_omloopplanningv2['starttijd'])
    df_omloop = df_omloopplanningv2.copy()

    # Voeg de kolommen samen en maak de nieuwe kolom 'code'
    df_omloop['code_omloop'] = df_omloop['startlocatie'].astype(str) + '_' + \
                                df_omloop['eindlocatie'].astype(str) + '_' + \
                                df_omloop['buslijn'].astype(str)
    
    # Afstands matrix inladen
    df_afstandsmatrix = pd.read_excel('Connexxion data - 2024-2025.xlsx', engine='openpyxl', sheet_name='Afstandsmatrix')

    # Voeg de kolommen samen en maak de nieuwe kolom 'code'
    df_afstandsmatrix['code_afstand'] = df_afstandsmatrix['startlocatie'].astype(str) + '_' + \
                                df_afstandsmatrix['eindlocatie'].astype(str) + '_' + \
                                df_afstandsmatrix['buslijn'].astype(str)

    # Merge df_omloop with the relevant columns from df_afstandsmatrix
    df_omloop_merged = pd.merge(
        df_omloop,
        df_afstandsmatrix[['code_afstand', 'afstand in meters']],
        left_on='code_omloop',
        right_on='code_afstand',
        how='left'
    )

    # Remove the 'code_afstand' column if it's not needed
    df_omloop_merged.drop(columns=['code_afstand'], inplace=True)

    # Create a new column 'afstand in km' by converting 'afstand in meters' to kilometers
    df_omloop_merged['afstand in km'] = df_omloop_merged['afstand in meters'] / 1000

    energie_verbruik_per_km = energieverbruik #kWh per gereden kilometer
    oplaadkracht_per_uur = 450 # kWh per uur tot 90%
    oplaadkracht_per_uur_laatste = 60 # wordt niet gebruikt
    max_batt_capa = 300 # kWh
    SOC_start = 0.9 # factor
    SOC_min = 0.1 # factor
    batterijslijtage = batterijslijtage  # Afhankelijk van de leeftijd van de bus is dat zo’n 85%-95% van de maximale capaciteit 
    SOH =  max_batt_capa * batterijslijtage # De SOH is de maximale capaciteit van een specifieke bus


    SOC_ochtend = SOH * SOC_start # De SOC geeft aan hoeveel procent de bus nog geladen is. 100% is daarbij gelijk aan de SOH van de bus.
    SOC_minimum = SOH * SOC_min # De veiligheidsmarge van 10% heeft ook betrekking op de SOH

    # DataFrame maken
    data = {
        'Parameter': ['Max Batterij Capaciteit', 'SOC Start', 'SOC Minimum', 'Batterij Slijtage', 'SOH', 'SOC Ochtend', 'SOC Minimum','Batterijverbuik','Oplaadsnelheid'],
        'Waarde': [max_batt_capa, SOC_start, SOC_min, batterijslijtage, SOH, SOC_ochtend, SOC_minimum, energie_verbruik_per_km,oplaadkracht_per_uur],
        'Eenheid': ['kWh', 'Factor', 'Factor', 'Factor', 'kW (MBC * BS)', 'kW (SOH * SOC S)', 'kW (SOH * SOC M)','kWh/km','kWh/uur']
    }

    df = pd.DataFrame(data)

    # Verkrijg alle unieke waarden van 'code_afstand'
    unieke_omloop = df_omloop_merged['omloop nummer'].unique()

    # Maak een lege dictionary om de DataFrames op te slaan
    df_dict_omloop = {}
    totaal = 0
    # Loop door elke unieke code en filter df_omloop
    for omloop in unieke_omloop:
        # Filter df_omloop
        gefilterde_df = df_omloop_merged[df_omloop_merged['omloop nummer'] == omloop]
        
        # Voeg het gefilterde DataFrame toe aan de dictionary
        df_dict_omloop[omloop] = gefilterde_df
        
        # Optioneel: Print de eerste paar rijen van elk gefilterd DataFrame
        # print(f"Code: {omloop}")
        # display(gefilterde_df.head())
        # print(len(gefilterde_df))
        totaal += len(gefilterde_df)

    resultaten = {}

    for key, df in df_dict_omloop.items():
        omloop_energie = df[['starttijd', 'eindtijd', 'activiteit', 'omloop nummer', 'code_omloop', 'afstand in km']].copy()
        omloop_energie['afstand in km'] = omloop_energie['afstand in km'].fillna(0)

        # Reset the index to use integer indexing
        omloop_energie.reset_index(drop=True, inplace=True)
        
        omloop_energie.sort_values(by=['starttijd', 'eindtijd'], inplace=True)

        # Initialize 'SOC_beginrit' for the first row
        omloop_energie.at[0, 'SOC_beginrit'] = SOC_ochtend
        
        for i in range(len(omloop_energie)):
            SOC_start = omloop_energie.at[i, 'SOC_beginrit']
            
            if omloop_energie.at[i, 'activiteit'] == 'opladen':
                starttijd = pd.to_datetime(omloop_energie.at[i, 'starttijd'])
                eindtijd = pd.to_datetime(omloop_energie.at[i, 'eindtijd'])
                duur_in_uren = (eindtijd - starttijd).total_seconds() / 3600
                
                opgeladen_energie = oplaadkracht_per_uur * duur_in_uren
                SOC_eind = SOC_start + opgeladen_energie
            else:
                afstand = omloop_energie.at[i, 'afstand in km']
                verbruik = energie_verbruik_per_km * afstand if pd.notna(afstand) else 0
                SOC_eind = SOC_start - verbruik
            
            # Save the calculated SOC, even if it is negative
            omloop_energie.at[i, 'SOC_eindrit'] = SOC_eind
            
            if i + 1 < len(omloop_energie):
                omloop_energie.at[i + 1, 'SOC_beginrit'] = SOC_eind
        
        resultaten[key] = omloop_energie

    omloopnummers_onder_nul = []

    for key, result in resultaten.items():
        if any(result['SOC_eindrit'] < SOC_minimum):
            omloopnummers_onder_nul.append(key)


    return resultaten, omloopnummers_onder_nul















# Functie om oplaad tijd te controleren:

def Check_oplaad_tijd(df_omloopplanning):

    # Nieuwe kolom 'duur' toevoegen die de verschil tussen eindtijd en starttijd aangeeft
    df_omloopplanning['duur'] = df_omloopplanning['eindtijd'] - df_omloopplanning['starttijd']

    # Als je de duur in minuten wilt omzetten
    df_omloopplanning['duur_minuten'] = df_omloopplanning['duur'].dt.total_seconds() / 60

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
        opladen_df = opladen_df[['activiteit', 'energieverbruik', 'duur_minuten', 'lang_genoeg_opgeladen']]

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


def plot_energie(resultaten):
    # Initialiseer een plot
    plt.figure(figsize=(12, 7))

    # Zet de formatter voor tijdweergave op de x-as
    time_formatter = mdates.DateFormatter('%m-%d %H:%M')

    # Maak een colormap aan voor visuele differentiatie
    colors = plt.cm.viridis(np.linspace(0, 1, len(resultaten)))

    # Itereer over de resultaten en plot ze
    for (key, result), color in zip(resultaten.items(), colors):
        # Zorg ervoor dat 'eindtijd' een datetime object is
        result['eindtijd'] = pd.to_datetime(result['eindtijd'])
        
        # Datum en tijd voor verschillen over middernacht
        x_values = result['eindtijd']
        y_values = result['SOC_eindrit']
        
        plt.plot(x_values, y_values, marker='o', linestyle='-', label=f"Sleutel {key}", color=color)

    # Voeg een horizontale lijn toe bij y = 0
    plt.axhline(y=0, color='red', linestyle='-', linewidth=2)
    # Voeg een horizontale lijn toe bij y = 0
    #plt.axhline(y=SOC_minimum, color='orange', linestyle='-', linewidth=2)

    # Pas de x-as formattering aan
    plt.gca().xaxis.set_major_formatter(time_formatter)
    plt.xticks(rotation=45)

    # Labels en legenda toevoegen
    plt.title("SOC_eindrit over eindtijd")
    plt.xlabel('Eindtijd (maand-dag uur:minuut)')
    plt.ylabel('SOC eindrit')
    plt.legend(title='Sleutels')
    plt.grid(True)
    plt.tight_layout()

    # Toon het plot
    plt.savefig('plteng.png')
