import streamlit as st
import pandas as pd

def cargar_datos():
    try:
        df = pd.read_csv('data/matricula_senescyt_2015_2023.csv')
        # Limpiar espacios en blanco
        df['carrera'] = df['carrera'].str.strip()
        df['universidad'] = df['universidad'].str.strip()
        df['provincia'] = df['provincia'].str.strip()
        return df
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return pd.DataFrame()

def inicializar_estado():
    if 'pregunta_actual' not in st.session_state:
        st.session_state.pregunta_actual = 0
    if 'respuestas' not in st.session_state:
        st.session_state.respuestas = {}
    if 'mostrar_resultados' not in st.session_state:
        st.session_state.mostrar_resultados = False
    if 'categoria_seleccionada' not in st.session_state:
        st.session_state.categoria_seleccionada = None

def obtener_preguntas():
    return [
        {
            'id': 'work_environment',
            'pregunta': '¿En qué tipo de entorno te ves trabajando?',
            'opciones': [
                {'label': 'Oficina o entorno corporativo', 'pesos': {'business': 3, 'tech': 2, 'health': 1}},
                {'label': 'Campo abierto o trabajo en terreno', 'pesos': {'engineering': 3, 'agriculture': 3, 'science': 2}},
                {'label': 'Laboratorio o centro de investigación', 'pesos': {'science': 3, 'health': 2, 'tech': 2}},
                {'label': 'Espacios creativos o estudios', 'pesos': {'arts': 3, 'design': 3, 'communication': 2}}
            ]
        },
        {
            'id': 'social_interaction',
            'pregunta': '¿Cómo prefieres interactuar en tu trabajo?',
            'opciones': [
                {'label': 'Trabajo independiente y concentrado', 'pesos': {'tech': 3, 'science': 2, 'arts': 2}},
                {'label': 'Colaboración constante en equipo', 'pesos': {'business': 2, 'engineering': 2, 'education': 3}},
                {'label': 'Atención directa a personas', 'pesos': {'health': 3, 'education': 3, 'social': 3}},
                {'label': 'Liderazgo y gestión de grupos', 'pesos': {'business': 3, 'management': 3, 'law': 2}}
            ]
        },
        {
            'id': 'task_type',
            'pregunta': '¿Qué tipo de tareas te resultan más atractivas?',
            'opciones': [
                {'label': 'Análisis de datos y resolución técnica', 'pesos': {'tech': 3, 'science': 2, 'engineering': 2}},
                {'label': 'Diseño y creación de contenido', 'pesos': {'arts': 3, 'design': 3, 'communication': 3}},
                {'label': 'Trabajo manual y construcción', 'pesos': {'engineering': 3, 'agriculture': 2, 'health': 1}},
                {'label': 'Planificación y toma de decisiones', 'pesos': {'business': 3, 'management': 3, 'law': 2}}
            ]
        },
        {
            'id': 'interest_area',
            'pregunta': '¿Qué área te apasiona más?',
            'opciones': [
                {'label': 'Tecnología y sistemas digitales', 'pesos': {'tech': 3, 'engineering': 1}},
                {'label': 'Negocios y emprendimiento', 'pesos': {'business': 3, 'management': 2}},
                {'label': 'Ciencia e investigación', 'pesos': {'science': 3, 'health': 1}},
                {'label': 'Arte y expresión creativa', 'pesos': {'arts': 3, 'design': 2, 'communication': 1}},
                {'label': 'Salud y bienestar', 'pesos': {'health': 3, 'social': 2}},
                {'label': 'Construcción e infraestructura', 'pesos': {'engineering': 3, 'agriculture': 1}}
            ]
        },
        {
            'id': 'motivation',
            'pregunta': '¿Qué te motiva principalmente en tu carrera profesional?',
            'opciones': [
                {'label': 'Innovar y crear cosas nuevas', 'pesos': {'tech': 3, 'engineering': 2, 'design': 2}},
                {'label': 'Resolver problemas complejos', 'pesos': {'science': 3, 'tech': 2, 'law': 2}},
                {'label': 'Ayudar y servir a otros', 'pesos': {'health': 3, 'education': 3, 'social': 3}},
                {'label': 'Generar impacto social', 'pesos': {'social': 3, 'education': 2, 'law': 2}},
                {'label': 'Crecimiento económico y estabilidad', 'pesos': {'business': 3, 'management': 2}}
            ]
        },
        {
            'id': 'skills',
            'pregunta': '¿Cuál consideras tu mayor fortaleza?',
            'opciones': [
                {'label': 'Pensamiento lógico y matemático', 'pesos': {'tech': 3, 'science': 2, 'engineering': 2}},
                {'label': 'Creatividad e imaginación', 'pesos': {'arts': 3, 'design': 3, 'communication': 2}},
                {'label': 'Comunicación y persuasión', 'pesos': {'communication': 3, 'business': 2, 'law': 2}},
                {'label': 'Empatía y comprensión', 'pesos': {'health': 3, 'education': 3, 'social': 3}},
                {'label': 'Organización y planificación', 'pesos': {'management': 3, 'business': 2}}
            ]
        }
    ]

