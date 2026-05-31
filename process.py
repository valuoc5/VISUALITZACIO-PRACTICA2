import pandas as pd
import os

# Carregar el dataset real de 1,24 GB sencer
ruta_gran = "data/flight_data_2024.csv"

if not os.path.exists(ruta_gran):
    print(f" Error: No s'ha trobat el fitxer gran a {ruta_gran}. Assegura't de descarregar-lo de Kaggle.")
else:
    df = pd.read_csv(ruta_gran)
    print(f"Dataset carregat correctament. Registres totals: {len(df):,}")

    # 1. ENRIQUIMENT DE DADES
    df['es_retardat'] = df['arr_delay'] > 15
    dies_dict = {1: "Dl", 2: "Dt", 3: "Dc", 4: "Dj", 5: "Dv", 6: "Ds", 7: "Dg"}
    df['nom_dia'] = df['day_of_week'].map(dies_dict)
    mesos_dict = {1:"Gen", 2:"Feb", 3:"Mar", 4:"Abr", 5:"Mai", 6:"Jun", 7:"Jul", 8:"Ago", 9:"Set", 10:"Oct", 11:"Nov", 12:"Des"}
    df['nom_mes'] = df['month'].map(mesos_dict)

    print("Calculant les mètriques reals globals de l'any 2024...")

    # Mètrica 1: Resum global anual
    resum_global = pd.DataFrame([{
        'total_vols': len(df),
        'vols_retardats': int(df['es_retardat'].sum()),
        'vols_cancel·lats': int(df['cancelled'].sum()),
        'retard_mitja_global': float(df['arr_delay'].mean())
    }])

    # Mètrica 2: Agregació per Aerolínies
    df_carrier = df.groupby(['nom_mes', 'op_unique_carrier']).agg(
        total_vols=('fl_date', 'count'),
        vols_retardats=('es_retardat', 'sum'),
        retard_mitja_arribada=('arr_delay', 'mean')
    ).reset_index()

    # Mètrica 3: Patrons Temporals
    df_dies = df.groupby(['nom_mes', 'nom_dia'])['arr_delay'].mean().reset_index()
    df_mesos = df.groupby('nom_mes')['arr_delay'].mean().reset_index()

    # Mètrica 4: Causes del retard global (Bloc 3)
    causes = ['carrier_delay', 'weather_delay', 'nas_delay', 'security_delay', 'late_aircraft_delay']
    df_causes = df[causes].sum().reset_index()
    df_causes.columns = ['Causa', 'Minuts Totals']

    # Mètrica 5: Aeroports crítics i Mostra de Distància (Bloc 4)
    df_aeroports = df.groupby('origin').agg(
        retard_mig=('arr_delay', 'mean'), 
        vols=('fl_date', 'count')
    ).reset_index()

    # Per al gràfic de dispersió de distàncies necessitem punts dispersos. 
    # Extraiem una mostra reduïda optimitzada només per pintar el gràfic, sense perdre les proporcions.
    df_dist_sample = df.dropna(subset=['distance', 'arr_delay']).sample(n=min(10000, len(df)), random_state=42)

    print("Guardant els fitxers d'agregació analítica per a producció...")
    resum_global.to_csv("data/resum_global.csv", index=False)
    df_carrier.to_csv("data/carrier_agregat.csv", index=False)
    df_dies.to_csv("data/dies_agregat.csv", index=False)
    df_mesos.to_csv("data/mesos_agregat.csv", index=False)
    df_causes.to_csv("data/causes_agregat.csv", index=False)
    df_aeroports.to_csv("data/aeroports_agregat.csv", index=False)
    df_dist_sample[['distance', 'arr_delay']].to_csv("data/distancia_agregat.csv", index=False)

    print("Procés analític finalitzat. Zero dades perdudes i fitxers optimitzats creats!")
