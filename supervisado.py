from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

class PredecirTrafico:
    def __init__(self):
        self.modelo = RandomForestClassifier()
        self.entrenar()

    def entrenar(self):
        # Datos de entrenamiento ficticios
        datos = [
            {"origen": "Galarza", "destino": "Yuldaima", "ruta": "37", "congestion": 1},
            {"origen": "Galarza", "destino": "Yuldaima", "ruta": "28", "congestion": 0},
            {"origen": "SENA", "destino": "Comfenalco", "ruta": "28", "congestion": 0},
            {"origen": "Comfenalco", "destino": "Gaitán", "ruta": "37", "congestion": 1},
            {"origen": "La Miel", "destino": "Yuldaima", "ruta": "28", "congestion": 0},
            {"origen": "Calle 40", "destino": "Gaitán", "ruta": "37", "congestion": 1},
        ]

        X = [[hash(d["origen"]) % 1000, hash(d["destino"]) % 1000, int(d["ruta"])] for d in datos]
        y = [d["congestion"] for d in datos]

        X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2)
        self.modelo.fit(X_train, y_train)

    def predecir(self, origen, destino, ruta):
        entrada = [[hash(origen) % 1000, hash(destino) % 1000, int(ruta)]]
        resultado = self.modelo.predict(entrada)
        return "Alta congestión" if resultado[0] == 1 else "Tráfico fluido"