def obtener_categorias():
    return {
        'tech': {
            'nombre': 'Tecnología e Informática',
            'keywords': ['software', 'sistemas', 'informática', 'computación', 'tecnología', 'tics'],
            'descripcion': 'Desarrollo de software, análisis de sistemas y soluciones tecnológicas'
        },
        'engineering': {
            'nombre': 'Ingeniería y Construcción',
            'keywords': ['ingeniería civil', 'ingeniería mecánica', 'ingeniería industrial', 'ingeniería eléctrica', 'arquitectura', 'construcción'],
            'descripcion': 'Diseño, construcción y mantenimiento de infraestructura'
        },
        'business': {
            'nombre': 'Negocios y Administración',
            'keywords': ['administración', 'marketing', 'comercio', 'finanzas', 'contabilidad', 'empresas', 'negocios'],
            'descripcion': 'Gestión empresarial, estrategia comercial y finanzas'
        },
        'health': {
            'nombre': 'Salud y Medicina',
            'keywords': ['medicina', 'enfermería', 'odontología', 'nutrición', 'salud'],
            'descripcion': 'Cuidado de la salud y bienestar de las personas'
        },
        'science': {
            'nombre': 'Ciencias Exactas y Naturales',
            'keywords': ['biología', 'química', 'física', 'matemáticas', 'biotecnología', 'ciencias'],
            'descripcion': 'Investigación científica y desarrollo del conocimiento'
        },
        'arts': {
            'nombre': 'Artes y Humanidades',
            'keywords': ['artes', 'música', 'literatura', 'historia', 'humanidades'],
            'descripcion': 'Expresión artística y cultural'
        },
        'education': {
            'nombre': 'Educación y Pedagogía',
            'keywords': ['pedagogía', 'educación', 'docencia', 'enseñanza'],
            'descripcion': 'Formación y enseñanza de nuevas generaciones'
        },
        'social': {
            'nombre': 'Ciencias Sociales',
            'keywords': ['trabajo social', 'sociología', 'antropología', 'psicología'],
            'descripcion': 'Comprensión y mejora de la sociedad'
        },
        'communication': {
            'nombre': 'Comunicación y Medios',
            'keywords': ['comunicación', 'periodismo', 'publicidad', 'relaciones públicas'],
            'descripcion': 'Información, medios y estrategias comunicacionales'
        },
        'law': {
            'nombre': 'Derecho y Ciencias Jurídicas',
            'keywords': ['derecho', 'jurisprudencia', 'ciencias políticas', 'legal'],
            'descripcion': 'Sistema legal y justicia'
        },
        'management': {
            'nombre': 'Gestión y Gerencia',
            'keywords': ['gestión', 'gerencia', 'administración pública'],
            'descripcion': 'Dirección y administración organizacional'
        },
        'design': {
            'nombre': 'Diseño',
            'keywords': ['diseño gráfico', 'diseño industrial', 'diseño de interiores', 'diseño'],
            'descripcion': 'Creación y desarrollo de productos visuales'
        },
        'agriculture': {
            'nombre': 'Ciencias Agrícolas',
            'keywords': ['agronomía', 'agropecuaria', 'veterinaria', 'agricultura'],
            'descripcion': 'Producción agrícola y cuidado animal'
        }
    }

