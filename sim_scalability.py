import matplotlib.pyplot as plt
from graph import Graph  # Győződj meg róla, hogy a legfrissebb fájlod neve "graph"


def create_line_graph(num_nodes):
    """Létrehoz egy egyszerű vonalgráfot N csomóponttal tesztelési célra."""
    g = Graph()
    for i in range(1, num_nodes + 1):
        g.add_node(i, x=i * 10, y=10)  # Koordináták csak formaiak
    for i in range(1, num_nodes):
        g.add_edge(i, i + 1)
    return g


def run_scalability_simulation(agent_count, graph_size):
    """Lefuttat egy szimulációt a megadott ágens-számmal, 'Rooted' indítással."""
    g = create_line_graph(graph_size)

    # Minden ágenst az 1-es csomópontra rakunk (Rooted Configuration)
    for _ in range(agent_count):
        g.add_agent(node_position=1)

    step_count = 0
    while True:
        res = g.step_graph()
        step_count += 1

        if res == "DISPERSION_FINISHED":
            break
        if step_count > 2000:
            print(f"  [!] Megszakítva: túl sok lépés ({agent_count} ágens).")
            break

    return step_count


def run_scalability_benchmark():
    print("--- Skálázódási Szimuláció (Kapacitás Analízis) indítása ---")

    # A vizsgálandó ágens-számok
    agent_counts = [5, 10, 15]
    results = []

    for count in agent_counts:
        # A gráf legyen elég nagy az ágenseknek (pl. +5 csomópont biztonsági ráhagyás)
        steps = run_scalability_simulation(agent_count=count, graph_size=count + 5)
        results.append(steps)
        print(f"  Vonalgráf - {count} ágens esetén: {steps} lépés")

    # --- Grafikon rajzolása ---
    plt.figure(figsize=(8, 5))
    plt.plot(agent_counts, results, marker='o', linestyle='-', color='#1d3557', linewidth=2.5, markersize=8)

    plt.title('Skálázódás Vizsgálata Vonalgráfon (Rooted Indítás)', fontsize=14)
    plt.xlabel('Ágensek száma ($k$)', fontsize=12)
    plt.ylabel('Szükséges lépések száma', fontsize=12)
    plt.xticks(agent_counts)
    plt.grid(True, linestyle='--', alpha=0.7)

    plt.savefig('scalability_results.png', dpi=300, bbox_inches='tight')
    print("\nEredmény mentve: 'scalability_results.png'")
    plt.show()


if __name__ == "__main__":
    run_scalability_benchmark()