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

st.set_page_config(page_title='Visão Entregadores', page_icon='📊', layout='wide')

# Import Dataset
df = pd.read_csv('C:/Users/Guilherme/Documents/repos/ftc_2/dataset/train.csv')

df1 = df.copy()

# 1.0 convertendo a coluna Age de texto para numero
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

#4.0 Convertendo Multiples Deliveries de texto para numero inteiro (int)
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

# limpando a coluna Time taken
df1 = df1.dropna(subset=['Time_taken(min)'])  # Remove linhas com NaN
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(str).apply(lambda x: x.split('(min) ')[1])
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)


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


#image_path = 'C:/Users/Guilherme/Documents/repos/ftc_2/divine_masala.png'
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

                df2['Time_taken(min)'] = pd.to_numeric(df2['Time_taken(min)'], errors='coerce')
                df2 = df2.dropna(subset=['Time_taken(min)'])  # Remover valores nulos

                # Remover espaços extras das colunas
                df2['City'] = df2['City'].str.strip()
                df2['Delivery_person_ID'] = df2['Delivery_person_ID'].str.strip()

                # Calcular a média do tempo de entrega por cidade e entregador
                df_grouped = (df2.groupby(['City', 'Delivery_person_ID'])['Time_taken(min)']
                            .mean()
                            .reset_index())

                # Ordenar por cidade e tempo de entrega (do menor para o maior)
                df_sorted = df_grouped.sort_values(['City', 'Time_taken(min)'], ascending=True)

                # Selecionar os 10 melhores entregadores por cidade
                df_aux1 = df_sorted[df_sorted['City'] == 'Metropolitian'].head(10)
                df_aux2 = df_sorted[df_sorted['City'] == 'Semi-Urban'].head(10)
                df_aux3 = df_sorted[df_sorted['City'] == 'Urban'].head(10)

                # Concatenar os resultados em um único DataFrame
                df_final = pd.concat([df_aux1, df_aux2, df_aux3]).reset_index(drop=True)
                st.dataframe(df_final)

            with col2:
                st.subheader('Top Entregadores mais lentos')

                df2['Time_taken(min)'] = pd.to_numeric(df2['Time_taken(min)'], errors='coerce')
                df2 = df2.dropna(subset=['Time_taken(min)'])  # Remover valores nulos

                # Remover espaços extras das colunas
                df2['City'] = df2['City'].str.strip()
                df2['Delivery_person_ID'] = df2['Delivery_person_ID'].str.strip()

                # Calcular a média do tempo de entrega por cidade e entregador
                df_grouped = (df2.groupby(['City', 'Delivery_person_ID'])['Time_taken(min)']
                            .mean()
                            .reset_index())

                # Ordenar por cidade e tempo de entrega (do menor para o maior)
                df_sorted = df_grouped.sort_values(['City', 'Time_taken(min)'], ascending=False)

                # Selecionar os 10 melhores entregadores por cidade
                df_aux1 = df_sorted[df_sorted['City'] == 'Metropolitian'].head(10)
                df_aux2 = df_sorted[df_sorted['City'] == 'Semi-Urban'].head(10)
                df_aux3 = df_sorted[df_sorted['City'] == 'Urban'].head(10)

                # Concatenar os resultados em um único DataFrame
                df_final = pd.concat([df_aux1, df_aux2, df_aux3]).reset_index(drop=True)
                st.dataframe(df_final)
            


        