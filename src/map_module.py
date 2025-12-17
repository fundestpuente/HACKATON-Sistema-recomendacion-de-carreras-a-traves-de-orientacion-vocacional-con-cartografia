# map_module.py
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Coordenadas aproximadas de las capitales de provincia
COORDENADAS_ECUADOR = {
    'Pichincha': {'lat': -0.1807, 'lon': -78.4678}, 
    'Guayas': {'lat': -2.1894, 'lon': -79.8891},    
    'Azuay': {'lat': -2.9001, 'lon': -79.0059},     
    'Manabí': {'lat': -1.0546, 'lon': -80.4544},    
    'Loja': {'lat': -3.9931, 'lon': -79.2042},      
    'Tungurahua': {'lat': -1.2491, 'lon': -78.6168},
    'Imbabura': {'lat': 0.3517, 'lon': -78.1223},   
    'El Oro': {'lat': -3.2581, 'lon': -79.9551},    
    'Chimborazo': {'lat': -1.6636, 'lon': -78.6546},
    'Cotopaxi': {'lat': -0.9349, 'lon': -78.6146},  
    'Esmeraldas': {'lat': 0.9682, 'lon': -79.6517}, 
    'Los Ríos': {'lat': -1.8022, 'lon': -79.5344},  
    'Bolívar': {'lat': -1.5905, 'lon': -79.0024},   
    'Carchi': {'lat': 0.8119, 'lon': -77.7173},     
    'Cañar': {'lat': -2.7402, 'lon': -78.8461},     
    'Pastaza': {'lat': -1.4924, 'lon': -77.9992},   
    'Napo': {'lat': -0.9938, 'lon': -77.8129},      
    'Morona Santiago': {'lat': -2.3089, 'lon': -78.1114}, 
    'Zamora Chinchipe': {'lat': -4.0692, 'lon': -78.9515}, 
    'Sucumbíos': {'lat': 0.0847, 'lon': -76.8828},  
    'Orellana': {'lat': -0.4665, 'lon': -76.9896},  
    'Santo Domingo de los Tsáchilas': {'lat': -0.2536, 'lon': -79.1759},
    'Santa Elena': {'lat': -2.2262, 'lon': -80.8587},
    'Galápagos': {'lat': -0.7402, 'lon': -90.3134}
}

def normalizar_texto(texto):
    """Limpia tildes y mayúsculas para asegurar coincidencias"""
    if not isinstance(texto, str): return ""
    texto = texto.lower().strip()
    replacements = (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n"))
    for a, b in replacements:
        texto = texto.replace(a, b)
    return texto

def generar_mapa_oferta(df, keywords_categoria, nombre_categoria):
    """
    Genera un mapa Plotly filtrando universidades.
    """
    st.subheader(f"🗺️ Mapa de Oportunidades: {nombre_categoria}")
    st.markdown("Ubicación de universidades con mayor oferta académica en tu área de interés.")

    if df is None or df.empty:
        st.error("No hay datos para generar el mapa.")
        return

    # 1. Copia y limpieza
    df_map = df.copy()
    df_map.columns = df_map.columns.str.lower().str.strip()
    rename_dict = {'nombre_ies': 'universidad', 'nombre_provincia': 'provincia', 'nombre_carrera': 'carrera'}
    df_map.rename(columns=rename_dict, inplace=True)
    
    # 2. Filtrar
    mask = df_map['carrera'].astype(str).str.lower().apply(
        lambda x: any(k.lower() in x for k in keywords_categoria)
    )
    df_filtrado = df_map[mask]

    if df_filtrado.empty:
        st.warning("No se encontraron universidades con esa oferta específica en la base de datos.")
        return

    # 3. Agrupar por Provincia
    map_data = []
    
    for provincia, grupo in df_filtrado.groupby('provincia'):
        prov_norm = None
        for p_key in COORDENADAS_ECUADOR.keys():
            if normalizar_texto(p_key) in normalizar_texto(provincia):
                prov_norm = p_key
                break
        
        if prov_norm:
            coords = COORDENADAS_ECUADOR[prov_norm]
            total_est = grupo['num_estudiantes'].sum() if 'num_estudiantes' in grupo.columns else 0
            
            top_unis = grupo['universidad'].value_counts().head(3).index.tolist()
            unis_str = "<br>".join([f"• {u}" for u in top_unis])
            
            map_data.append({
                'Provincia': prov_norm,
                'lat': coords['lat'],
                'lon': coords['lon'],
                'Estudiantes': total_est,
                'Universidades Destacadas': unis_str,
                # AHORA SÍ FUNCIONA PORQUE np YA ESTÁ IMPORTADO GLOBALMENTE
                'Oferta_Size': np.log(total_est + 1) * 5 
            })
            
    if not map_data:
        st.warning("No se pudieron geolocalizar las provincias de la oferta académica.")
        return

    df_plot = pd.DataFrame(map_data)
    
    # 4. Generar Mapa
    fig = px.scatter_mapbox(
        df_plot,
        lat="lat",
        lon="lon",
        size="Oferta_Size",
        color="Estudiantes",
        hover_name="Provincia",
        hover_data={"Universidades Destacadas": True, "lat": False, "lon": False, "Oferta_Size": False},
        color_continuous_scale=px.colors.sequential.Viridis,
        zoom=5.5,
        center={"lat": -1.8312, "lon": -78.1834},
        title=f"Concentración de oferta para: {nombre_categoria}"
    )

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    
    st.plotly_chart(fig, use_container_width=True)