import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
import json
import glob
from datetime import datetime
import re
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
from geopy.distance import geodesic
import warnings
warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(
    page_title="🏦 Análisis Multi-Bancos CDMX",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para tema oscuro
st.markdown("""
<style>
    /* Tema oscuro global */
    .stApp {
        background: linear-gradient(180deg, #0e1117 0%, #1a1d29 100%);
        color: #ffffff;
    }
    
    .main-header {
        font-size: 3.5rem;
        background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 0 0 20px rgba(255, 0, 0, 0.3);
        font-weight: bold;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
        border: 1px solid #4a5568;
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(4px);
    }
    
    .metric-card h2 {
        color: #ff0000;
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
    }
    
    .metric-card h3 {
        color: #a0aec0;
        font-size: 1rem;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .banco-santander {
        border-left: 5px solid #ff0000;
        background: linear-gradient(135deg, rgba(255, 0, 0, 0.1) 0%, rgba(255, 0, 0, 0.05) 100%);
        padding-left: 1rem;
        border-radius: 0 10px 10px 0;
    }
    
    .banco-bbva {
        border-left: 5px solid #004CFF;
        background: linear-gradient(135deg, rgba(0, 76, 255, 0.1) 0%, rgba(0, 76, 255, 0.05) 100%);
        padding-left: 1rem;
        border-radius: 0 10px 10px 0;
    }
    
    .banco-banorte {
        border-left: 5px solid #00C851;
        background: linear-gradient(135deg, rgba(0, 200, 81, 0.1) 0%, rgba(0, 200, 81, 0.05) 100%);
        padding-left: 1rem;
        border-radius: 0 10px 10px 0;
    }
    
    .insight-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .highlight-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        text-align: center;
    }
    
    .success-card {
        background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        text-align: center;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1d29 0%, #2d3748 100%);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 5px;
        background: rgba(45, 55, 72, 0.3);
        border-radius: 15px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        padding: 0 25px;
        background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
        border-radius: 12px;
        color: #a0aec0;
        border: 1px solid #4a5568;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%);
        color: white;
        border: 1px solid #ff0000;
        box-shadow: 0 4px 20px rgba(255, 0, 0, 0.3);
    }
    
    /* Mejorar selectbox y otros elementos */
    .stSelectbox > div > div {
        background-color: #2d3748;
        color: white;
        border: 1px solid #4a5568;
    }
    
    .stMultiSelect > div > div {
        background-color: #2d3748;
        color: white;
        border: 1px solid #4a5568;
    }
    
    /* Gráficos con fondo oscuro */
    .js-plotly-plot {
        background: rgba(45, 55, 72, 0.3) !important;
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

class BankAnalyzer:
    def __init__(self):
        """Inicializa el analizador de datos bancarios"""
        self.data = None
        self.competencia_data = None
        self.banco_colors = {
            'Santander': '#ff0000',
            'BBVA': '#004CFF', 
            'Banorte': '#00C851'
        }
    
    @st.cache_data
    def load_data(_self):
        """Carga los datos desde archivos generados"""
        try:
            # Buscar archivos más recientes
            json_files = glob.glob("multibancos_cdmx_*.json")
            csv_files = glob.glob("multibancos_cdmx_*.csv")
            competencia_files = glob.glob("multibancos_cdmx_competencia_*.json")
            
            if not csv_files:
                return None, None
            
            # Cargar archivo más reciente
            latest_csv = max(csv_files, key=lambda x: x.split('_')[-1])
            df = pd.read_csv(latest_csv)
            
            # Cargar datos de competencia si existen
            competencia_df = None
            if competencia_files:
                latest_comp = max(competencia_files, key=lambda x: x.split('_')[-1])
                with open(latest_comp, 'r', encoding='utf-8') as f:
                    competencia_data = json.load(f)
                    competencia_df = pd.DataFrame([
                        {
                            'place_id': comp['sucursal_base']['place_id'],
                            'banco': comp['sucursal_base']['banco'],
                            'nombre': comp['sucursal_base']['nombre'],
                            'total_competidores': comp['total_competidores'],
                            'competidor_mas_cercano': comp['competidor_mas_cercano'],
                            'ventaja_rating': comp['ventaja_rating']
                        }
                        for comp in competencia_data
                    ])
            
            return df, competencia_df
            
        except Exception as e:
            st.error(f"Error cargando datos: {e}")
            return None, None
    
    def analyze_sentiment(self, text):
        """Analiza el sentimiento de un texto"""
        try:
            if pd.isna(text) or text == '':
                return 0
            blob = TextBlob(str(text))
            return blob.sentiment.polarity
        except:
            return 0
    
    def categorize_sentiment(self, polarity):
        """Categoriza el sentimiento"""
        if polarity > 0.1:
            return 'Positivo'
        elif polarity < -0.1:
            return 'Negativo'
        else:
            return 'Neutral'
    
    def process_reviews_data(self, df):
        """Procesa los datos de reseñas para análisis"""
        reviews_data = []
        
        for _, row in df.iterrows():
            try:
                reviews = eval(row['reviews']) if isinstance(row['reviews'], str) else []
                for review in reviews:
                    sentiment_score = self.analyze_sentiment(review.get('texto', ''))
                    reviews_data.append({
                        'place_id': row['place_id'],
                        'banco': row['banco'],
                        'nombre_sucursal': row['nombre'],
                        'alcaldia': row['alcaldia'],
                        'lat': row['lat'],
                        'lng': row['lng'],
                        'autor': review.get('autor', ''),
                        'rating_review': review.get('rating', 0),
                        'texto': review.get('texto', ''),
                        'fecha': review.get('fecha', ''),
                        'sentiment_score': sentiment_score,
                        'sentiment_category': self.categorize_sentiment(sentiment_score),
                        'sucursal_rating': row['rating'],
                        'total_reviews': row['total_reviews']
                    })
            except:
                continue
        
        return pd.DataFrame(reviews_data)

def main():
    # Header principal
    st.markdown('''
    <div style="text-align: center; margin-bottom: 2rem;">
        <span style="font-size: 3.5rem; margin-right: 15px;">🏦</span>
        <span style="font-size: 3.5rem; background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-weight: bold;">Análisis Multi-Bancos CDMX</span>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center; color: #666;">Dashboard Interactivo de Reseñas y Competencia Bancaria</h3>', unsafe_allow_html=True)
    
    # Inicializar analizador
    analyzer = BankAnalyzer()
    
    # Cargar datos
    with st.spinner('🔄 Cargando datos...'):
        df, competencia_df = analyzer.load_data()
    
    if df is None:
        st.error("❌ No se encontraron datos. Ejecuta primero el extractor V1Extractor.py")
        st.info("💡 Asegúrate de tener archivos multibancos_cdmx_*.csv en el directorio")
        return
    
    # Procesar datos de reseñas
    with st.spinner('🔍 Analizando reseñas...'):
        reviews_df = analyzer.process_reviews_data(df)
    
    # Filtros principales en el contenido
    st.subheader("🎛️ Filtros y Configuración")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Filtros
        bancos_disponibles = df['banco'].unique()
        banco_seleccionado = st.multiselect(
            "🏛️ Selecciona Bancos",
            bancos_disponibles,
            default=bancos_disponibles
        )
    
    with col2:
        alcaldias_disponibles = df['alcaldia'].unique()
        alcaldia_seleccionada = st.multiselect(
            "🗺️ Selecciona Alcaldías",
            alcaldias_disponibles,
            default=alcaldias_disponibles[:5] if len(alcaldias_disponibles) > 5 else alcaldias_disponibles
        )
    
    # Filtrar datos
    df_filtered = df[
        (df['banco'].isin(banco_seleccionado)) & 
        (df['alcaldia'].isin(alcaldia_seleccionada))
    ]
    
    reviews_filtered = reviews_df[
        (reviews_df['banco'].isin(banco_seleccionado)) & 
        (reviews_df['alcaldia'].isin(alcaldia_seleccionada))
    ]
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🏦 Total Sucursales</h3>
            <h2>{}</h2>
        </div>
        """.format(len(df_filtered)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>💬 Total Reseñas</h3>
            <h2>{}</h2>
        </div>
        """.format(len(reviews_filtered)), unsafe_allow_html=True)
    
    with col3:
        avg_rating = df_filtered['rating'].mean()
        st.markdown("""
        <div class="metric-card">
            <h3>⭐ Rating Promedio</h3>
            <h2>{:.2f}</h2>
        </div>
        """.format(avg_rating), unsafe_allow_html=True)
    
    with col4:
        if competencia_df is not None:
            competencia_filtered = competencia_df[competencia_df['banco'].isin(banco_seleccionado)]
            if not competencia_filtered.empty:
                avg_competencia = competencia_filtered['total_competidores'].mean()
                st.markdown("""
                <div class="metric-card">
                    <h3>🎯 Competencia Promedio</h3>
                    <h2>{:.1f}</h2>
                </div>
                """.format(avg_competencia), unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="metric-card">
                    <h3>🎯 Competencia</h3>
                    <h2>0.0</h2>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card">
                <h3>🎯 Competencia</h3>
                <h2>N/A</h2>
            </div>
            """, unsafe_allow_html=True)
    
    # Tabs principales - Expandidos
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Resumen General", 
        "💬 Análisis de Reseñas", 
        "🎯 Análisis de Competencia",
        "🗺️ Mapas Interactivos",
        "📈 Analytics Avanzados",
        "🔍 Deep Insights",
        "📋 Reporte Ejecutivo"
    ])
    
    with tab1:
        show_general_summary(df_filtered, analyzer)
    
    with tab2:
        show_reviews_analysis(reviews_filtered, analyzer)
    
    with tab3:
        show_competition_analysis(df_filtered, competencia_df, analyzer)
    
    with tab4:
        show_interactive_maps(df_filtered, reviews_filtered)
    
    with tab5:
        show_advanced_insights(df_filtered, reviews_filtered, competencia_df, analyzer)
    
    with tab6:
        show_deep_insights(df_filtered, reviews_filtered, competencia_df, analyzer)
    
    with tab7:
        show_executive_report(df_filtered, reviews_filtered, competencia_df, analyzer)