def calcular_resultados(respuestas, preguntas):
    categorias = obtener_categorias()
    scores = {cat: 0 for cat in categorias.keys()}
    
    for pregunta_id, opcion_idx in respuestas.items():
        pregunta = next(p for p in preguntas if p['id'] == pregunta_id)
        pesos = pregunta['opciones'][opcion_idx]['pesos']
        
        for categoria, peso in pesos.items():
            scores[categoria] += peso

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
    max_score = max(scores.values()) if scores.values() else 1
    
    resultados = []
    for categoria, score in sorted_scores:
        info_categoria = categorias[categoria]
        resultados.append({
            'categoria': categoria,
            'nombre': info_categoria['nombre'],
            'descripcion': info_categoria['descripcion'],
            'keywords': info_categoria['keywords'],
            'score': score,
            'porcentaje': int((score / max_score) * 100)
        })
    
    return resultados

def limpiar_datos_universidades(df):

    universidades_validas = {
        'Escuela Politécnica Nacional': ['Pichincha'],
        'Universidad Central del Ecuador': ['Pichincha'],
        'Universidad de Guayaquil': ['Guayas'],
        'Universidad de Cuenca': ['Azuay'],
        'Escuela Superior Politécnica del Litoral': ['Guayas'],
        'Universidad de las Fuerzas Armadas': ['Pichincha', 'Sangolquí'],
        'Universidad Técnica de Ambato': ['Tungurahua'],
        'Universidad Técnica de Manabí': ['Manabí'],
        'Universidad Nacional de Loja': ['Loja'],
        'Universidad Estatal de Milagro': ['Guayas'],
        'Universidad Técnica del Norte': ['Imbabura'],
        'Universidad Técnica de Machala': ['El Oro'],
        'Universidad Laica Eloy Alfaro de Manabí': ['Manabí'],
        'Universidad Estatal de Bolívar': ['Bolívar'],
        'Universidad Nacional de Chimborazo': ['Chimborazo'],
        'Universidad Técnica de Cotopaxi': ['Cotopaxi'],
        'Universidad Técnica de Babahoyo': ['Los Ríos'],
        'Escuela Superior Politécnica de Chimborazo': ['Chimborazo'],
        'Escuela Superior Politécnica Agropecuaria de Manabí': ['Manabí'],
        'Universidad San Francisco de Quito': ['Pichincha'],
        'Pontificia Universidad Católica del Ecuador': ['Pichincha'],
        'Universidad de las Américas': ['Pichincha'],
        'Universidad Internacional del Ecuador': ['Pichincha'],
        'Universidad de Especialidades Espíritu Santo': ['Guayas'],
        'Universidad Católica de Santiago de Guayaquil': ['Guayas'],
        'Universidad Casa Grande': ['Guayas'],
        'Universidad del Azuay': ['Azuay'],
        'Universidad Católica de Cuenca': ['Azuay'],
        'Universidad de Especialidades Turísticas': ['Pichincha'],
        'Universidad Tecnológica Equinoccial': ['Pichincha'],
        'Universidad Tecnológica Indoamérica': ['Pichincha', 'Tungurahua'],
        'Universidad Israel': ['Pichincha'],
        'Universidad Iberoamericana del Ecuador': ['Pichincha'],
        'Universidad Técnica Particular de Loja': ['Loja', 'Azuay', 'Guayas', 'Pichincha', 'El Oro'],
    }

    df_limpio = []
    for _, row in df.iterrows():
        universidad = row['universidad']
        provincia = row['provincia']

        if universidad in universidades_validas:
            if provincia in universidades_validas[universidad]:
                df_limpio.append(row)
        else:
            df_limpio.append(row)
    
    return pd.DataFrame(df_limpio)

def obtener_universidades(df, keywords):
    mask = df['carrera'].str.lower().apply(
        lambda x: any(keyword.lower() in x for keyword in keywords)
    )
    carreras_filtradas = df[mask]

    carreras_filtradas = limpiar_datos_universidades(carreras_filtradas)

    if not carreras_filtradas.empty:
        año_reciente = carreras_filtradas['año'].max()
        carreras_filtradas = carreras_filtradas[carreras_filtradas['año'] >= año_reciente - 1]

    universidades = []
    for (universidad, provincia) in carreras_filtradas.groupby(['universidad', 'provincia']).groups.keys():
        datos_uni = carreras_filtradas[
            (carreras_filtradas['universidad'] == universidad) & 
            (carreras_filtradas['provincia'] == provincia)
        ]

        carreras_list = datos_uni['carrera'].unique().tolist()
        total_estudiantes = datos_uni['num_estudiantes'].sum()
        
        universidades.append({
            'nombre': universidad,
            'provincia': provincia,
            'carreras': carreras_list,
            'total_estudiantes': total_estudiantes
        })

    universidades.sort(key=lambda x: (len(x['carreras']), x['total_estudiantes']), reverse=True)
    
    return universidades[:20] 

