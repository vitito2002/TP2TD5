import json
import networkx as nx
import matplotlib.pyplot as plt

def main():
    filename = "instances/toy_instance.json"
    #filename = "instances/retiro-tigre-semana.json"  # Comentado para utilizar solo una instancia de prueba por vez

    with open(filename) as json_file:
        data = json.load(json_file)

    # Crear un grafo dirigido
    G = nx.DiGraph()

    # Iterar sobre los servicios en los datos
    for service_id, service_info in data["services"].items():
        previous_stop = None

        for stop in service_info["stops"]:
            station = stop["station"]
            time = stop["time"]
            event = stop["type"]
            node_label = (station, time, event)

            # Añadir nodo al grafo
            G.add_node(node_label)

            # Añadir arista desde el nodo anterior al actual si existe un nodo anterior
            if previous_stop:
                G.add_edge(previous_stop, node_label, weight=0, type='trip')

            # Actualizar previous_stop al nodo actual
            previous_stop = node_label

    # Agregar aristas de traspaso y de trasnoche
    add_transfer_and_overnight_edges(G)

    # Dibujar el grafo con aristas coloreadas
    pos = nx.spring_layout(G)  # Posiciones de los nodos
    edge_colors = [data['type'] for _, _, data in G.edges(data=True)]
    edge_color_map = {'trip': 'green', 'transfer': 'black', 'overnight': 'red'}

    nx.draw(G, pos, with_labels=True, node_size=500, node_color="skyblue", font_size=10, font_weight="bold", arrows=True,
            edge_color=[edge_color_map[color] for color in edge_colors])
    labels = {node: f"{node[0]}\n{node[1]}\n{node[2]}" for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=8)

    # Mostrar el grafo
    plt.show()

def add_transfer_and_overnight_edges(G):
    stations = set(node[0] for node in G.nodes())

    for station in stations:
        # Obtener los nodos en la misma estación y ordenarlos por tiempo
        events = [node for node in G.nodes() if node[0] == station]
        events.sort(key=lambda x: x[1])

        # Agregar aristas de traspaso entre eventos en la misma estación
        for i in range(len(events) - 1):
            G.add_edge(events[i], events[i + 1], weight=0, type='transfer')

        # Arista de trasnoche (del último evento del día al primer evento del día siguiente)
        if events:
            G.add_edge(events[-1], events[0], weight=1, type='overnight')

if __name__ == "__main__":
    main()
