import sys
import networkx as nx
from graph import Graph
import random as r

def parse_graph(graph_raw, agent_num):
    graph = Graph()

    for node in graph_raw.nodes:
        graph.add_node(int(node), None, None)

    for edge in graph_raw.edges:
        graph.add_edge(edge[0], edge[1])

    for _i in range(agent_num):
        graph.add_agent(0)

    return graph

def run(n, p, a, seed):
    print(f"Run started n = {n}, p = {p}, a = {a}, seed = {seed}")
    graph_raw = nx.fast_gnp_random_graph(n, p, seed)
    print("Graph generated.")

    graph = parse_graph(graph_raw, a)
    print("Graph parsed.")

    algo_status = ""
    round_counter = 0

    while algo_status != "DISPERSION_FINISHED":
        algo_status = graph.step_graph()
        
        if algo_status == "NO_AGENTS":
            print("No agents on the graph. Invalid run.")
            break

        if algo_status == "NOT ROOTED":
            print("Configuratin not rooted. Invalid run.")
            break

        round_counter += 1

    if algo_status == "DISPERSION_FINISHED":
        print(f"Dispersion done in {str(round_counter)} rounds")

    with open("stats\stats001.csv", "a") as stats:
        stats.write(f"{n},{p},{a},{round_counter}\n")

if __name__ == "__main__":
    n = int(sys.argv[1]) # Nodeok szama
    p = float(sys.argv[2]) # Edge creation prob (Erdoes-Renyi)
    ap = float(sys.argv[3]) # Agent arany

    for i in range(n):
        if i >= 10:
            for j in range(5):
                a = int(i*ap)
                run(i, p, a, r.randrange(10000))
