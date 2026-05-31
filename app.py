import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Vols EUA 2024", layout="wide", initial_sidebar_state="expanded")

# Càrrega de les taules que contenen el 100% de les dades de l'any pre-calculades
@st.cache_data
def load_agregated_data():
    global_metrics = pd.read_csv("data_prod/resum_global.csv")
    df_carrier = pd.read_csv("data_prod/carrier_agregat.csv")
    df_dies = pd.read_csv("data_prod/dies_agregat.csv")
    df_mesos = pd.read_csv("data_prod/mesos_agregat.csv")
    df_causes = pd.read_csv("data_prod/causes_agregat.csv")
    df_aeroports = pd.read_csv("data_prod/aeroports_agregat.csv")
    df_dist = pd.read_csv("data_prod/distancia_agregat.csv")
    return global_metrics, df_carrier, df_dies, df_mesos, df_causes, df_aeroports, df_dist

global_metrics, df_carrier, df_dies, df_mesos, df_causes, df_aeroports, df_dist = load_agregated_data()
m_global = global_metrics.iloc[0]

# SIDEBAR INTERACTIVA
st.sidebar.title("Filtres de la Història")
mesos_disponibles = ["Gen", "Feb", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Oct", "Nov", "Des"]
mesos_seleccionats = st.sidebar.multiselect("Selecciona els Mesos:", options=mesos_disponibles, default=mesos_disponibles)

# Filtrar els resums de manera dinàmica segons la selecció de l'usuari
carrier_filtrat = df_carrier[df_carrier['nom_mes'].isin(mesos_seleccionats)]
dies_filtrat = df_dies[df_dies['nom_mes'].isin(mesos_seleccionats)]

# NARRATIVA PRINCIPAL (DATA STORYTELLING)
st.title("Comportament i Eficiència del Sistema Aeri dels EUA (2024)")
st.markdown("Analitzant el **100% dels registres històrics reals** de l'aviació nord-americana durant l'any 2024.")

# KPIs Flash reals totals
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Vols Analitzats", f"{int(m_global['total_vols']):,}")
with col2:
    pct_retard = (m_global['vols_retardats'] / m_global['total_vols']) * 100
    st.metric("% Global de Retard (>15m)", f"{pct_retard:.1f}%")
with col3:
    pct_cancel = (m_global['vols_cancel·lats'] / m_global['total_vols']) * 100
    st.metric("Taxa de Cancel·lació", f"{pct_cancel:.2f}%")
with col4:
    st.metric("Retard Mitjà d'Arribada", f"{m_global['retard_mitja_global']:.1f} min")

st.markdown("---")

# 1. PUNTUALITAT PER AEROLÍNIA
st.header("1. Quines aerolínies són més puntuals?")
carrier_stats = carrier_filtrat.groupby('op_unique_carrier').agg(
    total_vols=('total_vols', 'sum'),
    vols_retardats=('vols_retardats', 'sum'),
    retard_mitja_arribada=('retard_mitja_arribada', 'mean')
).reset_index()
carrier_stats['pct_retard'] = (carrier_stats['vols_retardats'] / carrier_stats['total_vols']) * 100

fig_carrier = px.scatter(carrier_stats, x='pct_retard', y='retard_mitja_arribada', size='total_vols', color='op_unique_carrier',
                         labels={'pct_retard': '% de Vols Retardats', 'retard_mitja_arribada': 'Retard Mitjà (min)'},
                         title="Matriu d'Eficiència de les Aerolínies")
st.plotly_chart(fig_carrier, width='stretch')

# 2. PATRONS TEMPORALS
st.header("2. Com varien els retards segons el calendari?")
col_t1, col_t2 = st.columns(2)
with col_t1:
    ordres_dies = ["Dl", "Dt", "Dc", "Dj", "Dv", "Ds", "Dg"]
    delay_dia = dies_filtrat.groupby('nom_dia')['arr_delay'].mean().reindex(ordres_dies).reset_index()
    st.plotly_chart(px.bar(delay_dia, x='nom_dia', y='arr_delay', labels={'nom_dia': 'Dia', 'arr_delay': 'Retard (min)'}, title="Per Dia de la Setmana"), width='stretch')
with col_t2:
    delay_mes = df_mesos.reset_index()
    st.plotly_chart(px.line(delay_mes, x='nom_mes', y='arr_delay', markers=True, title="Evolució Mensual"), width='stretch')

# 3. CAUSES DELS RETARDS
st.header("3. Quines són les principals causes dels retards?")
causes_dict = {'carrier_delay': 'Problemes Aerolínia', 'weather_delay': 'Meteorologia', 'nas_delay': 'Sistema Nacional (NAS)', 'security_delay': 'Seguretat', 'late_aircraft_delay': 'Arribada Tardana Avió'}
df_causes['Causa'] = df_causes['Causa'].map(causes_dict)
st.plotly_chart(px.pie(df_causes, values='Minuts Totals', names='Causa', title="Distribució de las Causes"), width='stretch')

# 4. DISTÀNCIA I AEROPORTS
st.header("4. Geopolítica del retard i impacte de la distància")
col_g1, col_g2 = st.columns(2)
with col_g1:
    st.plotly_chart(px.scatter(df_dist, x='distance', y='arr_delay', opacity=0.3, title="Distància vs Retard"), width='stretch')
with col_g2:
    st.subheader("Top 10 Aeroports amb més Col·lapses")
    apt_critics = df_aeroports[df_aeroports['vols'] > 50].sort_values(by='retard_mig', ascending=False).head(10)
    
    # FORÇAR EL VERMELL: Afegim color i color_continuous_scale
    fig_apt = px.bar(apt_critics, 
                     x='retard_mig', 
                     y='origin', 
                     orientation='h', 
                     title="Top 10 Aeroports amb més Col·lapses",
                     labels={'retard_mig': 'Retard Mitjà (min)', 'origin': 'Aeroport'},
                     color='retard_mig', 
                     color_continuous_scale='Reds')
    
    fig_apt.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_apt, width='stretch')
