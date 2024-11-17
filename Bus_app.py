# python -m streamlit run .\0_??_Startpagina.py

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
import pandas as pd
import numpy as np
import streamlit as st
from datetime import time

# Streamlit paginas maken

st.set_page_config(
    page_title="Bus_app",
    page_icon= "🏠"
    )

st.title("Bus app ")
st.write("Welcome to the Bus app. This app is designed to check the Circulation Plan and TimeTable of a bus company. The app checks the battery level, the correctness of the Circulation Plan and TimeTable, the charging time and the minimum and maximum values. The app also provides visualizations of the Circulation Plan and the energy consumption of the buses. ")
st.subheader("Evaluation:")
with st.sidebar:
    path_omloopplanning = st.file_uploader('Upload Circulation Plan: ', type='xlsx', accept_multiple_files= False)

    Path_dienstregeling = st.file_uploader('Upload TimeTable: ', type= 'xlsx', accept_multiple_files= False)

    batterijslijtage = st.slider("Choose state of health value (for all busses):", 85,95,90,1)

    energieverbruik = st.slider("Choose energy use in KWH (average KWH = 1.2)", 0.7,2.5,1.2,0.1)

st.sidebar.success('Change settings')





with st.spinner("Calculation..."):
    if path_omloopplanning is not None and Path_dienstregeling is not None:

        # Data voorbereiden 

        # Functie om data in te laden
        def load_data():
            # Lees de Excel bestanden in DataFrames
            df_omloopplanning = pd.read_excel(path_omloopplanning, engine='openpyxl')
            df_dienstregeling = pd.read_excel(Path_dienstregeling, engine='openpyxl')
            return df_omloopplanning, df_dienstregeling

        # 1.CONTROLE BATTERIJNIVEAU:
        # Inladen van data
        df_omloopplanning, df_dienstregeling = load_data()

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

        # Connexxion afstandsmatrix inladen
        df_afstandsmatrix = pd.read_excel(Path_dienstregeling, engine='openpyxl', sheet_name='Afstandsmatrix')

        # Voeg de kolommen samen en maak de nieuwe kolom 'code'
        df_afstandsmatrix['code_afstand'] = df_afstandsmatrix['startlocatie'].astype(str) + '_' + \
                                    df_afstandsmatrix['eindlocatie'].astype(str) + '_' + \
                                    df_afstandsmatrix['buslijn'].astype(str)

        # Afstand linken
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

        # Variabel voor batterij
        energie_verbruik_per_km = energieverbruik #kWh per gereden kilometer
        oplaadkracht_per_uur = 450 # kWh per uur tot 90%
        oplaadkracht_per_uur_laatste = 60 # wordt niet gebruikt
        max_batt_capa = 300 # kWh
        SOC_start = 0.9 # factor
        SOC_min = 0.1 # factor
        batterijslijtage = batterijslijtage/100 # Afhankelijk van de leeftijd van de bus is dat zo’n 85%-95% van de maximale capaciteit 
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

        # Energieverbruik dict maken
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
            
        # df_dict bevat nu een DataFrame voor elke unieke 'code_afstand'

        # SOC einde van de rit bepalen

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
                    if SOC_eind > 300* SOH *0.9:
                        SOC_eind = 300* SOH *0.9
                    else:
                        SOC_eind = SOC_eind
                else:
                    afstand = omloop_energie.at[i, 'afstand in km']
                    verbruik = energie_verbruik_per_km * afstand if pd.notna(afstand) else 0
                    SOC_eind = SOC_start - verbruik
                    
                
                # Save the calculated SOC, even if it is negative
                omloop_energie.at[i, 'SOC_eindrit'] = SOC_eind
                
                if i + 1 < len(omloop_energie):
                    omloop_energie.at[i + 1, 'SOC_beginrit'] = SOC_eind
            
            resultaten[key] = omloop_energie

        # SOC controleren 
        omloopnummers_onder_nul = []

        for key, result in resultaten.items():
            if any(result['SOC_eindrit'] < SOC_minimum):
                omloopnummers_onder_nul.append(int(key))

        # Bericht maken voor batterijniveau
        if len(omloopnummers_onder_nul) == 0:
            
            st.write("- No Circulation Plan with SOC (State Of Charge) under", round(SOC_minimum,2), "kWh (10""%"" of maximum SOC): ✅")
        else:
            st.write("- Circulation Plan with SOC (State Of Charge) under", round(SOC_minimum,2), "kWh (10""%"" of maximum SOC):", " ⛔")
            st.write(" - ".join(map(str,omloopnummers_onder_nul)))
            st.markdown("""
                <p style='font-size:12px; font-style:italic;'>
                    Circulations with their minimun below the threshold may idicate a risk with the battery capacity.
                </p>
            """, unsafe_allow_html=True)

        # 2. CONTROLE OMLOOPPLANNING vs DIENSTREGELING:

        # Functie om de correctheid van de omloopplanning te controleren
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
                    if pd.notna(dienst_row['vertrektijd']):  # Zorg dat vertrektijd niet NaN is
                        # Maak een vertrektijd datetime object
                        vertrektijd = pd.to_datetime(f"{row['starttijd'].date()} {dienst_row['vertrektijd']}", errors='coerce')
                        if pd.notna(vertrektijd):
                            # Controleer of de starttijd overeenkomt met de dienstregeling
                            if vertrektijd == row['starttijd']:
                                omloop_df.at[idx, 'correct'] = True
                                break
            # Controleer of alle ritten in de dienstregeling aanwezig zijn in de omloopplanning
            dienst_df['found_in_omloop'] = False

            for idx, row in dienst_df.iterrows():
                if pd.notna(row['vertrektijd']):
                    dt_time = pd.to_datetime(row['vertrektijd'], format='%H:%M', errors='coerce')
                    if pd.notna(dt_time):
                        omloop_rows = omloop_df[
                            (omloop_df['startlocatie'] == row['startlocatie']) &
                            (omloop_df['eindlocatie'] == row['eindlocatie']) &
                            (omloop_df['buslijn'] == row['buslijn']) &
                            (omloop_df['starttijd'].dt.time == dt_time.time()) &
                            (omloop_df['activiteit'] == 'dienst rit')
                        ]

                        if not omloop_rows.empty:
                            dienst_df.at[idx, 'found_in_omloop'] = True

            return omloop_df, dienst_df

        # Controles uitvoeren
        # Inladen van data
        df_omloopplanning, df_dienstregeling = load_data()

        # Converteer tijd kolommen naar datetime objecten voor makkelijke bewerking
        df_omloopplanning['starttijd'] = pd.to_datetime(df_omloopplanning['starttijd datum'])
        df_omloopplanning['eindtijd'] = pd.to_datetime(df_omloopplanning['eindtijd datum'])

        # Voer de controle uit
        df_omloopplanning, df_dienstregeling = check_omloopplanning(df_omloopplanning, df_dienstregeling)

        # Deel 1: Resultaten van omloopplanning controleren
        filtered_df = df_omloopplanning[df_omloopplanning['activiteit'] == 'dienst rit']
        false_count = filtered_df[filtered_df['correct'] == False].shape[0]

        st.write("")
        if false_count > 0:
            df_messages_omloopplanning = filtered_df[filtered_df['correct'] == False]
            messages_omloopplanning = "Routes found in Circulation plan that are not in the TimeTable:",false_count, "⛔" # Er is een dienstrit die niet overeenkomt met de dienstregeling
            
            st.write("- Routes found in Circulation plan that are not in the TimeTable:",false_count, "⛔")
            st.dataframe(df_messages_omloopplanning)
            st.markdown("""
                <p style='font-size:12px; font-style:italic;'>
                    These routes indicate unnecessarily planned Circulations.
                </p>
            """, unsafe_allow_html=True)
        else:
            st.write("- No Routes found in Circulation plan that are not in the TimeTable: ✅")

        # Deel 2: Resultaten van dienstregeling controleren
        not_found_count = df_dienstregeling[df_dienstregeling['found_in_omloop'] == False].shape[0]
        st.write("")
        if not_found_count > 0:
            df_messages_dienstregeling = df_dienstregeling[df_dienstregeling['found_in_omloop'] == False]

            st.write("- Routes found in TimeTable that are not in the Circulation Plan:", not_found_count, "⛔")
            st.write(df_messages_dienstregeling)
            st.markdown("""
                <p style='font-size:12px; font-style:italic;'>
                    These routes indicate that they have not yet been assigned to a Circulation.
                </p>
            """, unsafe_allow_html=True)

        else:

            st.write("- No routes found in TimeTable that are not in the Cirvulation Plan: ✅")


        # 3. OPLAADTIJD CONTROLEREN:

        # Eerst ervoor zorgen dat de kolommen 'starttijd' en 'eindtijd' in datetime geformatteerd zijn
        df_omloopplanning['starttijd'] = pd.to_datetime(df_omloopplanning['starttijd'])
        df_omloopplanning['eindtijd'] = pd.to_datetime(df_omloopplanning['eindtijd'])

        # Nieuwe kolom 'duur' toevoegen die de verschil tussen eindtijd en starttijd aangeeft
        df_omloopplanning['duur'] = df_omloopplanning['eindtijd'] - df_omloopplanning['starttijd']

        # Als je de duur in minuten wilt omzetten
        df_omloopplanning['duur_minuten'] = df_omloopplanning['duur'].dt.total_seconds() / 60

        # Haal de unieke waarden uit de kolom 'activiteit'
        unieke_waarden_activiteit = df_omloopplanning['activiteit'].unique()

        # Filter de rijen waarbij 'activiteit' gelijk is aan 'opladen'
        opladen_df = df_omloopplanning[df_omloopplanning['activiteit'] == 'opladen']

        # Bereken de totale oplaadtijd
        tekort_oplaadtijd = opladen_df[opladen_df['duur_minuten'] < 15]
        df_messages_oplaadtijd = pd.DataFrame()

        st.write("")
        if tekort_oplaadtijd.shape[0] > 0:
            df_messages_oplaadtijd = tekort_oplaadtijd['starttijd', 'eindtijd','omloop nummer' ,'duur_minuten']
            messages_oplaadtijd = "Charging time is less than 15 minutes:", tekort_oplaadtijd.shape[0], "⛔"

            st.write("- Charging time is less than the minimum of 15 minutes:", tekort_oplaadtijd.shape[0], "⛔")
            st.dataframe(df_messages_oplaadtijd)
        else:

            st.write("- Charging time is more than the minimum of 15 minutes: ✅")


        # 4. CONTROLE Min/Max:
        # Samenvoegen van de DataFrames op basis van startlocatie, eindlocatie en buslijn
        merged_df = df_omloopplanning.merge(df_afstandsmatrix, on=['startlocatie', 'eindlocatie', 'buslijn'], how='left')

        # Voorwaarden controleren of de duur buiten de minimale en maximale reistijd valt
        condition_out_of_bounds = (merged_df['duur_minuten'] < merged_df['min reistijd in min']) | (merged_df['duur_minuten'] > merged_df['max reistijd in min'])

        # Nieuwe DataFrame met rijen waar de voorwaarde True is
        df_out_of_bounds = merged_df[condition_out_of_bounds]
        # Unieke 'code_afstand' waarden in df_out_of_bounds
        unieke_codes_domein = df_out_of_bounds['code_afstand'].unique()

        # Voorwaarden controleren of de duur onder de minimale reistijd ligt
        condition_below_min = merged_df['duur_minuten'] < merged_df['min reistijd in min']

        # Nieuwe DataFrame met rijen waar de voorwaarde True is
        df_below_min = merged_df[condition_below_min]

        # Unieke 'code_afstand' waarden in df_below_min
        unieke_codes_min = df_below_min['code_afstand'].unique()

        st.write("")
        if len(df_out_of_bounds) > 0:
            st.write("- Number of routes that according to the data outside are outside the minimum or maximum travel time: ", len(df_out_of_bounds)," ⛔")
            st.write("Number of routes below the minimum travel time:", len(df_below_min))
            st.write("Number of routes above the maximum travel time:", len(df_out_of_bounds)-len(df_below_min))
            st.write("Routes that are outside the minimum or maximum travel time:")
            st.dataframe(df_out_of_bounds)
            
        else:
            st.write("- There are no routes that according to the data outside the minimum or maximum travel time: ✅")





        # 5. VISUALISATIES:
        
        st.subheader("Visualisations:")

        # Plot voor Gantt chart
        df = pd.read_excel(path_omloopplanning, engine='openpyxl')
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
        ax.set_xlabel('Time')
        ax.set_ylabel('Circulation number')
        ax.set_title('Circulation plan Gantt Chart')
        
        st.write("- This Gantt chart illustrates the bus circulation plan by displaying different activities over time for each circulation number. Colors indicate specific activities: black for material rides, yellow for service trip 401, blue for idle times, green for service trip 400, and orange for charging. The x-axis represents the time of day, while the y-axis lists the circulation numbers, helping to track and optimize bus operations efficiently.")
        st.pyplot(fig)


        st.write("")
        # Plot voor energie verbruik
        # Initialiseer een plot
        fig, ax = plt.subplots(figsize=(12, 7))

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
            
            ax.plot(x_values, y_values, marker='o', linestyle='-', label=f"Circualation nr. {key}", color=color)

        # Voeg een horizontale lijn toe bij y = 0
        ax.axhline(y=0, color='red', linestyle='-', linewidth=2)
        # Voeg een horizontale lijn toe bij y = 0
        ax.axhline(y=SOC_minimum, color='orange', linestyle='-', linewidth=2)

        # Pas de x-as formattering aan
        ax.xaxis.set_major_formatter(time_formatter)
        plt.xticks(rotation=45)

        # Labels en legenda toevoegen
        ax.set_title("SOC for each Circulation Plan")
        ax.set_xlabel('End time route (month-day hour:minute)')
        ax.set_ylabel('SOC at the end of the route')
        ax.legend(title='Circualation nummer')
        ax.grid(True)
        plt.tight_layout()

        st.write("- This line plot shows the State of Charge (SOC) for each Circulation Plan at the end of the route. The x-axis represents the end time of the route, while the y-axis shows the SOC. The red line indicates the minimum SOC threshold, while the orange line represents the safety margin. The plot helps to monitor the battery capacity and ensure that the buses are charged adequately for the next route.")
        st.pyplot(fig)


