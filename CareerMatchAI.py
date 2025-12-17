import streamlit as st
import pandas as pd

# --- IMPORTACIÓN DE MÓDULOS PROPIOS DEL PROYECTO ---
from src.data_manager import DataManager
from src.nlp_module import NLPRecommender
from src.clustering_module import CareerClusterer, plot_clusters_3d
from src.prediction_module import CareerPredictor
from src.eda_module import EDAModule
import src.map_module
import quizz

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="IA Recomendador de Carreras",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; color: #333; text-align: center; margin-bottom: 2rem; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; }
    .metric-card { 
        background-color: #f8f9fa; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #00CC96;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    /* Mejora visual de pestañas */
    .stTabs [data-baseweb="tab-list"] { gap: 5px; }
    .stTabs [data-baseweb="tab"] { border-radius: 5px 5px 0 0; background-color: #f0f2f6; }
    .stTabs [aria-selected="true"] { background-color: white; border-top: 2px solid #00CC96; }
</style>
""", unsafe_allow_html=True)

# --- CARGA DE DATOS Y MODELOS ---
@st.cache_resource
def load_system():
    # 1. DataManager
    dm = DataManager()
    if not dm.load_data('matricula_senescyt_2015_2023.csv', 'encuentra_empleo_ofertas_2.csv', 'inec_enemdu_salarios.csv'):
        return None, None, None, None, None, "Error cargando CSVs." # Retornamos un valor extra para EDA

    df_master = dm.process_and_merge()
    if df_master is None: return None, None, None, None, None, "Error procesando master."

    # 2. Clustering
    clusterer = CareerClusterer(df_master)
    df_labeled = clusterer.ejecutar_clustering()

    # 3. NLP
    nlp = NLPRecommender(df_labeled)

    # 4. Predictor
    predictor = CareerPredictor()
    predictor.entrenar_modelo()
    
    # 5. EDA (Inicializamos pasando los DataFrames crudos para gráficos detallados)
    eda = EDAModule(dm.df_matricula, dm.df_ofertas, dm.df_inec)

    return df_labeled, nlp, predictor, eda, "OK" # Retornamos eda

# --- INICIALIZACIÓN ---
try:
    df_final, nlp_engine, predictor_engine, eda_engine, status = load_system()
    if df_final is None:
        st.error(f"Error: {status}")
        st.stop()
except Exception as e:
    st.error(f"Error init: {e}")
    st.stop()

# --- SIDEBAR ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135768.png", width=100)
st.sidebar.title("CareerMatch AI")
opcion = st.sidebar.radio("Menú Principal:", [
    "Inicio", 
    "📊 Análisis de Mercado", 
    "🤖 Clustering (Segmentación)", 
    "🔍 Recomendador Vocacional", 
    "🔮 Simulador Futuro",
    "📝 Test Vocacional"
])
st.sidebar.markdown("---")
st.sidebar.info(f"✅ Base de Datos: {len(df_final)} carreras activas.")

# --- PÁGINA: INICIO ---
if opcion == "Inicio":
    st.markdown("<h1 class='main-header'>Orientación Vocacional con IA</h1>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("""
        <div style="background:#e6fffa; padding:20px; border-radius:15px; text-align:center; border:1px solid #00CC96;">
            <h2 style="color:#00CC96;">IA + Big Data</h2>
            <p>Datos reales de SENESCYT, INEC y Bolsas de Empleo.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.write("### ¿Cómo funciona?")
        st.write("""
        1.  **Analizamos** el mercado laboral histórico y actual.
        2.  **Agrupamos** carreras similares usando K-Means.
        3.  **Recomendamos** opciones basadas en tus intereses usando NLP.
        4.  **Predecimos** el futuro de nuevas carreras con Random Forest.
        """)

# --- PÁGINA: EDA ---
# --- SECCIÓN PESTAÑA: ANÁLISIS DE MERCADO (ACTUALIZADA FIEL AL NOTEBOOK) ---
elif opcion == "📊 Análisis de Mercado":
    st.header("Radiografía del Mercado Laboral (EDA)")
    
    # Creamos pestañas internas para organizar los gráficos del notebook
    tab1, tab2, tab3 = st.tabs(["🎓 Oferta Académica", "💼 Brecha de Talento", "💰 Salarios"])
    
    with tab1:
        st.subheader("Tendencias de Matrícula")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(eda_engine.plot_top_carreras_matricula(), use_container_width=True)
        with col2:
            st.plotly_chart(eda_engine.plot_tendencia_temporal(), use_container_width=True)
            
    with tab2:
        st.subheader("La Realidad del Mercado: Graduados vs Ofertas")
        st.markdown("""
        Este gráfico cruza la oferta académica (barras azules) con la demanda laboral real (línea roja).
        **Una brecha grande indica saturación.**
        """)
        # Este es el gráfico dual axis del notebook
        st.plotly_chart(eda_engine.plot_brecha_talento(), use_container_width=True)
        
    with tab3:
        st.subheader("Análisis Salarial")
        st.plotly_chart(eda_engine.plot_distribucion_salarios(), use_container_width=True)

# --- PÁGINA: CLUSTERING ---
elif opcion == "🤖 Clustering (Segmentación)":
    st.header("Segmentación de Mercado (K-Means)")
    st.write("La IA ha agrupado las carreras en 4 categorías según su comportamiento:")
    
    # Métricas
    conteo = df_final['categoria'].value_counts()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("En Demanda", conteo.get("En Demanda", 0))
    c2.metric("Nicho", conteo.get("Nicho", 0))
    c3.metric("Balanceada", conteo.get("Balanceada", 0))
    c4.metric("Saturada", conteo.get("Saturada", 0))
    
    # Gráfico 3D (Ahora usamos la función importada directamente)
    fig_3d = plot_clusters_3d(df_final)
    if fig_3d:
        st.plotly_chart(fig_3d, use_container_width=True)
    else:
        st.error("No se pudo generar el gráfico 3D. Verifica los datos.")
    
    # Tabla
    with st.expander("Ver tabla de datos"):
        st.dataframe(df_final[['carrera', 'categoria', 'salario_oferta', 'num_ofertas', 'sector_economico']])

# --- PÁGINA: RECOMENDADOR NLP
elif opcion == "🔍 Recomendador Vocacional":
    st.header("Buscador Semántico Inteligente")
    st.markdown("Busca por conceptos (ej: *'construcción de obras'*, *'cuidar pacientes'*, *'empresarial'*).")
    
    col_input, col_check = st.columns([3, 1])
    query = col_input.text_input("Interés:", placeholder="Escribe aquí...")
    rentables = col_check.checkbox("Solo Alta Rentabilidad")
    
    if st.button("Buscar Carrera"):
        if query:
            # Usamos el motor NLP
            resultados = nlp_engine.recomendar(query, filtrar_alta_demanda=rentables)
            
            if resultados is not None and not resultados.empty:
                st.success(f"Encontramos {len(resultados)} coincidencias:")
                
                for _, row in resultados.iterrows():
                    # Definir color según categoría
                    color = "#00CC96" if row['categoria'] == "En Demanda" else "#EF553B" if row['categoria'] == "Saturada" else "#636EFA"
                    
                    # Usamos los nombres de columna reales del DataFrame (raw names)
                    # sector_economico en lugar de Sector (INEC)
                    # salario_oferta en lugar de Salario Ref.
                    
                    st.markdown(f"""
                    <div class="metric-card" style="border-left-color: {color};">
                        <div style="display:flex; justify-content:space-between;">
                            <h4 style="margin:0;">{row['carrera']}</h4>
                            <span style="background:#333; color:white; padding:2px 8px; border-radius:10px; font-size:0.8em;">{row['Afinidad']}%</span>
                        </div>
                        <p style="color:#666; margin:0; font-size:0.9em;">{row['sector_economico']}</p> 
                        <hr style="margin:5px 0;">
                        <div style="display:flex; gap:15px; font-weight:bold; font-size:0.9em;">
                            <span style="color:{color}">🏷️ {row['categoria']}</span>
                            <span>💰 ${row['salario_oferta']:.0f}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No encontramos coincidencias. Intenta con palabras clave como 'Negocios', 'Salud', 'Construcción'.")
        else:
            st.error("Por favor escribe algo para buscar.")

# --- PÁGINA: PREDICTOR ---
elif opcion == "🔮 Simulador Futuro":
    st.header("Simulador de Viabilidad (Random Forest)")
    
    c1, c2, c3, c4 = st.columns(4)
    est = c1.number_input("Graduados/Año", 0, 20000, 5000, step=500)
    ofe = c2.number_input("Ofertas/Año", 0, 1000, 50, step=10)
    sal = c3.number_input("Salario ($)", 400, 5000, 800, step=50)
    tas = c4.slider("Estabilidad (%)", 0, 100, 50)
    
    if st.button("Predecir Categoría"):
        pred, probs = predictor_engine.predecir(est, ofe, sal, tas)
        
        colores = {
            "En Demanda": "#00CC96", "Saturada": "#EF553B", 
            "Nicho": "#636EFA", "Balanceada": "#FECB52"
        }
        color = colores.get(pred, "#333")
        
        st.markdown(f"""
        <div style="text-align:center; padding:20px; border:2px solid {color}; border-radius:10px;">
            <h2 style="color:{color}; margin:0;">{pred}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("##### Probabilidades:")
        st.bar_chart(pd.DataFrame.from_dict(probs, orient='index', columns=['%']))

# --- PÁGINA: TEST VOCACIONAL + MAPA ---
elif opcion == "📝 Test Vocacional":
    try:
        # 1. Ejecutar el Test
        quizz.mostrar_quiz()
        
        # 2. Verificar si hay resultados seleccionados para mostrar el mapa
        # Accedemos al estado de sesión que maneja 'test.py'
        if 'categoria_seleccionada' in st.session_state and st.session_state.categoria_seleccionada:
            
            st.markdown("---")
            st.header("🗺️ Geolocalización de Oferta Académica")
            
            # Obtenemos los datos necesarios del estado
            categoria = st.session_state.categoria_seleccionada
            keywords = categoria['keywords']
            nombre_cat = categoria['nombre']
            
            # Pasamos el DataFrame crudo que ya tenemos cargado (eda_engine.df_matricula)
            # Asegúrate de usar el dataframe correcto disponible en tu scope
            if 'eda_engine' in locals() and eda_engine is not None:
                 map_module.generar_mapa_oferta(eda_engine.df_matricula, keywords, nombre_cat)
            else:
                 # Fallback si eda_engine no está instanciado localmente (ej. recarga de página)
                 dm_temp = DataManager()
                 # Nota: idealmente esto ya está en caché, no debería tardar
                 if dm_temp.load_data('matricula_senescyt_2015_2023.csv', 'encuentra_empleo_ofertas_2.csv', 'inec_enemdu_salarios.csv'):
                     map_module.generar_mapa_oferta(dm_temp.df_matricula, keywords, nombre_cat)
            
    except AttributeError:
        st.error("Error: Verifica que 'test.py' y 'map_module.py' estén en la carpeta correcta.")
    except Exception as e:
        st.error(f"Ocurrió un error al cargar el módulo: {e}")