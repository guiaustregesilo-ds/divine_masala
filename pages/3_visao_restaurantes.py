# Libraries
from haversine import haversine
from PIL import Image
from streamlit_folium import folium_static

import folium
import pandas as pd
import plotly.graph_objects as go
import numpy as np

import streamlit as st

import datetime as dt
import plotly.express as px
import plotly.graph_objects as go
import os

#=====================
# Functions
#=====================

def avg_std_time_delivery(df2, festival,op):
    """
        Esta função calcula o tempo médio e o desvio padrão de tempo de entrega,
        Parametros:
            Input:
                - df2: DataFrame com os dados necessários para o cálculo
                - op: Tipo de operação a ser realizada
                     'avg_time': Calcula o tempo médio
                     'std_time': Calcula o desvio padrão
            Output:
                - df2_aux: DataFrame com 2 colunas e 1 Linha
    """
    cols = ['Time_taken(min)', 'Festival']
    df2_aux = df2.loc[:, cols].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})

    df2_aux.columns = ['avg_time', 'std_time']
    df2_aux = df2_aux.reset_index()
    df2_aux = np.round(df2_aux.loc[df2_aux['Festival'] == festival, op], 2)            
            
    return df2_aux

def distance(df2):
    cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df2['distance'] = (df2.loc[:, cols].apply(lambda x: haversine((
                                                    x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude'])),
                                                    axis=1))

    avg_distance = np.round(df2['distance'].mean(), 2)

    return avg_distance  

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

st.set_page_config(page_title='Visão Restaurantes', page_icon='📊', layout='wide')

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

st.header('Marketplace - Visão Restaurantes')


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
# Visão Restaurantes
# ================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])

with tab1:
    with st.container():
        
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Deliver Únicos', delivery_unique)

        with col2:
             avg_distance = distance(df2)
             col2.metric('AVG Distance', avg_distance)

        with col3:
            df2_aux = avg_std_time_delivery(df2, 'Yes', 'avg_time')
            col3.metric('AVG c/ Festival', df2_aux)

        with col4:
            df2_aux = avg_std_time_delivery(df2, 'Yes', 'std_time')
            col4.metric('STD c/ Festival', df2_aux)

        with col5:
            df2_aux = avg_std_time_delivery(df2, 'No', 'avg_time')
            col5.metric('AVG s/ Festival', df2_aux)
        
        with col6:  
            df2_aux = avg_std_time_delivery(df2, 'No', 'std_time')
            col6.metric('STD s/ Festival', df2_aux)  

    with st.container():
        st.markdown("""---""")
        st.title('Distribuição do Tempo de Entrega')

        cols = ['City', 'Time_taken(min)']

        df2_aux = df2.loc[:, cols].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})

        df2_aux.columns = ['avg_time', 'std_time']

        df2_aux = df2_aux.reset_index()

        fig = go.Figure()

        fig.add_trace(go.Bar(name='Control',
                                x=df2_aux['City'],
                                y=df2_aux['avg_time'],
                                error_y=dict(type='data', array=df2_aux['std_time'])))

        fig.update_layout(barmode='group')
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown("""---""")
        

        col1, col2 = st.columns(2)

        with col1:
            st.subheader('Tempo Médio de Entrega por Cidade')
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']

            df2['distance'] = (df2.loc[:, cols].apply(lambda x: haversine((
            x['Delivery_location_latitude'], x['Delivery_location_longitude']), 
            (x['Restaurant_latitude'], x['Restaurant_longitude'])), axis=1))   

            avg_distance = df2.loc[:,['City', 'distance']].groupby('City').mean().reset_index()

            fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('')
            st.subheader('AVG Time e STD por Trafego/Cidade')
            # selecionando as colunas
            cols = ['City', 'Time_taken(min)', 'Road_traffic_density' ]

            # criando a função
            df2_aux = df2.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})

            df2_aux.columns =  ['avg_time', 'std_time']

            df2_aux = df2_aux.reset_index()

            fig = px.sunburst(df2_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                            color='std_time', color_continuous_scale='RdBu',
                            color_continuous_midpoint=np.average(df2_aux['std_time']))

            st.plotly_chart(fig, use_container_width=True)

    with st.container():

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""---""")
            st.subheader('AVG e STD Time por Tipo de Pedido')
            # selecionando as colunas
            cols = ['City', 'Time_taken(min)', 'Type_of_order' ]

            # criando a função
            df2_aux = df2.loc[:, cols].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']}).reset_index()

            df2_aux.columns = ['City', 'Type_of_order', 'avg_time', 'std_time']

            st.dataframe(df2_aux)
            

        with col2:
            st.markdown("""---""")
            st.subheader('AVG e STD Time por Festival')
            cols = ['Time_taken(min)', 'Festival']
            df2_aux = df2.loc[:, cols].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})

            df2_aux.columns = ['avg_time', 'std_time']
            df2_aux = df2_aux.reset_index()

            #linhas_selecionadas = df2_aux['Festival'] == 'Yes'
            #df2_aux = df2_aux.loc[linhas_selecionadas, :]

            st.dataframe(df2_aux)
            


        


    #with st.container():
