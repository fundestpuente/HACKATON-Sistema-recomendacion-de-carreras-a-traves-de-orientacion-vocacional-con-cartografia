import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

class CareerPredictor:
    def __init__(self):
        self.rf_model = None
        self.features = ['num_estudiantes', 'num_ofertas', 'salario_oferta', 'tasa_empleo_formal']

    def entrenar_modelo(self):
        """
        Entrena Random Forest usando Data Augmentation (Datos Sintéticos)
        para evitar overfitting con datasets pequeños.
        """
        def generar_datos_complejos(n=1000):
            datos, etiquetas = [], []
            
            def gen_val(media, desv, mn, mx):
                val = np.random.normal(media, desv)
                return max(mn, min(mx, int(val)))

            # Escenarios Difusos (Fuzzy Logic)
            for _ in range(n):
                # Saturada
                datos.append([gen_val(10000, 3500, 3000, 25000), gen_val(35, 25, 0, 90), gen_val(650, 200, 400, 950), gen_val(45, 12, 20, 70)])
                etiquetas.append("Saturada")
                # En Demanda
                datos.append([gen_val(2500, 1200, 800, 6000), gen_val(250, 90, 120, 600), gen_val(1600, 400, 1000, 3000), gen_val(80, 10, 55, 100)])
                etiquetas.append("En Demanda")
                # Nicho
                datos.append([gen_val(600, 300, 50, 1500), gen_val(60, 40, 10, 180), gen_val(1400, 450, 900, 2500), gen_val(70, 15, 45, 95)])
                etiquetas.append("Nicho")
                # Balanceada
                datos.append([gen_val(5000, 2000, 1500, 9000), gen_val(110, 50, 50, 250), gen_val(950, 250, 600, 1400), gen_val(60, 15, 35, 85)])
                etiquetas.append("Balanceada")
                
            return np.array(datos), np.array(etiquetas)

        X_sint, y_sint = generar_datos_complejos()
        
        # Configuración para evitar overfitting
        self.rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=6,
            min_samples_leaf=15,
            class_weight='balanced',
            random_state=42
        )
        self.rf_model.fit(X_sint, y_sint)

    def predecir(self, est, ofe, sal, tasa):
        if not self.rf_model:
            return "Modelo no entrenado", {}
            
        # DataFrame con nombres de columnas para coincidir con el entrenamiento (si se usara dataframe)
        # Como usamos numpy arrays en fit, usamos lista simple aquí, pero mantenemos orden
        data = [[est, ofe, sal, tasa]]
        
        pred = self.rf_model.predict(data)[0]
        probs = self.rf_model.predict_proba(data)[0]
        
        return pred, dict(zip(self.rf_model.classes_, probs))