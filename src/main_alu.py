import json
import networkx as nx
import matplotlib.pyplot as plt


def main():
    filename = "instances/toy_instance.json"  # Nombre del archivo JSON proporcionado


    with open(filename) as json_file:
        data = json.load(json_file)


    # Crear un grafo dirigido
    G = nx.DiGraph()
    maximo_trenes = data["rs_info"]["max_rs"]
    capacidad_vagon = data["rs_info"]["capacity"]


    # Iterar sobre los servicios en los datos
    for service_id, service_info in data["services"].items():
        previous_stop = None


        for stop in service_info["stops"]:
            station = stop["station"]
            time = stop["time"]
            event = stop["type"]
            node_label = (station, time, event)
            demanda = service_info["demand"][0]  # Obtener la demanda específica del servicio


            # Añadir nodo al grafo
            G.add_node(node_label, demand=0)


            # Añadir arista desde el nodo anterior al actual si existe un nodo anterior
            if previous_stop:
                num_vagones = demanda // capacidad_vagon  # Calcular el número de vagones necesarios
                G.add_edge(previous_stop, node_label, weight=0, capacity=maximo_trenes, lower_bound=num_vagones, type='trip', service_id=service_id)


            # Actualizar previous_stop al nodo actual
            previous_stop = node_label


    # Definir la demanda de los nodos
    define_node_demands(G, capacidad_vagon, data)


    # Agregar aristas de traspaso y de trasnoche
    add_transfer_and_overnight_edges(G, maximo_trenes)


    # Resolver el problema de flujo de costo mínimo
    flow_dict = nx.min_cost_flow(G)


    # Calcular la cantidad total de unidades necesarias
    total_units_retiro = 0
    total_units_tigre = 0
    for u in flow_dict:
        for v in flow_dict[u]:
            if G[u][v]['weight'] == 1:
                if u[0] == 'Retiro' or v[0] == 'Retiro':
                    total_units_retiro += flow_dict[u][v]
                elif u[0] == 'Tigre' or v[0] == 'Tigre':
                    total_units_tigre += flow_dict[u][v]
            print(f"Flow from {u} to {v}: {flow_dict[u][v]} units")


    print(f"Total de unidades necesarias para Retiro: {total_units_retiro}")
    print(f"Total de unidades necesarias para Tigre: {total_units_tigre}")


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


def define_node_demands(G, capacidad_vagon, data):
    """
    Define las demandas de los nodos según el problema de los trenes.
    """
    # Ajustar las demandas según la capacidad de los vagones y la demanda específica de los servicios
    for node in G.nodes():
        if node[2] == 'D':  # Nodo de salida (Departure)
            # Obtener la demanda del servicio asociado
            demanda = next(service_info['demand'][0] for service_id, service_info in data["services"].items() if (node[0], node[1], 'D') in [(stop["station"], stop["time"], stop["type"]) for stop in service_info["stops"]])
            G.nodes[node]['demand'] = demanda // capacidad_vagon  # Se necesitan tantos vagones como demanda / capacidad de vagón
        elif node[2] == 'A':  # Nodo de llegada (Arrival)
            demanda = next(service_info['demand'][0] for service_id, service_info in data["services"].items() if (node[0], node[1], 'A') in [(stop["station"], stop["time"], stop["type"]) for stop in service_info["stops"]])
            G.nodes[node]['demand'] = -demanda // capacidad_vagon  # Se completa tantos vagones como demanda / capacidad de vagón


def add_transfer_and_overnight_edges(G, maximo_trenes):
    stations = set(node[0] for node in G.nodes())


    for station in stations:
        # Obtener los nodos en la misma estación y ordenarlos por tiempo
        events = [node for node in G.nodes() if node[0] == station]
        events.sort(key=lambda x: x[1])


        # Agregar aristas de traspaso entre eventos en la misma estación
        for i in range(len(events) - 1):
            G.add_edge(events[i], events[i + 1], weight=0, capacity=maximo_trenes, type='transfer')


        # Arista de trasnoche (del último evento del día al primer evento del día siguiente)
        if events:
            G.add_edge(events[-1], events[0], weight=1, capacity=maximo_trenes, type='overnight')


if __name__ == "__main__":
    main()