def mostrar_quiz():

    st.title(" Test de Orientación Vocacional")

    inicializar_estado()
 
    df = cargar_datos()
    if df.empty:
        st.error("No se pudieron cargar los datos del CSV")
        return
    
    preguntas = obtener_preguntas()

    if st.session_state.categoria_seleccionada:
        categoria = st.session_state.categoria_seleccionada
        
        if st.button("⬅️ Volver a resultados"):
            st.session_state.categoria_seleccionada = None
            st.rerun()
        
        st.header(f"🏛️ {categoria['nombre']}")
        st.write(categoria['descripcion'])
        
        st.divider()
        st.subheader("Universidades que ofrecen estas carreras")
        
        universidades = obtener_universidades(df, categoria['keywords'])
        
        if universidades:
            for uni in universidades:
                with st.expander(f"📍 {uni['nombre']} - {uni['provincia']} ({len(uni['carreras'])} carrera{'s' if len(uni['carreras']) > 1 else ''})"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**📌 Ubicación:** {uni['provincia']}")
                    with col2:
                        st.metric("Estudiantes", f"{uni['total_estudiantes']:,}")
                    
                    st.divider()
                    st.write("** Carreras disponibles:**")
                    for carrera in uni['carreras']:
                        st.write(f"• {carrera}")
        else:
            st.info("No se encontraron universidades para esta categoría en la base de datos.")
        
        return
    
    # Mostrar resultados
    if st.session_state.mostrar_resultados:
        resultados = calcular_resultados(st.session_state.respuestas, preguntas)
        
        st.success("✅ Test completado")
        st.subheader("Tus Resultados")
        st.write("Basado en tus respuestas, estas son las áreas profesionales que mejor se ajustan a tu perfil.")
        
        st.divider()
        
        for i, resultado in enumerate(resultados, 1):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"### #{i} {resultado['nombre']}")
                st.write(resultado['descripcion'])
                st.progress(resultado['porcentaje'] / 100)
            
            with col2:
                st.metric("Compatibilidad", f"{resultado['porcentaje']}%")
            
            if st.button(f"🏛️ Ver universidades", key=f"btn_{resultado['categoria']}"):
                st.session_state.categoria_seleccionada = resultado
                st.rerun()
            
            st.divider()
        
        if st.button("🔄 Realizar test nuevamente"):
            st.session_state.pregunta_actual = 0
            st.session_state.respuestas = {}
            st.session_state.mostrar_resultados = False
            st.rerun()
        
        return
    
    # Mostrar preguntas
    pregunta_actual = preguntas[st.session_state.pregunta_actual]
    total_preguntas = len(preguntas)
    
    # Barra de progreso
    progreso = (st.session_state.pregunta_actual + 1) / total_preguntas
    st.progress(progreso)
    st.caption(f"Pregunta {st.session_state.pregunta_actual + 1} de {total_preguntas}")
    
    st.divider()
    
    # Pregunta
    st.subheader(f" {pregunta_actual['pregunta']}")
    
    # Opciones
    respuesta = st.radio(
        "Selecciona una opción:",
        range(len(pregunta_actual['opciones'])),
        format_func=lambda x: pregunta_actual['opciones'][x]['label'],
        key=f"pregunta_{pregunta_actual['id']}",
        index=st.session_state.respuestas.get(pregunta_actual['id'], None)
    )
    
    st.session_state.respuestas[pregunta_actual['id']] = respuesta
    
    st.divider()
    
    # Botones de navegación
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.session_state.pregunta_actual > 0:
            if st.button("⬅️ Anterior"):
                st.session_state.pregunta_actual -= 1
                st.rerun()
    
    with col3:
        if st.session_state.pregunta_actual < total_preguntas - 1:
            if st.button("Siguiente ➡️"):
                st.session_state.pregunta_actual += 1
                st.rerun()
        else:
            if st.button("✅ Ver Resultados"):
                st.session_state.mostrar_resultados = True
                st.rerun()

# Para ejecutar directamente este archivo
if __name__ == "__main__":
    mostrar_quiz()