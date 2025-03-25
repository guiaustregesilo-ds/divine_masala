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

def top_deliveries(df2, top_asc):
    df2['Time_taken(min)'] = pd.to_numeric(df2['Time_taken(min)'], errors='coerce')
    df2 = df2.dropna(subset=['Time_taken(min)'])  

    df2['City'] = df2['City'].str.strip()
    df2['Delivery_person_ID'] = df2['Delivery_person_ID'].str.strip()

    df_grouped = (df2.groupby(['City', 'Delivery_person_ID'])['Time_taken(min)']
                            .mean()
                            .reset_index())

    df_sorted = df_grouped.sort_values(['City', 'Time_taken(min)'], ascending=top_asc)

    df_aux1 = df_sorted[df_sorted['City'] == 'Metropolitian'].head(10)
    df_aux2 = df_sorted[df_sorted['City'] == 'Semi-Urban'].head(10)
    df_aux3 = df_sorted[df_sorted['City'] == 'Urban'].head(10)

    df_final = pd.concat([df_aux1, df_aux2, df_aux3]).reset_index(drop=True)

    return df_final

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


st.set_page_config(page_title='Visão Entregadores', page_icon='📊', layout='wide')


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

st.header('Marketplace - Visão Entregadores')


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


# ================================
# Layout - Visão Entregadores
# ================================

tab1, tab, tab3 = st.tabs(['Visão Gerêncial', '-', '-'])

with tab1:
    with st.container():
        st.title('Overal Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')

        with col1:
            # maior idade dos entregadores
            maior_idade = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric('Maior de Idade', maior_idade)

        with col2:
            # menor idade dos entregadores
            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor de Idade', menor_idade)
        
        with col3:
            # melhor condição de veículos
            melhor_condicao_veiculo = df2.loc[:,'Vehicle_condition'].max()
            col3.metric('Melhor Cond. Veículos', melhor_condicao_veiculo)

        with col4:
            # pior condição de veículos
            pior_condicao_veiculo = df2.loc[:,'Vehicle_condition'].min()
            col4.metric('Pior Cond. Veículos', pior_condicao_veiculo)


    with st.container():
        st.markdown('------')
        st.title('Avaliações')

        col1, col2 = st.columns(2)

        with col1:
            st.subheader('Avaliação Média por Entregadores')
            df2_avg_ratings_per_deliver= (df2.loc[:,['Delivery_person_ID','Delivery_person_Ratings']]
                                          .groupby('Delivery_person_ID')
                                          .mean()
                                          .reset_index())
            st.dataframe(df2_avg_ratings_per_deliver)
            
        with col2:
            st.subheader('Avaliação Média por Trânsito')
            df_avg_std_rating_by_traffic = ((df2.loc[:,['Delivery_person_Ratings','Road_traffic_density']]
                                             .groupby('Road_traffic_density')
                                             .agg({'Delivery_person_Ratings':['mean','std']})))
            df_avg_std_rating_by_traffic.columns = ['Delivery_mean','Delivery_std']
            df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()
            st.dataframe(df_avg_std_rating_by_traffic)

            st.subheader('Avaliação Média por Clima')
            df_avg_std_rating_by_weather = (df2.loc[:,['Delivery_person_Ratings','Weatherconditions']]
                                            .groupby('Weatherconditions')
                                            .agg({'Delivery_person_Ratings':['mean','std']}))
            df_avg_std_rating_by_weather.columns = ['Delivery_mean','Delivery_std']
            df_avg_std_rating_by_weather = df_avg_std_rating_by_weather.reset_index()
            st.dataframe(df_avg_std_rating_by_weather)

        with st.container():
            st.markdown('------')
            st.title('Velocidade de Entrega')

            col1, col2 = st.columns(2)

            with col1:
                st.subheader('Top Entregadores mais rápidos')
                df_final = top_deliveries(df2, top_asc = True)
                st.dataframe(df_final)

            with col2:
                 st.subheader('Top Entregadores mais lentos')
                 df_final = top_deliveries(df2, top_asc = False)
                 st.dataframe(df_final)
                


                

              
                
            


        
