# AVVIA IL TERMINALE CON LA COMBINAZIONE TASTI Ctrl + ò e digita la seguente istruzione:
#           streamlit run Dashboard.py

########################################################################################################################################################################################              
# IMPORTAZIONE LIBRERIE PYTHON
import streamlit as st
from streamlit_folium import folium_static
from streamlit_extras.metric_cards import style_metric_cards
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#import plost                             
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime, date
from itertools import product
#import calendar
import altair as alt
from taipy.gui import Gui 
import taipy.gui.builder as tgb
from math import cos, exp
from datetime import datetime
import folium
from folium.plugins import MarkerCluster, HeatMap, Fullscreen, Draw
from folium import plugins
from folium.plugins import MarkerCluster


####################################################################################################################################################################################################################################################################################################################################################################################################################
# CONFIGURAZIONE PAGINA
st.set_page_config(
    page_title="Dashboard Home",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

alt.themes.enable("dark")

# IMPORTAZIONE DEL DATABASE PRATICHE - METODO DRAG & DROP 
upload_file = st.file_uploader('Carica il DB Pratiche Edilizie', type=['xlsx'])
# Se il DB Excel è stato caricato:
if upload_file is not None:
    pratiche_database = pd.read_excel(upload_file)
else:
    st.error("Attenzione: per procedere correttamente è necessario caricare il DB Pratiche Edilzie!")
    st.stop()


####################################################################################################################################################################################################################################################################################################################################################################################################################
# IMPORTAZIONE DEL DATABASE PRATICHE - METODO STATICO PREDEFINITO
#pratiche_database = pd.read_excel('data/DB_Pratiche_Edilizie.xlsx')


# INSERIMENTO LOGO UFFICIO
st.sidebar.image('images/logo_studio.png')

st.sidebar.divider()  # 👈 Draws a horizontal rule


####################################################################################################################################################################################################################################################################################################################################################################################################################
# COSTRUZIONE SIDEBAR ####################################     
st.sidebar.title('🔎 Filtri Dashboard')


# FILTRO NOMI TECNICI ####################################
tecnici = st.sidebar.multiselect(
    'Selezionare il tecnico o i tecnici:',
    options = sorted(pratiche_database["Tecnico_Compilatore"].unique()),
    default = sorted(pratiche_database["Tecnico_Compilatore"].unique())
)



# FILTRO MESI UNIVOCI IN TUTTO IL DATABASE ####################################
def nome_mese(numero_mese):
    return datetime.strptime(str(numero_mese), "%m").strftime("%B")

date_cols = ["Data_Incarico_Pratica", "Data_Archiviazione", "Data_Presentaz._P.E.", "Data_Integraz._P.E."]
combined_dates = pd.concat([pratiche_database[col] for col in date_cols])
mesi = pd.to_datetime(combined_dates).dt.month.unique()
nomi_mesi = [nome_mese(int(mese)) for mese in mesi]
mese_numero_dict = dict(zip(nomi_mesi, mesi))
nomi_mesi_ordinati = sorted(nomi_mesi, key=lambda mese: datetime.strptime(mese, '%B').month)

mesi_selezionati_nomi = st.sidebar.multiselect("Selezionare il mese o i mesi:", nomi_mesi_ordinati, default=nomi_mesi_ordinati)
mesi_selezionati_numeri = [mese_numero_dict[mes] for mes in mesi_selezionati_nomi]



# FILTRO ANNI UNIVOCI IN TUTTO IL DATABASE ####################################
combined_dates1 = pd.concat([pratiche_database[col] for col in date_cols])
anni = pd.to_datetime(combined_dates1).dt.year.unique()
anni_ordinati = sorted([anno for anno in anni if anno != 1900])

anni_selezionati = st.sidebar.multiselect("Selezionare l'anno o gli anni:", anni_ordinati, default=anni_ordinati)



# I FILTRI DELLA DASHBORD VENGONO APPLICATI A TABELLA E GRAFICI ####################################
# Assicurati che tutti i filtri siano selezionati
if not tecnici or not mesi_selezionati_numeri or not anni_selezionati:
    st.error("Attenzione: è necessario selezionare almeno un valore per ciascun filtro!")
    st.stop()
else:
    # Pre-filtra per tecnico per ridurre la dimensione del dataframe
    filtered_df = pratiche_database[pratiche_database["Tecnico_Compilatore"].isin(tecnici)]
    # Applica i filtri di data utilizzando una funzione che verifica se la data rientra nei mesi e anni selezionati
    def filter_by_date(row):
        return any(row[col].month in mesi_selezionati_numeri and row[col].year in anni_selezionati for col in date_cols if pd.notna(row[col]))
    # Applica il filtro di data
    selection_query = filtered_df[filtered_df[date_cols].apply(filter_by_date, axis=1)]

    
######################################################################################################################################################################################################################################################################################################################################################################
# Titolo della dashboard
st.write("# 🖥️ Dashboard Studio Tecnico")


######################################################################################################################################################################################################################################################################################################################################################################
# Etichette con funzione di multipage
tab1, tab2, tab3 = st.tabs(["🏠 HOME", "📊 ANALISI 1", "🗺️ MAPPA"])


############################################ TAB HOME ############################################################################################################################################################################################################################
with tab1:
    st.markdown(' ')
    st.markdown(' ')
    st.markdown('#### _Database Pratiche Edilizie_')
    # Inserire gli eventuali indici delle colonne da nascondere nelle parentesi quadre
    indici_colonne_da_nascondere = [3,4,5] # inserire indice posizione numerica colonne da nascondere
    # Ordinamento della tabella in ordine crescente per il campo "Codice_Pratica"
    selection_query = selection_query.sort_values(by='Codice_Pratica', ascending=True)
    # Visualizzazione della tabella del database pratiche con colonne nascoste e ordinata
    st.dataframe(selection_query.drop(selection_query.columns[indici_colonne_da_nascondere], axis=1), height=353)

    st.markdown(' ')
    st.markdown(' ')

    tot_PE_da_lavorare = (selection_query['Stato_Pratica'] == 'Da lavorare').sum()
    tot_PE_primo_invio_lavoro = (selection_query['Stato_Pratica'] == 'Primo invio - in lavorazione').sum()
    tot_PE_primo_inviate = (selection_query['Stato_Pratica'] == 'Presentata per primo invio').sum()
    tot_PE_integr_lavoro = (selection_query['Stato_Pratica'] == 'Integrazione - in lavorazione').sum()
    tot_PE_integr_inviate = (selection_query['Stato_Pratica'] == 'Integrata').sum()
    tot_PE_concluse = (selection_query['Stato_Pratica'] == 'Conclusa').sum()
    tot_ore_lavorate=(selection_query['Tot_Ore_Lavorate'].sum())

    column1, column2, column3 = st.columns(3, gap="large")
    column4, column5, column6 = st.columns(3, gap="large")

    columns = [column1, column2, column3, column4, column5, column6]
    headers = [
        '✅ Da lavorare:', '✅ In lavorazione per I° invio:', '✅ Inviate per I° invio:',
        '✅ In lavorazione per integrazione:', '✅ Integrate:', '✅ Concluse:'
    ]
    counts = [
        tot_PE_da_lavorare, tot_PE_primo_invio_lavoro, tot_PE_primo_inviate,
        tot_PE_integr_lavoro, tot_PE_integr_inviate, tot_PE_concluse
    ]

    for col, header, count in zip(columns, headers, counts):
        with col:
            tile = col.container(height=115, border=True)
            # Utilizzo di tag HTML per centrare il testo
            tile.markdown(f'<h5 style="text-align: left;">{header}</h5>', unsafe_allow_html=True)
            tile.markdown(f'<h3 style="text-align: center;">{count}</h3>', unsafe_allow_html=True)




############################################ TAB ANALISI 1 con relativi grafici ############################################################################################################################################################################################################################ 
with tab2:
    st.markdown(' ')
    st.markdown(' ')
    # PRIMA riga di grafici suddivisi in 2 colonne totali
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('#### _Grafico 1:_')
        st.write("_Totale pratiche edilizie per tipologia_")
        # Usa i dati filtrati
        pratiche_grouped = selection_query.groupby('Tipologia_P.E.')['Codice_Pratica'].count()
        pratiche_grouped = pratiche_grouped.sort_index(key=lambda x: x.str.lower())  # Ordina alfabeticamente per Tipologia_P.E.
        # Creazione del grafico con Plotly
        grafico_1 = px.bar(pratiche_grouped, x=pratiche_grouped.index, y='Codice_Pratica', labels={'x': 'Tipologia P.E.', 'y': 'Q.tà P.E.'}, text='Codice_Pratica', color_discrete_sequence=['#45e900'])
        # Aggiunta delle etichette sulle barre
        grafico_1.update_traces(textposition='inside', textfont_size=12)
        # Imposta le etichette e la legenda
        grafico_1.update_layout(xaxis_title='', yaxis_title='Q.tà P.E.', title='', xaxis_tickangle=-45, height=500, width=650)
        # Visualizzazione del grafico
        st.plotly_chart(grafico_1)

    with col2:
        st.markdown('#### _Grafico 2:_')
        st.write("_Totale tipologia pratiche edilizie per tecnico_")
        # Raggruppa i dati per 'Tipologia_P.E.'
        pratiche_grouped = selection_query.groupby(['Tipologia_P.E.', 'Tecnico_Compilatore']).size().unstack(fill_value=0)
        pratiche_grouped = pratiche_grouped.sort_index(key=lambda x: x.str.lower())  # Ordina alfabeticamente per Tipologia_P.E.
        # Converti l'indice e le colonne in stringhe per Plotly Express
        pratiche_grouped.index = pratiche_grouped.index.astype(str)
        pratiche_grouped.columns = pratiche_grouped.columns.astype(str)
		# Definisci una lista di colori esadecimali per i tecnici
        colori_tecnici = ['#fde910', '#00a6e9', '#d21759']  # Aggiungi altri colori se necessario
        # Creazione del grafico a barre con Plotly Express
        grafico_2 = px.bar(pratiche_grouped, barmode='stack', template='plotly_dark', color_discrete_map={col: colore for col, colore in zip(pratiche_grouped.columns, colori_tecnici)})
        # Aggiungi le etichette alle barre
        for data in grafico_2.data:
            data.text = [f'{y:g}' if y != 0 else '' for y in data.y]
        # Imposta i titoli e la legenda
        grafico_2.update_layout(xaxis_tickangle=-45, yaxis=dict(title='Q.tà P.E.'), legend=dict(title='Tecnico:'), title='', xaxis_title='', height=500, width=650)
        grafico_2.update_traces(textposition='inside', textfont_size=12)
        # Visualizzazione del grafico
        st.plotly_chart(grafico_2)


    st.divider()  # 👈 Draws a horizontal rule


    # SECONDA riga di grafici suddivisi in 2 colonne totali
    col3, col4 = st.columns(2, gap="large")

    with col3:
        st.markdown('#### _Grafico 3:_')
        st.write("_Funnel stato lavorazione pratiche edilizie per tecnico_")
        # Definisci l'ordine desiderato delle categorie
        order = [
            'Da lavorare', 
            'Primo invio - in lavorazione', 
            'Presentata per primo invio', 
            'Integrazione - in lavorazione', 
            'Integrata', 
            'Conclusa'
        ]
        # Raggruppa i dati e usa reindex per ordinare le categorie
        pratiche_grouped = selection_query.groupby(['Stato_Pratica', 'Tecnico_Compilatore']).size().unstack(fill_value=0)
        pratiche_grouped = pratiche_grouped.reindex(order, axis=0)
        # Definisci una lista di colori esadecimali per i tecnici
        colori_tecnici = ['#fde910', '#00a6e9', '#d21759']  # Aggiungi altri colori se necessario
        # Creazione del grafico a funnel
        grafico_3 = go.Figure()
        for tecnico, colore in zip(pratiche_grouped.columns, colori_tecnici):
            grafico_3.add_trace(go.Funnel(
                name=tecnico,
                y=pratiche_grouped.index,
                x=pratiche_grouped[tecnico],
                textinfo="value",
                marker=dict(color=colore),
                textposition="inside",
                hoverinfo="name+x",
            ))
        # Impostazioni del layout
        grafico_3.update_layout(
            title="",
            legend=dict(title='Tecnico:'),
            yaxis_title="Stato Pratica",
            xaxis_title="Quantità P.E.",
            width=800,
            height=500,
            #margin=dict(t=70, b=20, l=10, r=10),
            font=dict(size=12)
        )
        # Visualizzazione del grafico
        st.plotly_chart(grafico_3)

    with col4:
        st.markdown('#### _Grafico 4:_')
        st.write("_Totale assoluto ore lavorate da ogni tecnico_")
        # Usa i dati filtrati
        pratiche_grouped = selection_query.groupby('Tecnico_Compilatore')['Tot_Ore_Lavorate'].sum()
        #pratiche_grouped = pratiche_grouped.sort_index(key=lambda x: x.str.lower())
        def absolute_value(val):
            a = np.round(val/100.*pratiche_grouped.sum(), 0)
            return int(a)
        # Creazione del grafico Donut Chart con Plotly Express
        grafico_4 = px.pie(names=pratiche_grouped.index, values=pratiche_grouped.values, 
                    title='', hole=0.4, template='plotly_dark', color_discrete_map={'Christian Campaner':'lightcyan',
                                                                                    'Simone Regazzo':'#lightcyan',
                                                                                    'Tania Finotto':'#lightcyan'})
        # Aggiunta l'etichetta con valore intero e percentuale
        grafico_4.update_traces(textposition='inside', textinfo='value+percent', text=pratiche_grouped.values, textfont_size=14)
        # Imposta layout grafico
        grafico_4.update_layout(legend=dict(title='Tecnico:'), height=470, width=650)
        # Visualizzazione del grafico
        st.plotly_chart(grafico_4)


    st.divider()  # 👈 Draws a horizontal rule


    # TERZA riga di grafici
    
    #  https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart          https://plotly.com/python/bar-charts/
    st.markdown('#### _Grafico 5:_')
    st.write("_Totale pratiche edilizie mensili a capo di ogni tecnico_")
    # Estrai i mesi dalla colonna "Data_Incarico_Pratica"
    selection_query['Mese'] = selection_query['Data_Incarico_Pratica'].dt.month
    # Raggruppa per tecnico e mese e conta il numero di pratiche
    pratiche_per_tecnico_mese = selection_query.groupby(['Tecnico_Compilatore', 'Mese']).size().reset_index(name='Count')
    # Crea il grafico
    grafico_5 = px.line(pratiche_per_tecnico_mese, x='Mese', y='Count', color='Tecnico_Compilatore', markers=True, 
                        title='', labels={'Mese': '', 'Count': 'Q.tà P.E.'},
                        template='plotly_dark')
    # Modifica le etichette dell'asse x con i nomi dei mesi
    grafico_5.update_xaxes(tickmode='array', tickvals=list(range(1, 13)),
                                ticktext=['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre'])
    # Modifica l'asse y per visualizzare i valori per ciascun mese
    grafico_5.update_yaxes(tickmode='linear')
    # Aggiungi assi verticali per ciascun mese
    for mese in range(1, 13):
        grafico_5.add_shape(
            type="line",
            x0=mese, y0=0,
            x1=mese, y1=pratiche_per_tecnico_mese['Count'].max(),
            line=dict(color="rgba(68, 68, 68, 0.5)", width=1),
            xref='x', yref='y'
        )
    # Imposta la larghezza del contenitore
    grafico_5.update_layout(width=1350, height=None)
    grafico_5.update_yaxes(automargin=True)
    # Mostra il grafico utilizzando Streamlit
    st.plotly_chart(grafico_5)


    st.divider()  # 👈 Draws a horizontal rule


    # QUARTA riga di grafici
    
    #  https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart          https://plotly.com/python/bar-charts/
    st.markdown('#### _Grafico 6:_')
    st.write("_Totale ore  mensili a capo di ogni tecnico_")
    # Estrai i mesi dalla colonna "Data_Incarico_Pratica"
    selection_query['Mese'] = selection_query['Data_Incarico_Pratica'].dt.month
    # Raggruppa per tecnico e mese e somma il numero totale di ore lavorate
    pratiche_per_tecnico_mese = selection_query.groupby(['Tecnico_Compilatore', 'Mese'])['Tot_Ore_Lavorate'].sum().reset_index()
    # Crea il grafico
    grafico_6 = px.line(pratiche_per_tecnico_mese, x='Mese', y='Tot_Ore_Lavorate', color='Tecnico_Compilatore', markers=True, 
                        title='', labels={'Mese': '', 'Tot_Ore_Lavorate': 'Totale Ore Lavorate'},
                        template='plotly_dark')
    # Modifica le etichette dell'asse x con i nomi dei mesi
    grafico_6.update_xaxes(tickmode='array', tickvals=list(range(1, 13)),
                                ticktext=['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre'])
    # Modifica l'asse y per visualizzare solo multipli di 10 per le ore lavorate
    grafico_6.update_yaxes(tickmode='array', tickvals=list(range(0, pratiche_per_tecnico_mese['Tot_Ore_Lavorate'].max() + 10, 10)))
    # Aggiungi assi verticali per ciascun mese
    for mese in range(1, 13):
        grafico_6.add_shape(
            type="line",
            x0=mese, y0=0,
            x1=mese, y1=pratiche_per_tecnico_mese['Tot_Ore_Lavorate'].max(),
            line=dict(color="rgba(68, 68, 68, 0.5)", width=1),
            xref='x', yref='y'
        )
    # Imposta la larghezza del contenitore
    grafico_6.update_layout(width=1350, height=None)
    grafico_6.update_yaxes(automargin=True)
    # Mostra il grafico utilizzando Streamlit
    st.plotly_chart(grafico_6)


############################################ TAB MAPPA con specifiche luoghi intervento/p.e. ############################################################################################################################################################################################################################
with tab3:
    st.markdown(' ')
    st.markdown(' ')
    
    try:
        st.write("_Mappa dei luoghi di intervento delle P.E._")
        
        # Filtraggio del dataframe pratiche_database
        filtered_pratiche = pratiche_database[
            (pratiche_database["Tecnico_Compilatore"].isin(tecnici)) &
            (pratiche_database["Data_Incarico_Pratica"].dt.month.isin(mesi_selezionati_numeri)) &
            (pratiche_database["Data_Incarico_Pratica"].dt.year.isin(anni_selezionati))
        ]
        
        # Crea la mappa solo se ci sono dati filtrati
        if not filtered_pratiche.empty:
            # Calcola la media delle coordinate per centrare la mappa
            center_lat = filtered_pratiche['Lat'].mean()
            center_long = filtered_pratiche['Long'].mean()
            # Crea la mappa Folium centrata sulla media delle coordinate filtrate
            Mymappa = folium.Map(location=[center_lat, center_long], zoom_start=8)
            # Crea un MarkerCluster per raggruppare i marker sulla mappa
            marker_cluster = MarkerCluster().add_to(Mymappa)
            # Aggiungi un marker per ogni riga del dataframe filtrato
            for index, row in filtered_pratiche.iterrows():
                # Contenuto popup personalizzato
                popup_content = f"""
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
                <ul class="list-group">
                <h3>Informazioni p.e.: {row['Codice_Pratica']}</h3>
                <hr class'bg-danger text-primary'>
                <div style='width:400px;height:200px;margin:10px;color:gray;text-size:18px;'>
                <li class="list-group-item"><b>Intestatario:</b> {row['Intestatario_principale']}</li>
                <li class="list-group-item"><b>Indirizzo:</b> {row['Indirizzo_totale']}</li>
                <li class="list-group-item"><b>Tipologia p.e.:</b> {row['Tipologia_P.E.']}</li>
                <li class="list-group-item"><b>Intervento:</b> {row['Descrizione_Intervento']}</li>
                <li class="list-group-item"><b>Stato lavorazione:</b> {row['Stato_Pratica']}</li>
                <li class="list-group-item"><b>Tot. ore lavorate:</b> {row['Tot_Ore_Lavorate']}</li>
                <li class="list-group-item"><b>Tecnico:</b> {row['Tecnico_Compilatore']}</li>
                """
                # Aggiungi il marker al MarkerCluster
                folium.Marker(
                    location=[row['Lat'], row['Long']], 
                    tooltip=row['Codice_Pratica'], 
                    icon=folium.Icon(color='red', icon='fas fa-crosshairs', prefix = 'fa'),
                ).add_to(marker_cluster).add_child(folium.Popup(popup_content, max_width=600)) 
            # Aggiungi heatmap layer
            heat_data = filtered_pratiche[['Lat', 'Long']].values.tolist()
            HeatMap(heat_data).add_to(Mymappa)
            # Aggiungi controlli per fullscreen e disegno sulla mappa
            Fullscreen(position='topright', title='Fullscreen', title_cancel='Exit Fullscreen').add_to(Mymappa)
            draw = Draw(export=True)
            draw.add_to(Mymappa)
            # Aggiungi layout e controlli per la mappa
            tiles = "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
            attr = "Google Digital Satellite"
            folium.TileLayer(tiles=tiles, attr=attr, name=attr, overlay=True, control=True).add_to(Mymappa)
            label_tiles = "https://mt1.google.com/vt/lyrs=h&x={x}&y={y}&z={z}"
            label_attr = "Google Labels"
            folium.TileLayer(tiles=label_tiles, attr=label_attr, name=label_attr, overlay=True, control=True).add_to(Mymappa)
            folium.LayerControl().add_to(Mymappa)  # Aggiungi controllo layer
            # Visualizza la mappa in Streamlit
            folium_static(Mymappa, width=1350, height=750)
        else:
            st.warning("Nessun dato trovato con i filtri selezionati.")
            
    except Exception as e:
        st.error(f"Errore durante la creazione della mappa: {e}")

