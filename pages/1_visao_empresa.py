# Libraries
from haversine import haversine
from PIL import Image
from streamlit_folium import folium_static

import folium
import pandas as pd

import streamlit as st

import datetime as dt
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title='Visão Empresa', page_icon='📊', layout='wide')

# Verifique se o arquivo existe antes de tentar carregá-lo
dataset_path = 'C:/Users/Guilherme/Documents/repos/ftc_2/dataset/train.csv'

if os.path.exists(dataset_path):
    df = pd.read_csv(dataset_path)
else:
    st.error(f"Arquivo não encontrado: {dataset_path}")
    st.stop()  # Para o código se o arquivo não for encontrado

df1 = df.copy()

# 1.0 Convertendo a coluna Age de texto para numero
linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN '
df1 = df1.loc[linhas_selecionadas,:].copy()

linhas_selecionadas = df1['Road_traffic_density'] != 'NaN '
df1 = df1.loc[linhas_selecionadas,:].copy()

linhas_selecionadas = df1['City'] != 'NaN '
df1 = df1.loc[linhas_selecionadas,:].copy()

df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

# 2.0 Convertendo a coluna Ratings de texto para numero decimal (float)
df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

# 3.0 Convertendo a Coluna OrderDate para Data
df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

# 4.0 Convertendo Multiples Deliveries de texto para numero inteiro (int)
linhas_selecionadas = df1['multiple_deliveries']  != 'NaN '
df1 = df1.loc[linhas_selecionadas, :].copy()
df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

# 5.0 Removendo os espaços

# ID
df1 = df1.reset_index(drop=True)
for i in range(len(df1)):
    df1.loc[i,'ID'] = df1.loc[i,'ID'].strip()

# Road_traffic_density
df1 = df1.reset_index(drop=True)
for i in range(len(df1)):
    df1.loc[i,'Road_traffic_density'] = df1.loc[i,'Road_traffic_density'].strip()

# Festival
df1 = df1.reset_index(drop=True)
for i in range(len(df1)):
    df1.loc[i,'Festival'] = df1.loc[i,'Festival'].strip()

# type_of_vehicle
df1 = df1.reset_index(drop=True)
for i in range(len(df1)):
    df1.loc[i,'Type_of_vehicle'] = df1.loc[i,'Type_of_vehicle'].strip()

# Type_of_order
df1 = df1.reset_index(drop=True)
for i in range(len(df1)):
    df1.loc[i,'Type_of_order'] = df1.loc[i,'Type_of_order'].strip()

# Limpando a coluna Time taken
df1 = df1.dropna(subset=['Time_taken(min)'])  # Remove linhas com NaN
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(str).apply(lambda x: x.split('(min) ')[1])
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

# Visão Empresa
df2 = df1.copy()

colunas = ['ID', 'Order_Date']
colunas_groupby = ['Order_Date']

df2_aux = df2.loc[:, colunas].groupby(colunas_groupby).count().reset_index()

# ================================
# Barra Lateral
# ================================

st.header('Marketplace - Visão Cliente')

# Caminho da imagem
image_path = 'divine_masala.png'

if os.path.exists(image_path):
    image = Image.open(image_path)
    st.sidebar.image(image, width=200)
else:
    st.sidebar.error(f"Imagem não encontrada: {image_path}")

st.sidebar.markdown('# DivineMasala Express')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""----""")

st.sidebar.markdown('## Selecione uma data limite:')

data_slider = st.sidebar.slider(
    'Até qual valor?',
    value=dt.datetime(2022, 4, 13),
    min_value=dt.datetime(2022, 2, 11),
    max_value=dt.datetime(2022, 6, 4),
    format='DD-MM-YYYY')

st.sidebar.markdown("""----""")

traffic_options = st.sidebar.multiselect(
    'Quais as Condições de Trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""----""")
st.sidebar.markdown('### Powered by @guiaustregesilo.ds')

# Filtro de Data
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de Trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

st.dataframe(df1)

# ================================
# Layout - Visão Empresa
# ================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        # Order Metric
        st.markdown('# Orders by Day')
        df2 = df1.copy()

        colunas = ['ID', 'Order_Date']
        colunas_groupby = ['Order_Date']

        df2_aux = df2.loc[:, colunas].groupby(colunas_groupby).count().reset_index()

        fig = px.bar(df2_aux, x='Order_Date', y='ID')
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.header('Traffic Order Share')
            df2_aux = df2.loc[:,['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
            df2_aux = df2_aux.loc[df2_aux['Road_traffic_density'] != 'NaN', :]
            df2_aux['entregas_perc'] = df2_aux['ID'] / df2_aux['ID'].sum() 
            fig = px.pie(df2_aux, values='entregas_perc', names='Road_traffic_density')
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.header('Traffic Order City')
            df2_aux = df2.loc[:,['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
            df2_aux = df2_aux.loc[df2_aux['City'] != 'NaN ', :]
            df2_aux = df2_aux.loc[df2_aux['Road_traffic_density'] != 'NaN', :]
            fig = px.scatter(df2_aux, x='City', y='Road_traffic_density', size='ID', color='City')
            st.plotly_chart(fig, use_container_width=True)
        
with tab2:
    with st.container():
        st.markdown('## Order by Week')
        df2['week_of_year'] = df2['Order_Date'].dt.strftime('%U')
        colunas = ['ID', 'week_of_year']
        colunas_groupby = ['week_of_year']
        df2_aux = df2.loc[:, colunas].groupby(colunas_groupby).count().reset_index()
        fig = px.line(df2_aux, x='week_of_year', y='ID')
        st.plotly_chart(fig, use_container_width=True)
        
    with st.container():
        st.markdown('## Order Share by Week')
        df2_aux01 = df2.loc[:,['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        df2_aux02 = df2.loc[:,['Delivery_person_ID','week_of_year']].groupby('week_of_year').nunique().reset_index()
        df2_aux = pd.merge(df2_aux01, df2_aux02, how='inner', on='week_of_year')
        df2_aux['order_by_delivery'] = df2_aux['ID']/df2_aux['Delivery_person_ID']
        fig = px.line(df2_aux, x='week_of_year', y='order_by_delivery')
        st.plotly_chart(fig, use_container_width=True)
        
with tab3:
    st.markdown('## Country Maps')
    df2_aux = df2.loc[:,['City', 'Road_traffic_density','Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    df2_aux = df2_aux.loc[df2_aux['City'] != 'NaN ', :]
    df2_aux = df2_aux.loc[df2_aux['Road_traffic_density'] != 'NaN', :]
    map_ = folium.Map()
    for index, location_info in df2_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                       location_info['Delivery_location_longitude']],
                       popup=location_info[['City', 'Road_traffic_density']]).add_to(map_)
    folium_static(map_, width=1024, height=600)