def show_general_summary(df, analyzer):
    """Muestra resumen general de los datos"""
    st.header("📊 Resumen General por Banco")
    
    # Análisis por banco
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de sucursales por banco
        banco_counts = df['banco'].value_counts()
        fig_banco = px.pie(
            values=banco_counts.values,
            names=banco_counts.index,
            title="Distribución de Sucursales por Banco"
        )
        
        # Asegurar que los colores se apliquen correctamente
        colors = [analyzer.banco_colors.get(name, '#cccccc') for name in banco_counts.index]
        fig_banco.update_traces(marker=dict(colors=colors))
        
        fig_banco.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_size=16,
            title_font_color='#ff0000'
        )
        st.plotly_chart(fig_banco, use_container_width=True)
    
    with col2:
        # Gráfico de ratings por banco
        fig_rating = px.box(
            df, 
            x='banco', 
            y='rating',
            title="Distribución de Ratings por Banco",
            color='banco',
            color_discrete_map=analyzer.banco_colors
        )
        fig_rating.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_size=16,
            title_font_color='#ff0000'
        )
        st.plotly_chart(fig_rating, use_container_width=True)
    
    # Análisis por alcaldía
    st.subheader("🏛️ Distribución por Alcaldía")
    
    # Heatmap de sucursales por alcaldía y banco
    pivot_data = df.groupby(['alcaldia', 'banco']).size().unstack(fill_value=0)
    
    fig_heatmap = px.imshow(
        pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        color_continuous_scale='Blues',
        title="Distribución de Sucursales por Alcaldía y Banco"
    )
    fig_heatmap.update_layout(
        height=600,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_color='#ff0000'
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Tabla de estadísticas
    st.subheader("📋 Estadísticas Detalladas")
    stats_table = df.groupby('banco').agg({
        'nombre': 'count',
        'rating': ['mean', 'std'],
        'total_reviews': ['sum', 'mean']
    }).round(2)
    
    stats_table.columns = ['Sucursales', 'Rating Promedio', 'Rating Std', 'Total Reseñas', 'Reseñas Promedio']
    st.dataframe(stats_table, use_container_width=True)

def show_reviews_analysis(reviews_df, analyzer):
    """Muestra análisis detallado de reseñas"""
    st.header("💬 Análisis de Reseñas y Sentimientos")
    
    if reviews_df.empty:
        st.warning("⚠️ No hay datos de reseñas disponibles")
        return
    
    # Análisis de sentimientos
    col1, col2, col3 = st.columns(3)
    
    sentiment_counts = reviews_df['sentiment_category'].value_counts()
    
    with col1:
        positivo = sentiment_counts.get('Positivo', 0)
        st.metric("😊 Reseñas Positivas", positivo, f"{positivo/len(reviews_df)*100:.1f}%")
    
    with col2:
        neutral = sentiment_counts.get('Neutral', 0)
        st.metric("😐 Reseñas Neutrales", neutral, f"{neutral/len(reviews_df)*100:.1f}%")
    
    with col3:
        negativo = sentiment_counts.get('Negativo', 0)
        st.metric("😞 Reseñas Negativas", negativo, f"{negativo/len(reviews_df)*100:.1f}%")
    
    # Gráficos de sentimientos
    col1, col2 = st.columns(2)
    
    with col1:
        # Sentimientos por banco
        sentiment_banco = reviews_df.groupby(['banco', 'sentiment_category']).size().unstack(fill_value=0)
        fig_sentiment = px.bar(
            sentiment_banco,
            title="Distribución de Sentimientos por Banco",
            color_discrete_map={'Positivo': '#2E8B57', 'Neutral': '#FFD700', 'Negativo': '#DC143C'}
        )
        st.plotly_chart(fig_sentiment, use_container_width=True)
    
    with col2:
        # Relación entre rating y sentimiento
        fig_scatter = px.scatter(
            reviews_df,
            x='rating_review',
            y='sentiment_score',
            color='banco',
            title="Relación Rating vs Sentimiento",
            color_discrete_map=analyzer.banco_colors,
            hover_data=['nombre_sucursal', 'texto']
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # WordCloud por banco
    st.subheader("☁️ WordCloud por Banco")
    
    # Función para filtrar palabras mayores a 3 caracteres
    def filter_words(text):
        """Filtra palabras mayores a 3 caracteres y elimina palabras comunes"""
        import re
        
        # Palabras comunes a filtrar
        stop_words = {'para', 'que', 'con', 'una', 'por', 'muy', 'bien', 'banco', 'sucursal', 
                     'servicio', 'atencion', 'personal', 'cajero', 'desde', 'hasta', 'donde',
                     'cuando', 'como', 'todo', 'todos', 'todas', 'esta', 'este', 'esto',
                     'tienen', 'siempre', 'nunca', 'puede', 'hacer', 'tiempo', 'años'}
        
        # Limpiar texto y filtrar palabras
        words = re.findall(r'\b[a-záéíóúñ]{4,}\b', text.lower())
        filtered_words = [word for word in words if word not in stop_words]
        return ' '.join(filtered_words)
    
    # Crear columnas para cada banco
    bancos = reviews_df['banco'].unique()
    if len(bancos) == 3:
        col1, col2, col3 = st.columns(3)
        columns = [col1, col2, col3]
    elif len(bancos) == 2:
        col1, col2 = st.columns(2)
        columns = [col1, col2]
    else:
        columns = [st.container()]
    
    banco_colors_wc = {
        'Santander': '#ff0000',
        'BBVA': '#004CFF', 
        'Banorte': '#00C851'
    }
    
    for i, banco in enumerate(bancos):
        if i < len(columns):
            with columns[i]:
                st.markdown(f"<h4 style='color: {banco_colors_wc.get(banco, '#ffffff')};'>🏦 {banco}</h4>", 
                           unsafe_allow_html=True)
                
                banco_reviews = reviews_df[reviews_df['banco'] == banco]['texto']
                if len(banco_reviews) > 0:
                    # Combinar todas las reseñas del banco
                    all_text = ' '.join(banco_reviews.astype(str))
                    # Filtrar palabras mayores a 3 caracteres
                    filtered_text = filter_words(all_text)
                    
                    if len(filtered_text) > 10:
                        try:
                            # Crear wordcloud con el color del banco
                            wordcloud = WordCloud(
                                width=400, 
                                height=300, 
                                background_color='black',
                                colormap='viridis',
                                max_words=50,
                                relative_scaling=0.5,
                                min_word_length=4
                            ).generate(filtered_text)
                            
                            # Mostrar wordcloud
                            fig_wc, ax_wc = plt.subplots(figsize=(5, 4))
                            ax_wc.imshow(wordcloud, interpolation='bilinear')
                            ax_wc.axis('off')
                            ax_wc.set_facecolor('black')
                            fig_wc.patch.set_facecolor('black')
                            st.pyplot(fig_wc)
                            
                            # Mostrar las 5 palabras más frecuentes
                            word_freq = wordcloud.words_
                            if word_freq:
                                top_words = list(word_freq.keys())[:5]
                                st.write(f"**Top palabras:** {', '.join(top_words)}")
                        except Exception as e:
                            st.write(f"No hay suficientes palabras únicas para generar wordcloud")
                    else:
                        st.write("No hay suficiente texto para generar wordcloud")
                else:
                    st.write("No hay reseñas disponibles para este banco")
    
    # Tabla de mejores y peores reseñas
    st.subheader("🏆 Top Reseñas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🌟 Reseñas Más Positivas:**")
        top_positive = reviews_df.nlargest(5, 'sentiment_score')[['banco', 'nombre_sucursal', 'texto', 'sentiment_score']]
        st.dataframe(top_positive, use_container_width=True)
    
    with col2:
        st.write("**💔 Reseñas Más Negativas:**")
        top_negative = reviews_df.nsmallest(5, 'sentiment_score')[['banco', 'nombre_sucursal', 'texto', 'sentiment_score']]
        st.dataframe(top_negative, use_container_width=True)

def show_competition_analysis(df, competencia_df, analyzer):
    """Muestra análisis de competencia"""
    st.header("🎯 Análisis de Competencia y Distancias")
    
    if competencia_df is None:
        st.warning("⚠️ No hay datos de competencia disponibles")
        return
    
    # Merge de datos
    df_comp = df.merge(competencia_df, on=['place_id', 'banco'], how='left')
    
    # Métricas de competencia
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_competitors = df_comp['total_competidores'].mean()
        st.metric("🏢 Competidores Promedio", f"{avg_competitors:.1f}")
    
    with col2:
        avg_distance = df_comp['competidor_mas_cercano'].mean()
        st.metric("📏 Distancia Promedio al Competidor", f"{avg_distance:.2f} km")
    
    with col3:
        avg_advantage = df_comp['ventaja_rating'].mean()
        st.metric("⭐ Ventaja Rating Promedio", f"{avg_advantage:.2f}")
    
    # Análisis por banco
    col1, col2 = st.columns(2)
    
    with col1:
        # Competidores por banco
        fig_comp = px.box(
            df_comp.dropna(),
            x='banco',
            y='total_competidores',
            title="Distribución de Competidores por Banco",
            color='banco',
            color_discrete_map=analyzer.banco_colors
        )
        st.plotly_chart(fig_comp, use_container_width=True)
    
    with col2:
        # Ventaja rating vs competencia
        df_comp_clean = df_comp.dropna()
        if not df_comp_clean.empty:
            fig_advantage = px.scatter(
                df_comp_clean,
                x='total_competidores',
                y='ventaja_rating',
                color='banco',
                size='rating',
                title="Ventaja en Rating vs Número de Competidores",
                color_discrete_map=analyzer.banco_colors,
                hover_data={'nombre_x': True, 'alcaldia': True}
            )
            fig_advantage.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig_advantage, use_container_width=True)
        else:
            st.warning("⚠️ No hay datos suficientes para el análisis de ventaja competitiva")
    
    # Análisis de saturación por alcaldía
    st.subheader("🌆 Saturación del Mercado por Alcaldía")
    
    saturacion = df_comp.groupby('alcaldia').agg({
        'total_competidores': 'mean',
        'competidor_mas_cercano': 'mean',
        'ventaja_rating': 'mean'
    }).round(2)
    
    # Gráfico de saturación
    fig_saturacion = px.bar(
        saturacion.reset_index(),
        x='alcaldia',
        y='total_competidores',
        title="Nivel de Competencia Promedio por Alcaldía",
        color='total_competidores',
        color_continuous_scale='Reds'
    )
    fig_saturacion.update_xaxes(tickangle=45)
    st.plotly_chart(fig_saturacion, use_container_width=True)
    
    # Insights de competencia
    st.subheader("💡 Insights de Competencia")
    
    # Zonas más competitivas
    zonas_competitivas = saturacion.nlargest(3, 'total_competidores')
    zonas_menos_competitivas = saturacion.nsmallest(3, 'total_competidores')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="insight-box">
            <h4>🔥 Zonas Más Competitivas</h4>
        </div>
        """, unsafe_allow_html=True)
        for alcaldia, data in zonas_competitivas.iterrows():
            st.write(f"• **{alcaldia}**: {data['total_competidores']:.1f} competidores promedio")
    
    with col2:
        st.markdown("""
        <div class="insight-box">
            <h4>🌱 Oportunidades de Expansión</h4>
        </div>
        """, unsafe_allow_html=True)
        for alcaldia, data in zonas_menos_competitivas.iterrows():
            st.write(f"• **{alcaldia}**: {data['total_competidores']:.1f} competidores promedio")

def show_interactive_maps(df, reviews_df):
    """Muestra mapas interactivos"""
    st.header("🗺️ Mapas Interactivos")
    
    # Mapa de sucursales con ratings
    st.subheader("📍 Mapa de Sucursales por Rating")
    
    # Crear mapa base
    center_lat = df['lat'].mean()
    center_lon = df['lng'].mean()
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11)
    
    # Añadir marcadores por banco
    colors = {'Santander': 'red', 'BBVA': 'blue', 'Banorte': 'green'}
    
    for _, row in df.iterrows():
        color = colors.get(row['banco'], 'gray')
        
        # Popup con información
        popup_html = f"""
        <div style="width: 200px;">
            <h4>{row['nombre']}</h4>
            <p><b>Banco:</b> {row['banco']}</p>
            <p><b>Rating:</b> {row['rating']} ⭐</p>
            <p><b>Reseñas:</b> {row['total_reviews']}</p>
            <p><b>Alcaldía:</b> {row['alcaldia']}</p>
        </div>
        """
        
        folium.Marker(
            location=[row['lat'], row['lng']],
            popup=folium.Popup(popup_html, max_width=250),
            icon=folium.Icon(color=color, icon='bank', prefix='fa'),
            tooltip=f"{row['banco']} - {row['nombre']}"
        ).add_to(m)
    
    # Mostrar mapa
    map_data = st_folium(m, width=700, height=500)
    
    # Análisis de densidad
    st.subheader("🔥 Análisis de Densidad")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Densidad por alcaldía
        density = df['alcaldia'].value_counts()
        fig_density = px.bar(
            x=density.index,
            y=density.values,
            title="Densidad de Sucursales por Alcaldía",
            labels={'x': 'Alcaldía', 'y': 'Número de Sucursales'}
        )
        fig_density.update_xaxes(tickangle=45)
        st.plotly_chart(fig_density, use_container_width=True)
    
    with col2:
        # Mapa de calor de ratings
        if not reviews_df.empty:
            rating_by_alcaldia = reviews_df.groupby('alcaldia')['sentiment_score'].mean()
            fig_heat = px.bar(
                x=rating_by_alcaldia.index,
                y=rating_by_alcaldia.values,
                title="Sentimiento Promedio por Alcaldía",
                labels={'x': 'Alcaldía', 'y': 'Sentimiento Promedio'},
                color=rating_by_alcaldia.values,
                color_continuous_scale='RdYlGn'
            )
            fig_heat.update_xaxes(tickangle=45)
            st.plotly_chart(fig_heat, use_container_width=True)

def show_advanced_insights(df, reviews_df, competencia_df, analyzer):
    """Muestra insights avanzados"""
    st.header("📈 Insights Avanzados")
    
    # Correlación entre variables
    st.subheader("🔗 Análisis de Correlaciones")
    
    # Preparar datos para correlación
    numeric_cols = ['rating', 'total_reviews']
    if competencia_df is not None:
        df_analysis = df.merge(competencia_df, on=['place_id', 'banco'], how='left')
        numeric_cols.extend(['total_competidores', 'competidor_mas_cercano', 'ventaja_rating'])
    else:
        df_analysis = df.copy()
    
    # Matriz de correlación
    corr_matrix = df_analysis[numeric_cols].corr()
    
    fig_corr = px.imshow(
        corr_matrix,
        title="Matriz de Correlación",
        color_continuous_scale='RdBu',
        aspect='auto'
    )
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # Análisis predictivo
    st.subheader("🔮 Análisis Predictivo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Relación entre número de reseñas y rating
        fig_scatter = px.scatter(
            df,
            x='total_reviews',
            y='rating',
            color='banco',
            size='total_reviews',
            title="Relación Reseñas vs Rating",
            color_discrete_map=analyzer.banco_colors,
            trendline="ols"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col2:
        # Análisis de outliers
        fig_box = px.box(
            df,
            y='rating',
            title="Detección de Outliers en Ratings",
            points="outliers"
        )
        st.plotly_chart(fig_box, use_container_width=True)
    
    # Recomendaciones estratégicas
    st.subheader("💡 Recomendaciones Estratégicas")
    
    recommendations = []
    
    # Análizar datos para generar recomendaciones
    best_alcaldia = df.groupby('alcaldia')['rating'].mean().idxmax()
    worst_alcaldia = df.groupby('alcaldia')['rating'].mean().idxmin()
    
    recommendations.append(f"🏆 **Mejor alcaldía por rating**: {best_alcaldia}")
    recommendations.append(f"⚠️ **Alcaldía con menor rating**: {worst_alcaldia} - Oportunidad de mejora")
    
    if competencia_df is not None:
        low_competition = competencia_df.groupby('banco')['total_competidores'].mean().idxmin()
        recommendations.append(f"🎯 **Banco con menor competencia promedio**: {low_competition}")
    
    if not reviews_df.empty:
        most_positive_bank = reviews_df.groupby('banco')['sentiment_score'].mean().idxmax()
        recommendations.append(f"😊 **Banco con mejor sentimiento en reseñas**: {most_positive_bank}")
    
    # Mostrar recomendaciones
    for rec in recommendations:
        st.markdown(f"- {rec}")
    
    # Exportar resultados
    st.subheader("📤 Exportar Análisis")
    
    if st.button("📊 Generar Reporte Completo"):
        # Crear reporte en formato dict para JSON
        report = {
            'timestamp': datetime.now().isoformat(),
            'resumen_general': {
                'total_sucursales': len(df),
                'total_reseñas': len(reviews_df) if not reviews_df.empty else 0,
                'rating_promedio': df['rating'].mean(),
                'bancos_analizados': df['banco'].unique().tolist()
            },
            'analisis_sentimientos': {
                'sentimientos': reviews_df['sentiment_category'].value_counts().to_dict() if not reviews_df.empty else {},
                'sentimiento_promedio_por_banco': reviews_df.groupby('banco')['sentiment_score'].mean().to_dict() if not reviews_df.empty else {}
            },
            'recomendaciones': recommendations
        }
        
        # Convertir a JSON
        report_json = json.dumps(report, indent=2, ensure_ascii=False)
        
        # Botón de descarga
        st.download_button(
            label="💾 Descargar Reporte JSON",
            data=report_json,
            file_name=f"reporte_analisis_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        )
        
        st.success("✅ Reporte generado exitosamente!")

def show_deep_insights(df, reviews_df, competencia_df, analyzer):
    """Muestra análisis profundo con gráficas avanzadas"""
    st.header("🔍 Deep Insights - Análisis Profundo")
    
    # Gráficos de análisis temporal
    st.subheader("📅 Análisis Temporal y Tendencias")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Análisis de distribución de ratings
        fig_dist = px.histogram(
            df, 
            x='rating', 
            color='banco',
            title="Distribución de Ratings por Banco",
            color_discrete_map=analyzer.banco_colors,
            nbins=20
        )
        fig_dist.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_color='#00d4ff'
        )
        st.plotly_chart(fig_dist, use_container_width=True)
    
    with col2:
        # Violin plot de ratings
        fig_violin = px.violin(
            df,
            y='rating',
            x='banco',
            color='banco',
            title="Distribución Detallada de Ratings",
            color_discrete_map=analyzer.banco_colors
        )
        fig_violin.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_color='#00d4ff'
        )
        st.plotly_chart(fig_violin, use_container_width=True)
    

    
    # Análisis de outliers
    st.subheader("🚨 Detección de Anomalías")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Outliers en ratings
        q1 = df['rating'].quantile(0.25)
        q3 = df['rating'].quantile(0.75)
        iqr = q3 - q1
        outliers_rating = df[(df['rating'] < q1 - 1.5*iqr) | (df['rating'] > q3 + 1.5*iqr)]
        
        st.markdown("""
        <div class="highlight-card">
            <h4>⭐ Outliers en Rating</h4>
            <h2>{}</h2>
            <p>Sucursales con ratings anómalos</p>
        </div>
        """.format(len(outliers_rating)), unsafe_allow_html=True)
    
    with col2:
        # Outliers en reseñas
        q1_rev = df['total_reviews'].quantile(0.25)
        q3_rev = df['total_reviews'].quantile(0.75)
        iqr_rev = q3_rev - q1_rev
        outliers_reviews = df[(df['total_reviews'] < q1_rev - 1.5*iqr_rev) | (df['total_reviews'] > q3_rev + 1.5*iqr_rev)]
        
        st.markdown("""
        <div class="success-card">
            <h4>💬 Outliers en Reseñas</h4>
            <h2>{}</h2>
            <p>Sucursales con actividad atípica</p>
        </div>
        """.format(len(outliers_reviews)), unsafe_allow_html=True)
    
    with col3:
        # Sucursales perfectas
        perfect_rating = df[df['rating'] == 5.0]
        
        st.markdown("""
        <div class="success-card">
            <h4>🌟 Rating Perfecto</h4>
            <h2>{}</h2>
            <p>Sucursales con 5.0 estrellas</p>
        </div>
        """.format(len(perfect_rating)), unsafe_allow_html=True)
    
    # Análisis de performance por alcaldía
    st.subheader("🏆 Ranking de Performance")
    
    performance = df.groupby(['alcaldia', 'banco']).agg({
        'rating': 'mean',
        'total_reviews': 'sum',
        'nombre': 'count'
    }).round(2)
    performance.columns = ['Rating_Promedio', 'Total_Reseñas', 'Num_Sucursales']
    performance['Score_Compuesto'] = (performance['Rating_Promedio'] * 0.4 + 
                                     np.log1p(performance['Total_Reseñas']) * 0.3 + 
                                     performance['Num_Sucursales'] * 0.3)
    
    top_performance = performance.nlargest(10, 'Score_Compuesto').reset_index()
    
    fig_performance = px.bar(
        top_performance,
        x='Score_Compuesto',
        y='alcaldia',
        color='banco',
        title="Top 10 Combinaciones Alcaldía-Banco por Performance",
        color_discrete_map=analyzer.banco_colors,
        orientation='h'
    )
    fig_performance.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_color='#00d4ff',
        height=500
    )
    st.plotly_chart(fig_performance, use_container_width=True)

def show_executive_report(df, reviews_df, competencia_df, analyzer):
    """Muestra reporte ejecutivo completo"""
    st.header("📋 Reporte Ejecutivo - Dashboard CEO")
    
    # KPIs principales
    st.subheader("📊 KPIs Estratégicos")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        market_share = df.groupby('banco').size()
        leader = market_share.idxmax()
        leader_share = (market_share.max() / market_share.sum() * 100)
        
        st.markdown(f"""
        <div class="success-card">
            <h4>👑 Líder de Mercado</h4>
            <h3>{leader}</h3>
            <p>{leader_share:.1f}% market share</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_rating_leader = df[df['banco'] == leader]['rating'].mean()
        best_quality = df.groupby('banco')['rating'].mean().idxmax()
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>⭐ Mejor Calidad</h4>
            <h3>{best_quality}</h3>
            <p>{df[df['banco'] == best_quality]['rating'].mean():.2f} rating</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_market = len(df)
        growth_opportunity = 16 - len(df['alcaldia'].unique())  # 16 alcaldías total
        
        st.markdown(f"""
        <div class="highlight-card">
            <h4>📈 Oportunidad</h4>
            <h3>{growth_opportunity}</h3>
            <p>Alcaldías sin cobertura completa</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if not reviews_df.empty:
            customer_satisfaction = (reviews_df['sentiment_category'] == 'Positivo').mean() * 100
            
            st.markdown(f"""
            <div class="success-card">
                <h4>😊 Satisfacción</h4>
                <h3>{customer_satisfaction:.1f}%</h3>
                <p>Reseñas positivas</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col5:
        if competencia_df is not None:
            high_competition = len(competencia_df[competencia_df['total_competidores'] >= 3])
            total_with_comp = len(competencia_df)
            saturation = (high_competition / total_with_comp * 100) if total_with_comp > 0 else 0
            
            st.markdown(f"""
            <div class="highlight-card">
                <h4>🎯 Saturación</h4>
                <h3>{saturation:.1f}%</h3>
                <p>Zonas altamente competidas</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Mapa estratégico
    st.subheader("🗺️ Mapa Estratégico de Oportunidades")
    
    # Análisis de gaps y oportunidades
    alcaldias_all = ['Álvaro Obregón', 'Azcapotzalco', 'Benito Juárez', 'Coyoacán',
                     'Cuajimalpa', 'Cuauhtémoc', 'Gustavo A. Madero', 'Iztacalco',
                     'Iztapalapa', 'Magdalena Contreras', 'Miguel Hidalgo', 'Milpa Alta',
                     'Tláhuac', 'Tlalpan', 'Venustiano Carranza', 'Xochimilco']
    
    coverage_analysis = []
    for alcaldia in alcaldias_all:
        for banco in ['Santander', 'BBVA', 'Banorte']:
            sucursales = len(df[(df['alcaldia'] == alcaldia) & (df['banco'] == banco)])
            avg_rating = df[(df['alcaldia'] == alcaldia) & (df['banco'] == banco)]['rating'].mean()
            coverage_analysis.append({
                'alcaldia': alcaldia,
                'banco': banco,
                'sucursales': sucursales,
                'rating_promedio': avg_rating if not pd.isna(avg_rating) else 0,
                'oportunidad': 'Alta' if sucursales == 0 else 'Media' if sucursales < 2 else 'Baja'
            })
    
    coverage_df = pd.DataFrame(coverage_analysis)
    
    # Crear heatmap de oportunidades
    pivot_oportunidades = coverage_df.pivot(index='alcaldia', columns='banco', values='sucursales')
    
    fig_heat_oport = px.imshow(
        pivot_oportunidades.fillna(0),
        title="Mapa de Presencia por Alcaldía y Banco",
        color_continuous_scale='Viridis',
        aspect='auto'
    )
    fig_heat_oport.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_color='#00d4ff',
        height=600
    )
    st.plotly_chart(fig_heat_oport, use_container_width=True)
    
    # Recomendaciones estratégicas
    st.subheader("💡 Recomendaciones Estratégicas")
    
    # Encontrar oportunidades de expansión
    gaps = coverage_df[coverage_df['sucursales'] == 0].groupby('banco').size()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="insight-box">
            <h4>🎯 Oportunidades de Expansión</h4>
        </div>
        """, unsafe_allow_html=True)
        
        for banco in gaps.index:
            gap_count = gaps[banco]
            st.write(f"• **{banco}**: {gap_count} alcaldías sin presencia")
        
        # Top alcaldías sin cobertura
        no_coverage = coverage_df[coverage_df['sucursales'] == 0]['alcaldia'].value_counts()
        if not no_coverage.empty:
            st.write("**Alcaldías con mayores gaps:**")
            for alcaldia, count in no_coverage.head(3).items():
                st.write(f"• {alcaldia}: {count} bancos ausentes")
    
    with col2:
        st.markdown("""
        <div class="insight-box">
            <h4>⚠️ Áreas de Mejora</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Bancos con ratings más bajos
        low_ratings = df.groupby('banco')['rating'].mean().sort_values()
        st.write("**Bancos por mejorar calidad:**")
        for banco, rating in low_ratings.items():
            st.write(f"• {banco}: {rating:.2f} ⭐")
        
        # Alcaldías con baja satisfacción
        if not reviews_df.empty:
            low_satisfaction = reviews_df.groupby('alcaldia')['sentiment_score'].mean().nsmallest(3)
            st.write("**Alcaldías con menor satisfacción:**")
            for alcaldia, score in low_satisfaction.items():
                st.write(f"• {alcaldia}: {score:.2f}")
    

    
    # Exportar reporte ejecutivo
    st.subheader("📤 Exportar Reporte Ejecutivo")
    
    if st.button("📊 Generar Reporte CEO", key="executive_report"):
        executive_summary = {
            'fecha_reporte': datetime.now().isoformat(),
            'market_leader': {
                'banco': leader,
                'market_share': f"{leader_share:.1f}%"
            },
            'quality_leader': {
                'banco': best_quality,
                'rating': f"{df[df['banco'] == best_quality]['rating'].mean():.2f}"
            },
            'expansion_opportunities': gaps.to_dict(),
            'customer_satisfaction': f"{customer_satisfaction:.1f}%" if not reviews_df.empty else "N/A",
            'market_saturation': f"{saturation:.1f}%" if competencia_df is not None else "N/A",
            'recommendations': [
                f"Expandir {banco} en {count} alcaldías" for banco, count in gaps.items()
            ]
        }
        
        report_json = json.dumps(executive_summary, indent=2, ensure_ascii=False)
        
        st.download_button(
            label="💾 Descargar Reporte CEO",
            data=report_json,
            file_name=f"reporte_ejecutivo_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        )
        
        st.success("✅ Reporte ejecutivo generado exitosamente!")

if __name__ == "__main__":
    main() 