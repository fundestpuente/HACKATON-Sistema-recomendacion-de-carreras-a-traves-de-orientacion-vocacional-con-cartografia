import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import plotly.express as px

# --- FUNCIÓN DE VISUALIZACIÓN (FIEL AL NOTEBOOK) ---
def plot_clusters_3d(df):
    """
    Genera el gráfico 3D de clusters replicando exactamente el Notebook 02.
    """
    # Aseguramos que existan las columnas necesarias
    required = ['num_estudiantes', 'num_ofertas', 'salario_oferta', 'categoria']
    if not all(col in df.columns for col in required):
        return None

    fig = px.scatter_3d(
        df,
        x='num_estudiantes',
        y='num_ofertas',
        z='salario_oferta',
        color='categoria',
        symbol='categoria',
        hover_name='carrera',
        # Formato de hover data idéntico al notebook
        hover_data={'tasa_empleo_formal':':.1f%', 'sector_economico':True},
        title='<b>Clustering de Carreras 2025</b>',
        labels={
            'num_estudiantes': 'Total Graduados (2015-2023)',
            'num_ofertas': 'Ofertas Activas',
            'salario_oferta': 'Salario Promedio ($)'
        },
        color_discrete_map={
            "En Demanda": "#00CC96",
            "Saturadas": "#EF553B",
            "Nicho": "#636EFA",
            "Balanceadas": "#FECB52"
        },
        opacity=0.9
    )
    
    # Ajustes de Layout del notebook (fuentes pequeñas, márgenes)
    fig.update_layout(
        scene=dict(
            xaxis=dict(title=dict(font=dict(size=10)), tickfont=dict(size=9)),
            yaxis=dict(title=dict(font=dict(size=10)), tickfont=dict(size=9)),
            zaxis=dict(title=dict(font=dict(size=10)), tickfont=dict(size=9)),
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        legend=dict(title="Categoría", font=dict(size=10))
    )
    return fig

# --- CLASE DE LÓGICA DE NEGOCIO ---
class CareerClusterer:
    def __init__(self, df_master):
        self.df = df_master.copy()
        self.features = ['num_estudiantes', 'num_ofertas', 'salario_oferta', 'tasa_empleo_formal']
        self.kmeans = None

    def ejecutar_clustering(self):
        """Ejecuta K-Means y aplica etiquetas."""
        # 1. Escalar
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(self.df[self.features])
        
        # 2. Modelo (K=4)
        self.kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
        self.df['cluster'] = self.kmeans.fit_predict(X_scaled)
        
        # 3. Etiquetado Inteligente
        centroides = self.df.groupby('cluster')[self.features].mean()
        medias = self.df[self.features].mean()

        def _get_label(row, m):
            alta_demanda = row['num_ofertas'] > m['num_ofertas']
            buen_sueldo = row['salario_oferta'] > m['salario_oferta']
            empleo_estable = row['tasa_empleo_formal'] > m['tasa_empleo_formal']
            muchos_graduados = row['num_estudiantes'] > m['num_estudiantes']

            if alta_demanda and buen_sueldo: return "En Demanda"
            elif muchos_graduados and (not alta_demanda or not empleo_estable): return "Saturadas"
            elif not muchos_graduados and (buen_sueldo or empleo_estable): return "Nicho"
            else: return "Balanceada"

        mapa_labels = {i: _get_label(centroides.loc[i], medias) for i in centroides.index}
        self.df['categoria'] = self.df['cluster'].map(mapa_labels)
        
        return self.df