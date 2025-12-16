import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

class EDAModule:
    def __init__(self, df_matricula, df_ofertas, df_inec):
        self.df_matricula = df_matricula
        self.df_ofertas = df_ofertas
        self.df_inec = df_inec

    def plot_top_carreras_matricula(self):
        """Top 10 Carreras con mayor matrícula (Replica Notebook 01)"""
        if 'año' not in self.df_matricula.columns: return None
        # Filtramos último año disponible (usualmente 2023)
        anio_max = self.df_matricula['año'].max()
        df_curr = self.df_matricula[self.df_matricula['año'] == anio_max]
        
        top = df_curr.groupby('carrera')['num_estudiantes'].sum().sort_values(ascending=False).head(10).reset_index()
        
        fig = px.bar(top, x='num_estudiantes', y='carrera', orientation='h', 
                     title=f'Top 10 Carreras con Mayor Matrícula ({anio_max})',
                     color='num_estudiantes', color_continuous_scale='Viridis')
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        return fig

    def plot_tendencia_temporal(self):
        """Evolución temporal: Tradicionales vs Nuevas"""
        carreras_interes = ['Derecho', 'Desarrollo de Software', 'Medicina', 'Administración de Empresas']
        # Filtramos solo si existen en la base
        df_trend = self.df_matricula[self.df_matricula['carrera'].isin(carreras_interes)]
        
        if df_trend.empty: return None
        
        trend_data = df_trend.groupby(['año', 'carrera'])['num_estudiantes'].sum().reset_index()
        
        fig = px.line(trend_data, x='año', y='num_estudiantes', color='carrera', markers=True,
                      title='Tendencia Histórica: Carreras Tradicionales vs Tecnológicas')
        return fig

    def plot_brecha_talento(self):
        """
        GRÁFICO CRÍTICO: Doble Eje (Estudiantes vs Ofertas)
        Replica la celda 5 del Notebook 01.
        """
        # 1. Preparar Oferta Académica (Estudiantes último año)
        anio_max = self.df_matricula['año'].max()
        oferta = self.df_matricula[self.df_matricula['año'] == anio_max].groupby('carrera')['num_estudiantes'].sum().reset_index()
        oferta.rename(columns={'num_estudiantes': 'Total_Estudiantes'}, inplace=True)
        
        # 2. Preparar Demanda Laboral (Total histórico de ofertas)
        demanda = self.df_ofertas['carrera_requerida'].value_counts().reset_index()
        demanda.columns = ['carrera', 'Total_Ofertas']
        
        # 3. Merge y Top 15
        top_est = oferta.sort_values('Total_Estudiantes', ascending=False).head(15)
        df_cruce = pd.merge(top_est, demanda, on='carrera', how='left').fillna(0)
        
        # 4. Gráfico Dual Axis (Plotly Graph Objects)
        fig = go.Figure()
        
        # Barras: Estudiantes
        fig.add_trace(go.Bar(
            x=df_cruce['carrera'], 
            y=df_cruce['Total_Estudiantes'],
            name='Estudiantes (Oferta)',
            marker_color='#636EFA',
            opacity=0.7
        ))
        
        # Línea: Ofertas
        fig.add_trace(go.Scatter(
            x=df_cruce['carrera'], 
            y=df_cruce['Total_Ofertas'],
            name='Ofertas de Empleo',
            yaxis='y2',
            line=dict(color='#EF553B', width=4),
            mode='lines+markers'
        ))
        
        # Layout complejo
        fig.update_layout(
            title='<b>La Brecha de Talento</b>: Graduados vs Vacantes Reales',
            xaxis=dict(title='Carrera'),
            yaxis=dict(title='Número de Estudiantes', showgrid=False),
            yaxis2=dict(title='Número de Ofertas', overlaying='y', side='right', showgrid=False),
            legend=dict(orientation="h", y=1.1, x=0),
            height=600
        )
        return fig

    def plot_distribucion_salarios(self):
        """Histograma de salarios ofertados"""
        df = self.df_ofertas.copy()
        df['salario_promedio'] = (df['salario_minimo'] + df['salario_maximo']) / 2
        
        fig = px.histogram(df, x='salario_promedio', nbins=20, 
                           title='Distribución de Salarios Ofertados',
                           color_discrete_sequence=['#00CC96'])
        fig.update_layout(bargap=0.1)
        return fig