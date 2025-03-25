import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='🏠',
    layout='wide'
)

# Carregar imagem
#image_path = 'C:/Users/Guilherme/Documents/repos/ftc_2/'
image = Image.open('divine_masala.png')
st.sidebar.image(image, width=120)

# Sidebar
st.sidebar.markdown('# 🚀 Divine Masala Express')
st.sidebar.markdown('## 🏎️ Fastest Delivery in Town')
st.sidebar.markdown("""---""")

# Título principal
st.write("""# 📊 Divine Masala Growth Dashboard""")

# Texto
st.markdown(
    """
    O Growth Dashboard do Divine Masala foi desenvolvido para fornecer uma visão abrangente e em tempo real do desempenho dos restaurantes e entregadores parceiros. Com o objetivo de otimizar operações e maximizar o crescimento, o dashboard oferece métricas detalhadas sobre o volume de pedidos, tempo médio de entrega, análise de vendas por dia/semana/mês, e a performance de cada entregador. Ele também permite monitorar a satisfação do cliente, o impacto de promoções e a performance de diferentes áreas geográficas, proporcionando insights valiosos para ajustes estratégicos. Ao centralizar esses dados, o Growth Dashboard facilita decisões informadas, ajudando o Divine Masala a alcançar novos patamares de eficiência e sucesso
    """
)

# Instruções de uso
st.markdown("""
## 🛠️ Como utilizar esse Growth Dashboard:
- **🏢 Visão Empresa:**  
  - 📊 **Visão Gerencial**: Métricas gerais de comportamento.  
  - 📈 **Visão Tática**: Indicadores semanais de crescimento.  
  - 🌍 **Visão Geográfica**: Insights de geolocalização.  

- **🚴‍♂️ Visão Entregadores:**  
  - 📦 Acompanhamento dos indicadores semanais de crescimento.  

- **🍽️ Visão Restaurantes:**  
  - 🍕 Acompanhamento dos indicadores semanais de crescimento.  

## 📩 Contato:
✉️ **Email**: guiaustregesilo.ds@gmail.com  

🔗 **Redes Sociais:**  
[![LinkedIn](https://img.shields.io/badge/🔗-LinkedIn-blue?logo=linkedin)](https://www.linkedin.com/in/guiaustregesilo/)  
[![GitHub](https://img.shields.io/badge/💻-GitHub-black?logo=github)](https://github.com/guiaustregesilo-ds)
""")


