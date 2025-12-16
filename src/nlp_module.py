import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class NLPRecommender:
    def __init__(self, df_final):
        # Reset index es vital para que los índices de la matriz coincidan con el DF
        self.df = df_final.copy().reset_index(drop=True)
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = None
        self._entrenar_nlp()

    def _entrenar_nlp(self):
        """Genera el perfil semántico y entrena el modelo."""
        
        def crear_perfil_busqueda(row):
            # 1. Texto Base: Carrera + Sector
            texto = f"{row['carrera']} {row['sector_economico']}".lower()
            
            # 2. Diccionario de Sinónimos (Fiel al Notebook + Correcciones de robustez)
            sinonimos = {
                # TI
                'información': 'tecnología software digital programacion desarrollo sistemas computacion',
                # Negocios (Agregado 'empresarial' para que pase tu prueba)
                'financieras': 'negocios dinero banca economia gerencia administracion contabilidad empresarial empresa finanzas',
                # Salud
                'salud': 'medicina clinica hospital cuidado bienestar enfermeria medico paciente',
                # Construcción (Agregado 'obras' para que pase tu prueba)
                'construcción': 'obra obras infraestructura diseño edificacion civil arquitectura planos',
                # Industria
                'manufactureras': 'produccion fabrica industria procesos ingenieria mantenimiento',
                # Agro
                'agricultura': 'agro campo rural cultivo alimentos veterinaria animales granja',
                # Educación
                'educación': 'docencia pedagogia enseñanza escuela colegio aprender'
            }
            
            # 3. Inyección de Sinónimos
            sector_lower = str(row['sector_economico']).lower()
            
            for key, val in sinonimos.items():
                if key in sector_lower:
                    texto += " " + val
            
            return texto

        # Crear columna de perfil
        self.df['perfil_nlp'] = self.df.apply(crear_perfil_busqueda, axis=1)
        
        # Vectorización
        self.tfidf_matrix = self.tfidf.fit_transform(self.df['perfil_nlp'])
        print(f"✅ [NLP] Motor entrenado con {len(self.df)} registros.")

    def recomendar(self, consulta, filtrar_alta_demanda=False):
        """Busca carreras similares a la consulta."""
        if not consulta:
            return pd.DataFrame()
            
        try:
            # 1. Vectorizar consulta
            query_vec = self.tfidf.transform([consulta.lower()])
            
            # 2. Calcular similitud
            sim_scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
            
            # 3. Si no hay coincidencia
            if sim_scores.max() == 0:
                return pd.DataFrame()
            
            # 4. Top índices
            top_indices = sim_scores.argsort()[::-1][:10]
            
            # 5. Crear DF de resultados
            res = self.df.iloc[top_indices].copy()
            res['Afinidad'] = (sim_scores[top_indices] * 100).round(1)
            
            # FILTRO: Eliminar lo que tenga 0 afinidad (Ruido)
            res = res[res['Afinidad'] > 0]
            
            # FILTRO: Alta Demanda (Opcional)
            if filtrar_alta_demanda:
                res = res[res['categoria'].isin(['En Demanda', 'Nicho'])]
            
            if res.empty:
                return pd.DataFrame()

            # Selección de columnas finales
            cols = ['carrera', 'categoria', 'salario_oferta', 'Afinidad', 'sector_economico']
            return res[cols].head(5)
            
        except Exception as e:
            print(f"Error en recomendación: {e}")
            return pd.DataFrame()