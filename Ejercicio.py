import pandas as pd
import networkx as nx

def crear_grafo_ruta(df, num_ruta):
    """Crea un grafo dirigido a partir de las paradas de una ruta."""
    G = nx.DiGraph(name=f"Ruta {num_ruta}")
    
    # Agregar nodos (paradas)
    for idx, row in df.iterrows():
        G.add_node(row['parada'], id=row['id'], ubicacion=row['ubicacion'], ruta=num_ruta)
    
    # Agregar aristas (conexiones entre paradas consecutivas)
    for i in range(len(df) - 1):
        origen = df.iloc[i]['parada']
        destino = df.iloc[i + 1]['parada']
        G.add_edge(origen, destino, weight=1, ruta=num_ruta)
    
    return G


def encontrar_mejor_ruta(rutas_grafos, origen, destino):
    """Encuentra la mejor ruta entre todas las disponibles."""
    resultados = {}
    
    for num_ruta, G in rutas_grafos.items():
        # Buscar coincidencias parciales para origen
        nodos_origen = [n for n in G.nodes if origen.lower() in n.lower()]
        # Buscar coincidencias parciales para destino
        nodos_destino = [n for n in G.nodes if destino.lower() in n.lower()]
        
        if not nodos_origen or not nodos_destino:
            continue
            
        # Usar el primer nodo que coincida (se podría mejorar este criterio)
        origen_actual = nodos_origen[0]
        destino_actual = nodos_destino[0]
        
        try:
            # Calcular el camino más corto
            path = nx.shortest_path(G, source=origen_actual, target=destino_actual, weight='weight')
            # Calcular el tiempo estimado (3 minutos por parada)
            tiempo_estimado = (len(path) - 1) * 3
            
            resultados[num_ruta] = {
                'camino': path,
                'num_paradas': len(path),
                'tiempo_estimado': tiempo_estimado
            }
        except nx.NetworkXNoPath:
            # No hay camino directo en esta ruta
            continue
    
    return resultados

def main():
    # Archivos de las rutas
    archivos = {
        '37': 'ruta37.csv',
        '28': 'ruta28.csv'
    }
    
    # Cargar datos de ambas rutas y crear grafos
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
    origen = input("Ingrese la parada de origen: ")
    destino = input("Ingrese la parada de destino: ")
    
    resultados = encontrar_mejor_ruta(rutas_grafos, origen, destino)
    
    if not resultados:
        print("\nError: No se encontró ninguna ruta que conecte estas paradas.")
        return

    print("\nResultados de la búsqueda:")
    for num_ruta, info in resultados.items():
        print(f"\nRuta {num_ruta}:")
        print(f"Número de paradas: {info['num_paradas']}")
        print(f"Tiempo estimado: {info['tiempo_estimado']} minutos")
        print("Recorrido:")
        for i, parada in enumerate(info['camino']):
            nodo_id = rutas_grafos[num_ruta].nodes[parada]['id']
            print(f"{i+1}. [{nodo_id}] {parada}")
    
    # Determinar la mejor ruta basada en el número de paradas
    mejor_ruta = min(resultados.items(), key=lambda x: x[1]['num_paradas'])[0]
    
    print(f"\n*** La ruta más rápida es la Ruta {mejor_ruta} con {resultados[mejor_ruta]['num_paradas']} paradas ***")
    print(f"*** Tiempo estimado: {resultados[mejor_ruta]['tiempo_estimado']} minutos ***")

if __name__ == "__main__":
    main()