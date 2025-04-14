import pandas as pd
import networkx as nx
from supervisado import PredecirTrafico
from nosupervisado import AgruparParadas


def crear_grafo_ruta(df, num_ruta):
    G = nx.DiGraph(name=f"Ruta {num_ruta}")
    for idx, row in df.iterrows():
        G.add_node(row['parada'], id=row['id'], ubicacion=row['ubicacion'], ruta=num_ruta)
    for i in range(len(df) - 1):
        origen = df.iloc[i]['parada']
        destino = df.iloc[i + 1]['parada']
        G.add_edge(origen, destino, weight=1, ruta=num_ruta)
    return G

def encontrar_mejor_ruta(rutas_grafos, origen, destino):
    resultados = {}
    for num_ruta, G in rutas_grafos.items():
        nodos_origen = [n for n in G.nodes if origen.lower() in n.lower()]
        nodos_destino = [n for n in G.nodes if destino.lower() in n.lower()]
        if not nodos_origen or not nodos_destino:
            continue
        origen_actual = nodos_origen[0]
        destino_actual = nodos_destino[0]
        try:
            path = nx.shortest_path(G, source=origen_actual, target=destino_actual, weight='weight')
            num_paradas = len(path)
            tiempo_estimado = (len(path) - 1) * 3
            resultados[num_ruta] = {
                'camino': path,
                'num_paradas': len(path),
                'tiempo_estimado': tiempo_estimado
            }
        except nx.NetworkXNoPath:
            continue
    return resultados

def main():
    archivos = {
        '37': 'ruta37.csv',
        '28': 'ruta28.csv'
    }

    rutas_dfs = {}
    rutas_grafos = {}

    for num_ruta, archivo in archivos.items():
        try:
            df = pd.read_csv(archivo)
            rutas_dfs[num_ruta] = df
            rutas_grafos[num_ruta] = crear_grafo_ruta(df, num_ruta)
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {archivo}")
            return


    print("\nBienvenido al sistema de rutas de Ibagué-Tolima")

    # MODELO NO SUPERVISADO
    # Agrupamiento no supervisado para sugerir destino
    agrupador = AgruparParadas(archivos)
    agrupador.cargar_datos()
    agrupador.entrenar_modelo()

    destino_input = input("Ingrese una parada de destino: ")
    sugerencias = agrupador.sugerir_similares(destino_input)

    if not sugerencias:
        print("No se encontraron paradas similares.")
        return

    print("\nParadas sugeridas (agrupadas por el modelo no supervisado):")
    for idx, parada in enumerate(sugerencias, 1):
        print(f"{idx}. [{parada['id']}] {parada['parada']} - Ruta {parada['ruta']}")

    # Permitir al usuario seleccionar una
    while True:
        try:
            seleccion = int(input("\nSeleccione el número del destino deseado: "))
            if 1 <= seleccion <= len(sugerencias):
                destino = sugerencias[seleccion - 1]['parada']
                break
            else:
                print("Número fuera de rango.")
        except ValueError:
            print("Por favor, ingrese un número válido.")

    origen = input("Ingrese la parada de origen: ")

    resultados = encontrar_mejor_ruta(rutas_grafos, origen, destino)

    if not resultados:
        print("\nError: No se encontró ninguna ruta que conecte estas paradas.")
        return

    print("\nResultados de la búsqueda:")
    for num_ruta, info in resultados.items():
        print(f"\nRuta {num_ruta}:")
        print(f"Número de paradas: {info['num_paradas']}")
        print(f"Tiempo estimado (modelo supervisado): {info['tiempo_estimado']} minutos")
        print("Recorrido:")
        for i, parada in enumerate(info['camino']):
            nodo_id = rutas_grafos[num_ruta].nodes[parada]['id']
            print(f"{i+1}. [{nodo_id}] {parada}")

    mejor_ruta = min(resultados.items(), key=lambda x: x[1]['num_paradas'])[0]

    print(f"\n*** La ruta más rápida es la Ruta {mejor_ruta} con {resultados[mejor_ruta]['num_paradas']} paradas ***")
    print(f"*** Tiempo estimado: {resultados[mejor_ruta]['tiempo_estimado']} minutos ***")

    # Inicializa el modelo
    modelo = PredecirTrafico()

# Después de encontrar las rutas posibles...
    for num_ruta, info in resultados.items():
        estado_trafico = modelo.predecir(origen, destino, num_ruta)
        print(f"\nRuta {num_ruta}:")
        print(f"Estado del tráfico: {estado_trafico}")

if __name__ == "__main__":
    main()