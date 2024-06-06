import json
import networkx as nx
import matplotlib.pyplot as plt
import math

def info_parada(stop):
    return stop["time"], stop["station"], stop["type"]

def nuevo_nodo(G, hora, estacion, tipo, demanda):
    G.add_node(
        f"{hora}_{estacion}_{tipo}",
        time=hora,
        station=estacion,
        type=tipo,
        demanda=demanda,
    )

def Grafo(data):

    G = nx.DiGraph()

    # cada servicio en data[services]
    for service_id, service_info in data["services"].items():

        # info de las dos cabeceras 
        izq_hora, izq_estacion, izq_tipo = info_parada(service_info["stops"][0])
        der_hora, der_estacion, der_tipo = info_parada(service_info["stops"][1])

        demanda = math.ceil(service_info["demand"][0] / 100)
        maximo_trenes = data["rs_info"]["max_rs"]

        # izq --> der
        if izq_tipo == "D": 
            nuevo_nodo(G, izq_hora, izq_estacion, izq_tipo, demanda)
            nuevo_nodo(G, der_hora, der_estacion, der_tipo, -demanda)
            
            G.add_edge(
                f"{izq_hora}_{izq_estacion}_{izq_tipo}",
                f"{der_hora}_{der_estacion}_{der_tipo}",
                tipo="tren",
                capacidad=maximo_trenes - demanda,
                costo=0,
            )

        # izq <-- der
        else:
            nuevo_nodo(G, izq_hora, izq_estacion, izq_tipo, -demanda)
            nuevo_nodo(G, der_hora, der_estacion, der_tipo, demanda)
            
            G.add_edge(
                f"{der_hora}_{der_estacion}_{der_tipo}",
                f"{izq_hora}_{izq_estacion}_{izq_tipo}",
                tipo="tren",
                capacidad=maximo_trenes - demanda,
                costo=0,
            )
            
    estaciones = {}

    for cabecera in G.nodes:
        estacion = G.nodes[cabecera]["station"]
        if estacion not in estaciones:
            estaciones[estacion] = []
        estaciones[estacion].append(cabecera)

    for estacion, cabeceras in estaciones.items():
        # ordena por tiempo
        nodos_ordenados = sorted(cabeceras, key=lambda nodo: G.nodes[nodo]["time"])

        for i in range(len(nodos_ordenados) - 1):
            G.add_edge(
                nodos_ordenados[i],
                nodos_ordenados[i + 1],
                tipo="traspaso",
                capacidad=float("inf"),
                costo=0,
            )
            
        G.add_edge(
            nodos_ordenados[-1],
            nodos_ordenados[0],
            tipo="trasnoche",
            capacidad=float("inf"),
            costo=1,
        )
    return G

def minimocosto(G):

    # flujo de costo minimo
    flow = nx.min_cost_flow(G, "demanda", "capacidad", "costo")
    print("hola",flow)

    # todas las aristas
    for u, v in G.edges:
        if G.edges[u, v]["tipo"] == "tren":
            # AJUSTAR FLUJO!!!
            flow[u][v] += G.nodes[u]["demanda"]
    print("chau",flow)

    return flow

def vagones_iniciales(flow_dict,estaciones):
    # Filtrar estaciones Retiro y Tigre
    estaciones_a = [key for key in flow_dict.keys() if estaciones[0] in key]
    estaciones_b = [key for key in flow_dict.keys() if estaciones[1] in key]

    nodo_estacion_a = min(estaciones_a, key=lambda x: int(x.split('_')[0]))
    nodo_estacion_b = min(estaciones_b, key=lambda x: int(x.split('_')[0]))

    vagones_estacion_a = sum(flow_dict[nodo_estacion_a].values())
    vagones_estacion_b = sum(flow_dict[nodo_estacion_b].values())

    print(f"{estaciones[0]}: {vagones_estacion_a} vagones")
    print(f"{estaciones[1]}: {vagones_estacion_b} vagones")


def main():
    filename = "instances/retiro-tigre-semana.json"  # Nombre del archivo JSON proporcionado

    with open(filename) as json_file:
        data = json.load(json_file)

    G = Grafo(data)

    flow_dict = minimocosto(G)

    for u in flow_dict:
        for v in flow_dict[u]:
            if G[u][v]["costo"] == 1:
                if u[0] == "Retiro" or v[0] == "Retiro":
                    total_units_retiro += flow_dict[u][v]
                elif u[0] == "Tigre" or v[0] == "Tigre":
                    total_units_tigre += flow_dict[u][v]
            print(f"Flow from {u} to {v}: {flow_dict[u][v]} units")
    print(flow_dict)

    estaciones = data.get("stations",[])

    vagones_iniciales(flow_dict,estaciones)

    # Dibujar el grafo con aristas coloreadas

    pos = nx.spring_layout(G)  # Posiciones de los nodos
    edge_colors = [data["tipo"] for _, _, data in G.edges(data=True)]
    edge_color_map = {"tren": "green", "traspaso": "black", "trasnoche": "red"}

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=500,
        node_color="skyblue",
        font_size=10,
        font_weight="bold",
        arrows=True,
        edge_color=[edge_color_map[color] for color in edge_colors],
    )
    labels = {node: f"{node[0]}\n{node[1]}\n{node[2]}" for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=8)

    # Mostrar el grafo

    plt.show()


if __name__ == "__main__":
    main()
