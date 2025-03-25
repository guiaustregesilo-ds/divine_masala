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

st.set_page_config(page_title='Visão Restaurantes', page_icon='📊', layout='wide')

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
            cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

            df2['distance'] = (df2.loc[:, cols].apply(lambda x: haversine((
                x['Restaurant_latitude'], x['Restaurant_longitude']),
                  (x['Delivery_location_latitude'], x['Delivery_location_longitude'])),
                    axis=1))

            avg_distance = np.round(df2['distance'].mean(), 2)
            col2.metric('AVG Distance', avg_distance)

        with col3:
            cols = ['Time_taken(min)', 'Festival']
            df2_aux = df2.loc[:, cols].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})

            df2_aux.columns = ['avg_time', 'std_time']
            df2_aux = df2_aux.reset_index()
            df2_aux = np.round(df2_aux.loc[df2_aux['Festival'] == 'Yes', 'avg_time'], 2)

            col3.metric('AVG c/ Festival', df2_aux)

        with col4:
            cols = ['Time_taken(min)', 'Festival']
            df2_aux = df2.loc[:, cols].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})

            df2_aux.columns = ['avg_time', 'std_time']
            df2_aux = df2_aux.reset_index()
            df2_aux = np.round(df2_aux.loc[df2_aux['Festival'] == 'Yes', 'std_time'], 2)

            col4.metric('STD c/ Festival', df2_aux)

        with col5:
            cols = ['Time_taken(min)', 'Festival']
            df2_aux = df2.loc[:, cols].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})

            df2_aux.columns = ['avg_time', 'std_time']
            df2_aux = df2_aux.reset_index()
            df2_aux = np.round(df2_aux.loc[df2_aux['Festival'] == 'No', 'avg_time'], 2)

            col5.metric('AVG s/ Festival', df2_aux)
        
        with col6:  
            cols = ['Time_taken(min)', 'Festival']
            df2_aux = df2.loc[:, cols].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']})

            df2_aux.columns = ['avg_time', 'std_time']
            df2_aux = df2_aux.reset_index()
            df2_aux = np.round(df2_aux.loc[df2_aux['Festival'] == 'No', 'std_time'], 2)

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
