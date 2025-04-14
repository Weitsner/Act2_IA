import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder

class AgruparParadas:
    def __init__(self, archivos_rutas, n_clusters=5):
        self.archivos_rutas = archivos_rutas
        self.n_clusters = n_clusters
        self.modelo = None
        self.datos = None
        self.df_paradas = None
        self.label_rutas = LabelEncoder()

    def cargar_datos(self):
        data_frames = []
        for ruta, archivo in self.archivos_rutas.items():
            try:
                df = pd.read_csv(archivo)
                df['ruta'] = ruta
                data_frames.append(df)
            except FileNotFoundError:
                print(f"Error: No se encontró el archivo {archivo}")
        self.df_paradas = pd.concat(data_frames, ignore_index=True)

    def entrenar_modelo(self):
        self.df_paradas['ruta_cod'] = self.label_rutas.fit_transform(self.df_paradas['ruta'])
        X = self.df_paradas[['id', 'ruta_cod']]
        self.modelo = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        self.df_paradas['grupo'] = self.modelo.fit_predict(X)

    def sugerir_similares(self, parada_destino):
        # Buscar coincidencias de nombre
        match = self.df_paradas[self.df_paradas['parada'].str.lower().str.contains(parada_destino.lower())]
        if match.empty:
            print("No se encontró una parada con ese nombre.")
            return []

        grupo_objetivo = match.iloc[0]['grupo']
        sugerencias = self.df_paradas[self.df_paradas['grupo'] == grupo_objetivo]

        # Retornar lista de diccionarios con paradas del mismo grupo
        resultados = []
        for _, row in sugerencias.iterrows():
            resultados.append({
                'parada': row['parada'],
                'id': row['id'],
                'ruta': row['ruta'],
                'ubicacion': row['ubicacion']
            })
        return resultados