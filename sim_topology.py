import matplotlib.pyplot as plt
import random
from graph import Graph

# --- TOPOLÓGIA GENERÁTOROK ---
def create_line_graph(num_nodes):
    g = Graph()
    for i in range(1, num_nodes + 1):
        g.add_node(i, x=i * 10, y=10)
    for i in range(1, num_nodes):
        g.add_edge(i, i + 1)
    return g

def create_ring_graph(num_nodes):
    g = create_line_graph(num_nodes)
    g.add_edge(num_nodes, 1)
    return g

def create_star_graph(num_nodes):
    g = Graph()
    g.add_node(1, x=50, y=50) # Központ
    for i in range(2, num_nodes + 1):
        g.add_node(i, x=i * 10, y=10)
        g.add_edge(1, i)
    return g

def create_grid_graph(rows, cols):
    g = Graph()
    num_nodes = rows * cols
    for i in range(1, num_nodes + 1):
        g.add_node(i, x=i * 10, y=10)
    for r in range(rows):
        for c in range(cols):
            node_id = r * cols + c + 1
            if c < cols - 1: g.add_edge(node_id, node_id + 1)
            if r < rows - 1: g.add_edge(node_id, node_id + cols)
    return g

# --- SZIMULÁCIÓ FUTTATÁSA ---
def run_topology_simulation(graph_generator, *args):
    """Létrehozza a gráfot, lerak 15 ágenst SZÉTSZÓRVA, és mér."""
    g = graph_generator(*args)
    agent_count = 15

    # "General" (Szétszórt) felállás:
    # A 15 ágenst 5 különböző csomópontra (1-től 5-ig) osztjuk el
    for i in range(agent_count):
        start_node = (i % 5) + 1
        g.add_agent(node_position=start_node)

    step_count = 0
    while True:
        res = g.step_graph()
        step_count += 1

        if res == "DISPERSION_FINISHED":
            break
        if step_count > 3000:
            print(f"  [!] Megszakítva: túl sok lépés (Végtelen ciklus gyanúja).")
            break

    return step_count

def run_topology_benchmark():
    print("--- Topológiai Érzékenységvizsgálat indítása (k=15, Szétszórt indítás) ---")

    num_nodes = 20 # 15 ágensnek 20 helyet adunk
    results = {}

    results['Vonal (Line)'] = run_topology_simulation(create_line_graph, num_nodes)
    print(f"  Vonalgráf kész: {results['Vonal (Line)']} lépés")

    results['Gyűrű (Ring)'] = run_topology_simulation(create_ring_graph, num_nodes)
    print(f"  Gyűrűgráf kész: {results['Gyűrű (Ring)']} lépés")

    results['Rács (Grid 4x5)'] = run_topology_simulation(create_grid_graph, 4, 5)
    print(f"  Rácsgráf kész: {results['Rács (Grid 4x5)']} lépés")

    results['Csillag (Star)'] = run_topology_simulation(create_star_graph, num_nodes)
    print(f"  Csillaggráf kész: {results['Csillag (Star)']} lépés")

    # --- Oszlopdiagram rajzolása ---
    topologies = list(results.keys())
    steps = list(results.values())

    plt.figure(figsize=(10, 6))
    colors = ['#e63946', '#f4a261', '#2a9d8f', '#264653']
    bars = plt.bar(topologies, steps, color=colors, width=0.6)

    plt.title('Diszperzió sebessége különböző topológiákon (Szétszórt Indítás)', fontsize=14)
    plt.xlabel('Gráf Típusa (20 csomóponttal, k=15 ágens)', fontsize=12)
    plt.ylabel('Szükséges lépések száma', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval + 1, int(yval), ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.savefig('topology_results.png', dpi=300, bbox_inches='tight')
    print("\nEredmény mentve: 'topology_results.png'")
    plt.show()

if __name__ == "__main__":
    run_topology_benchmark()