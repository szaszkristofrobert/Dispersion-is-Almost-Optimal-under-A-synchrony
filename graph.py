from node import Node
from agent import Agent
import json
import os


class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.agents = []
        self.phase = "INIT"
        self.target_port = None

        # Változók a UI naplózáshoz
        self.step_counter = 0
        self.action_logs = []

    def add_agent(self, node_position):
        agent = Agent(len(self.agents), node_position)
        self.agents.append(agent)

    def add_node(self, node_number, x, y):
        node = Node(node_number, x, y)
        self.nodes[node_number] = node

    def add_edge(self, node1_number, node2_number):
        if node1_number in self.nodes.keys() and node2_number in self.nodes.keys():
            self.edges.append([node1_number, node2_number])
            self.nodes[node1_number].neighbors.add(node2_number)
            self.nodes[node2_number].neighbors.add(node1_number)
            p1 = len(self.nodes[node1_number].edges)
            p2 = len(self.nodes[node2_number].edges)
            self.nodes[node1_number].edges[p1] = node2_number
            self.nodes[node2_number].edges[p2] = node1_number

    def move_agent(self, agent, port_number):
        old_node_position = agent.node_position
        current_node = self.nodes[int(agent.node_position)]
        new_node_position = current_node.edges[port_number]
        new_node = self.nodes[int(new_node_position)]

        new_pin = 0
        for pin, target in new_node.edges.items():
            if int(target) == int(agent.node_position):
                new_pin = pin
                break

        agent.move_to_node(new_node_position, new_pin, port_number)

        # Automatikus naplózás a UI-nak
        log_msg = f"[Lépés: {self.step_counter}] Ágens {agent.id} átlépett a(z) N{new_node_position} csomópontra a(z) {port_number}-es porton. (Indult: N{old_node_position})"
        self.action_logs.append(log_msg)

    def get_unsettled_neighbor_port(self, node_id, my_tree_label):
        node = self.nodes[node_id]
        sorted_ports = sorted([p for p in node.edges.keys() if p > 0])
        for port in sorted_ports:
            neighbor_id = node.edges[port]
            enemy_tree_label = getattr(self.nodes[neighbor_id], 'visited_by', None)

            if enemy_tree_label is None:
                return port, "EMPTY"
            elif enemy_tree_label != my_tree_label:
                return port, "COLLISION"
        return None, "FULL"

    def step_graph(self):
        if not self.agents: return "NO_AGENTS"

        self.step_counter += 1

        if self.phase == "INIT":
            nodes_with_agents = set(a.node_position for a in self.agents)
            for node_id in nodes_with_agents:
                team = [a for a in self.agents if a.node_position == node_id]
                team.sort(key=lambda x: x.id, reverse=True)

                leader = team[0]
                leader.is_leader = True
                tree_label = leader.id

                self.nodes[node_id].visited_by = tree_label

                k = len(team)
                num_seekers = (k + 2) // 3

                for i, agent in enumerate(team):
                    agent.tree_label = tree_label
                    if i > 0 and i <= num_seekers:
                        agent.is_seeker = True

                explorers = [a for a in team if not a.is_leader and not a.is_seeker]
                if explorers:
                    min(explorers, key=lambda x: x.id).settled = True
                    self.action_logs.append(
                        f"[Lépés: {self.step_counter}] Rendszer: Inicializálás - Ágens {min(explorers, key=lambda x: x.id).id} letelepedett az N{node_id} bázison.")
                elif len(team) > 1:
                    seekers = [a for a in team if a.is_seeker]
                    if seekers:
                        settler = min(seekers, key=lambda x: x.id)
                        settler.settled = True
                        settler.is_seeker = False
                        self.action_logs.append(
                            f"[Lépés: {self.step_counter}] Rendszer: Inicializálás - Kereső Ágens {settler.id} feláldozta magát az N{node_id} bázison.")
                else:
                    leader.settled = True
                    self.action_logs.append(
                        f"[Lépés: {self.step_counter}] Rendszer: Inicializálás - Vezér Ágens {leader.id} egyedül letelepedett az N{node_id} bázison.")

            self.phase = "PROBE_OUT"
            self.action_logs.append(
                f"[Lépés: {self.step_counter}] Rendszer: Inicializálás befejeződött. Csapatok felálltak.")
            return "INIT_DONE"

        active_leaders = [a for a in self.agents if a.is_leader and not a.settled]
        if not active_leaders:
            return "DISPERSION_FINISHED"

        if self.phase == "PROBE_OUT":
            for leader in active_leaders:
                curr_node = self.nodes[leader.node_position]
                seekers = [a for a in self.agents if
                           a.is_seeker and not a.settled and a.tree_label == leader.tree_label and a.node_position == leader.node_position]
                ports_to_check = sorted([p for p in curr_node.edges.keys() if p > 0])
                for i, seeker in enumerate(seekers):
                    if i < len(ports_to_check):
                        self.move_agent(seeker, ports_to_check[i])
                        seeker.parent_port = seeker.pin
            self.phase = "PROBE_IN"
            return "PROBING_OUT"

        elif self.phase == "PROBE_IN":
            for seeker in [a for a in self.agents if a.is_seeker and not a.settled]:
                if seeker.parent_port is not None:
                    self.move_agent(seeker, seeker.parent_port)
                    seeker.parent_port = None
            self.phase = "MOVE"
            return "PROBING_IN"

        elif self.phase == "MOVE":
            for leader in active_leaders:
                if leader.settled or not leader.is_leader: continue

                my_team = [a for a in self.agents if a.tree_label == leader.tree_label]
                target_port, status = self.get_unsettled_neighbor_port(leader.node_position, leader.tree_label)

                if status == "COLLISION":
                    target_node_id = self.nodes[leader.node_position].edges[target_port]
                    enemy_tree_label = getattr(self.nodes[target_node_id], 'visited_by', None)
                    enemy_team = [a for a in self.agents if a.tree_label == enemy_tree_label]

                    if len(my_team) > len(enemy_team) or (
                            len(my_team) == len(enemy_team) and leader.id > enemy_tree_label):
                        for a in enemy_team:
                            a.tree_label = leader.tree_label
                            a.is_leader = False
                        for n in self.nodes.values():
                            if getattr(n, 'visited_by', None) == enemy_tree_label:
                                n.visited_by = leader.tree_label
                        self.action_logs.append(
                            f"[Lépés: {self.step_counter}] Rendszer: A(z) {leader.id} fa bekebelezte a(z) {enemy_tree_label} fát!")
                    else:
                        for a in my_team:
                            a.tree_label = enemy_tree_label
                            a.is_leader = False
                        for n in self.nodes.values():
                            if getattr(n, 'visited_by', None) == leader.tree_label:
                                n.visited_by = enemy_tree_label
                        self.action_logs.append(
                            f"[Lépés: {self.step_counter}] Rendszer: A(z) {enemy_tree_label} fa bekebelezte a(z) {leader.id} fát!")
                        continue

                elif status == "EMPTY":
                    target_node_id = self.nodes[leader.node_position].edges[target_port]
                    self.nodes[target_node_id].visited_by = leader.tree_label

                    moving_group = [a for a in my_team if not a.settled and a.node_position == leader.node_position]
                    for a in moving_group:
                        self.move_agent(a, target_port)

                    leader.path_stack.append(leader.pin)

                    current_explorers = [a for a in moving_group if not a.is_leader and not a.is_seeker]
                    if current_explorers:
                        settler = min(current_explorers, key=lambda x: x.id)
                        settler.settled = True
                        self.action_logs.append(
                            f"[Lépés: {self.step_counter}] Rendszer: Felfedező Ágens {settler.id} letelepedett az N{settler.node_position} csomóponton.")

                else:
                    current_node_settlers = [a for a in my_team if
                                             a.node_position == leader.node_position and a.settled]
                    moving_group = [a for a in my_team if not a.settled and a.node_position == leader.node_position]

                    if not current_node_settlers:
                        current_seekers = [a for a in moving_group if a.is_seeker]
                        if current_seekers:
                            settler = min(current_seekers, key=lambda x: x.id)
                            settler.settled = True
                            settler.is_seeker = False
                            moving_group.remove(settler)
                            self.action_logs.append(
                                f"[Lépés: {self.step_counter}] Rendszer: Visszatöltés. Kereső Ágens {settler.id} letelepedett az N{settler.node_position} csomóponton.")
                        elif leader in moving_group:
                            leader.settled = True
                            moving_group.remove(leader)
                            self.action_logs.append(
                                f"[Lépés: {self.step_counter}] Rendszer: Visszatöltés. Vezér Ágens {leader.id} letelepedett az N{leader.node_position} csomóponton.")

                    if leader.path_stack and moving_group:
                        back_port = leader.path_stack.pop()
                        for a in moving_group:
                            self.move_agent(a, back_port)
                    elif leader in moving_group:
                        leader.settled = True

            self.phase = "PROBE_OUT"
            return "MOVED_AND_MERGED"

    def print_graph(self):
        print("Nodes:")
        for node_number, node in self.nodes.items():
            print(f"  Node {node_number}: ({node.x}, {node.y})")
        print("Agents:")
        for agent in self.agents:
            status = "Settled" if agent.settled else "Active"
            role = "Leader" if agent.is_leader else ("Seeker" if agent.is_seeker else "Explorer")
            print(f"  Agent {agent.id} (Tree: {agent.tree_label}) ({role}) at Node {agent.node_position} - {status}")

    def clear_graph(self):
        self.nodes = {}
        self.edges = []
        self.agents = []
        self.phase = "INIT"
        self.target_port = None
        self.step_counter = 0
        self.action_logs = []

    def save_graph(self, filename):
        graph_data = {
            'nodes': {num: {'x': node.x, 'y': node.y} for num, node in self.nodes.items()},
            'edges': self.edges,
            'agents': [{'id': agent.id, 'node_position': agent.node_position} for agent in self.agents]
        }
        if not os.path.exists("graphs"): os.makedirs("graphs")
        with open(f"graphs/{filename}.json", 'w') as f: json.dump(graph_data, f, indent=2)

    def load_graph(self, filename):
        self.clear_graph()
        try:
            with open(f"graphs/{filename}.json", 'r') as f:
                graph_data = json.load(f)
            self.nodes = {int(num): Node(int(num), data['x'], data['y']) for num, data in graph_data['nodes'].items()}
            for edge in graph_data['edges']: self.add_edge(int(edge[0]), int(edge[1]))
            if 'agents' in graph_data: self.agents = [Agent(agent['id'], int(agent['node_position'])) for agent in
                                                      graph_data['agents']]
        except FileNotFoundError:
            pass