import pandas as pd
import numpy as np
import os

class DataManager:
    def __init__(self):
        self.df_matricula = None
        self.df_ofertas = None
        self.df_inec = None

    def load_data(self, file_matricula, file_ofertas, file_inec, path='data/'):
        """Carga los datos desde CSVs."""
        try:
            self.df_matricula = pd.read_csv(os.path.join(path, file_matricula))
            self.df_ofertas = pd.read_csv(os.path.join(path, file_ofertas))
            self.df_inec = pd.read_csv(os.path.join(path, file_inec))
            return True
        except Exception as e:
            print(f"Error cargando datos: {e}")
            return False

    def process_and_merge(self):
        """Procesa y fusiona los dataframes."""
        if self.df_matricula is None: return None

        # 1. Agrupar Estudiantes
        df_est = self.df_matricula.groupby('carrera')['num_estudiantes'].sum().reset_index()
        df_est['key'] = df_est['carrera'].str.lower().str.strip()

        # 2. Agrupar Ofertas
        self.df_ofertas['salario_oferta'] = (self.df_ofertas['salario_minimo'] + self.df_ofertas['salario_maximo']) / 2
        df_off = self.df_ofertas.groupby('carrera_requerida').agg({
            'titulo_puesto': 'count',
            'salario_oferta': 'mean'
        }).reset_index()
        df_off.rename(columns={'titulo_puesto': 'num_ofertas'}, inplace=True)
        df_off['key'] = df_off['carrera_requerida'].str.lower().str.strip()

        # 3. Mapeo de Sectores (CRÍTICO: Debe coincidir con NLP)
        def _mapear_sector(carrera):
            c = str(carrera).lower()
            if 'sistemas' in c or 'software' in c or 'informática' in c or 'computación' in c: return 'Información y Comunicación'
            elif 'administración' in c or 'contabilidad' in c or 'financ' in c or 'marketing' in c or 'comercio' in c or 'negocios' in c: return 'Actividades Financieras'
            elif 'medicina' in c or 'enfermería' in c or 'salud' in c or 'odont' in c: return 'Salud Humana'
            elif 'civil' in c or 'arquitectura' in c or 'construcción' in c: return 'Construcción'
            elif 'mecánica' in c or 'industrial' in c or 'eléctrica' in c: return 'Industrias Manufactureras'
            elif 'educación' in c or 'docencia' in c or 'pedagogía' in c: return 'Educación'
            elif 'agro' in c or 'veterinaria' in c or 'agrónom' in c: return 'Agricultura y Ganadería'
            else: return 'Actividades Profesionales'

        df_est['sector_economico'] = df_est['carrera'].apply(_mapear_sector)

        # 4. Merges
        df_master = pd.merge(df_est, df_off, on='key', how='left')
        
        # Merge con INEC (Opcional para salarios de referencia)
        if self.df_inec is not None:
             # Limpieza básica INEC
            df_inec_clean = self.df_inec[self.df_inec['nivel_educacion'] == 'Educación Superior Universitaria']
            df_inec_agg = df_inec_clean.groupby('sector_economico').agg({
                'tasa_empleo_formal': 'mean',
                'salario_promedio_mensual': 'mean'
            }).reset_index()
            # Left join para no perder carreras
            df_master = pd.merge(df_master, df_inec_agg, on='sector_economico', how='left')

        # 5. Limpieza Final
        df_master['num_ofertas'] = df_master['num_ofertas'].fillna(0)
        # Rellenar salarios vacíos con el del INEC o el promedio global
        promedio_global = df_master['salario_oferta'].mean()
        df_master['salario_oferta'] = df_master['salario_oferta'].fillna(df_master['salario_promedio_mensual'])
        df_master['salario_oferta'] = df_master['salario_oferta'].fillna(promedio_global)
        
        df_master['tasa_empleo_formal'] = df_master['tasa_empleo_formal'].fillna(50.0)

        return df_master