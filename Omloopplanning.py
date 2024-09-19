# Importeren van benodigde libraries
import pandas as pd

# Functie om data in te laden
def load_data():
    # Lees de Excel bestanden in DataFrames
    df_omloopplanning = pd.read_excel('omloopplanning.xlsx', engine='openpyxl')
    df_dienstregeling = pd.read_excel('Connexxion data - 2024-2025.xlsx', engine='openpyxl')
    return df_omloopplanning, df_dienstregeling

