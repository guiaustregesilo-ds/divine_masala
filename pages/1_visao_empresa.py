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

#=====================
# Functions
#=====================

def country_maps(df2):        
    df2_aux = (df2.loc[:,['City', 'Road_traffic_density','Delivery_location_latitude', 'Delivery_location_longitude']]
                   .groupby(['City', 'Road_traffic_density'])
                   .median()
                   .reset_index())
    df2_aux = df2_aux.loc[df2_aux['City'] != 'NaN ', :]
    df2_aux = df2_aux.loc[df2_aux['Road_traffic_density'] != 'NaN', :]
    
    map_ = folium.Map()
    for index, location_info in df2_aux.iterrows():
            folium.Marker([location_info['Delivery_location_latitude'],
                       location_info['Delivery_location_longitude']],
                       popup=location_info[['City', 'Road_traffic_density']]).add_to(map_)
            
    folium_static(map_, width = 1024, height = 600)
    
    return None
    

def order_share_by_week(df2):  
    df2_aux01 = df2.loc[:,['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df2_aux02 = df2.loc[:,['Delivery_person_ID','week_of_year']].groupby('week_of_year').nunique().reset_index()
    df2_aux = pd.merge(df2_aux01, df2_aux02, how='inner', on='week_of_year')
    df2_aux['order_by_delivery'] = df2_aux['ID']/df2_aux['Delivery_person_ID']
    fig = px.line(df2_aux, x='week_of_year', y='order_by_delivery')

    return fig

def order_by_week(df2):
    df2['week_of_year'] = df2['Order_Date'].dt.strftime('%U')
    colunas = ['ID', 'week_of_year']
    colunas_groupby = ['week_of_year']
    df2_aux = df2.loc[:, colunas].groupby(colunas_groupby).count().reset_index()
    fig = px.line(df2_aux, x='week_of_year', y='ID')

    return fig

def traffic_order_city(df2):
    df2_aux = df2.loc[:,['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    df2_aux = df2_aux.loc[df2_aux['City'] != 'NaN ', :]
    df2_aux = df2_aux.loc[df2_aux['Road_traffic_density'] != 'NaN', :]
    fig = px.scatter(df2_aux, x='City', y='Road_traffic_density', size='ID', color='City')

    return fig

def traffic_order_share(df2):
    df2_aux = df2.loc[:,['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df2_aux = df2_aux.loc[df2_aux['Road_traffic_density'] != 'NaN', :]
    df2_aux['entregas_perc'] = df2_aux['ID'] / df2_aux['ID'].sum() 
    fig = px.pie(df2_aux, values='entregas_perc', names='Road_traffic_density')

    return fig

def order_metric(df2):
    df2 = df1.copy()

    colunas = ['ID', 'Order_Date']
    colunas_groupby = ['Order_Date']

    df2_aux = df2.loc[:, colunas].groupby(colunas_groupby).count().reset_index()

    fig = px.bar(df2_aux, x='Order_Date', y='ID')

    return fig

def clean_code(df1):  
    '''
    Função para limpar o dataframe
    Tipos de limpeza:
    1. Remoção dos dados NaN
    2. Mudança do tipo da coluna de dados
    3. Remoção dos espaços nos dados
    4. Formatação da coluna de datas
    5. Limpeza da coluna de tempo (remoção do texto da coluna time_taken(min))
    '''
    
    df1 = df1.copy()  # Garante que as alterações não afetem o dataframe original

    # Removendo linhas com valores "NaN"
    df1 = df1[df1['Delivery_person_Age'] != 'NaN ']
    df1 = df1[df1['Road_traffic_density'] != 'NaN ']
    df1 = df1[df1['City'] != 'NaN ']
    df1 = df1[df1['multiple_deliveries'] != 'NaN ']

    # Convertendo tipos de dados
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # Convertendo coluna de data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # Removendo espaços em branco das colunas categóricas
    for col in ['ID', 'Road_traffic_density', 'Festival', 'Type_of_vehicle', 'Type_of_order']:
        df1[col] = df1[col].str.strip()

    # Limpando a coluna Time taken
    df1 = df1.dropna(subset=['Time_taken(min)'])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(str).str.extract('(\d+)').astype(int)

    return df1

st.set_page_config(page_title='Visão Empresa', page_icon='📊', layout='wide')


# ===================== Inicio da Estrutura lógica do código =====================


# ========================
# Import dataset
# ========================
df = pd.read_csv('dataset/train.csv')

# ========================
# Limpando os dados
# ========================
df1 = clean_code(df)

# visao empresa

df2 = df1.copy()

colunas = ['ID', 'Order_Date']
colunas_groupby = ['Order_Date']

df2_aux = df2.loc[:, colunas].groupby(colunas_groupby).count().reset_index()

px.bar(df2_aux, x='Order_Date', y='ID')


# ================================
# Barra Lateral
# ================================

st.header('Marketplace - Visão Cliente')



image = Image.open('divine_masala.png')
st.sidebar.image(image, width = 200)

st.sidebar.markdown('# DivineMasala Express')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""----""")

st.sidebar.markdown('## Selecione uma data limite:')

data_slider= st.sidebar.slider(
    'Até qual valor ?',
    value=dt.datetime(2022, 4, 13),
    min_value=dt.datetime(2022, 2, 11),
    max_value=dt.datetime(2022, 6, 4),
    format='DD-MM-YYYY')

st.sidebar.markdown("""----""")

traffic_options= st.sidebar.multiselect(
    'Quais as Condições de Trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""----""")
st.sidebar.markdown('### Powered by @guiaustregesilo.ds')

# Filtro de Data
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selecionadas,:]

# Filtro de Trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]

st.dataframe(df1)

# ================================
# Layout - Visão Empresa
# ================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        # Order Metric
        fig = order_metric(df2)
        st.markdown( '# Orders by Day')
        st.plotly_chart(fig, use_container_width=True)

       
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.header('Traffic Order Share')
            fig = traffic_order_share(df2)
            st.plotly_chart(fig, use_container_width=True)
       
        with col2:
             st.header('Traffic Order City')
             fig = traffic_order_city(df2)
             st.plotly_chart(fig, use_container_width=True)
    
with tab2:
    with st.container():
         st.markdown('## Order by Week')
         fig = order_by_week(df2)
         st.plotly_chart(fig, use_container_width=True)
        
    with st.container():
         st.markdown('## Order Share by Week')
         fig = order_share_by_week(df2)
         st.plotly_chart(fig, use_container_width=True)


        
        
with tab3:
    st.markdown('## Country Maps')
    country_maps(df2)
        








#file_path = "C:/Users/Guilherme/Documents/repos/ftc_2/dataset/train.csv"

# Verifique se o arquivo existe
#if os.path.exists(file_path):
    #try:
        # Leia as primeiras linhas do arquivo para inspecionar manualmente
        #with open(file_path, 'r', encoding='utf-8') as file:
            #lines = [next(file) for _ in range(10)]
            #for i, line in enumerate(lines):
                #print(f"Linha {i+1}: {line.strip()}")
    #except UnicodeDecodeError:
        #with open(file_path, 'r', encoding='ISO-8859-1') as file:
            #lines = [next(file) for _ in range(10)]
            #for i, line in enumerate(lines):
                #print(f"Linha {i+1}: {line.strip()}")
#else:
    #print(f"Erro: O arquivo '{file_path}' não existe.")
