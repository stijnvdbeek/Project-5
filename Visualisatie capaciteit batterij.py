import pandas as pd
import matplotlib.pyplot as plt

# Laad de Excel-gegevens in
df = pd.read_excel('Omloopplanning met energieniveau.xlsx')

# Converteer de starttijden naar datetime voor correcte tijdreeksen
df['starttijd'] = pd.to_datetime(df['starttijd'])

# Voor elke omloopnummer de SOC_beginrit over tijd plotten
unique_omloopnummers = df['omloop nummer'].unique()

plt.figure(figsize=(10, 6))

# Loop door elke omloopnummer om SOC over tijd te plotten
for omloop in unique_omloopnummers:
    omloop_data = df[df['omloop nummer'] == omloop]
    
    # Plot SOC_beginrit over tijd voor de specifieke omloopnummer
    plt.plot(omloop_data['starttijd'], omloop_data['SOC_beginrit'], label=f'Omloop {omloop}')

# Grafiek instellen
plt.xlabel('Tijd')
plt.ylabel('Batterij capaciteit (SOC)')
plt.title('Batterij capaciteit per omloopnummer over tijd')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()

# Toon de grafiek
plt.show()
