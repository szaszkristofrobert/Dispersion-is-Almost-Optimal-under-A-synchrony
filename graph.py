from node import Node
from agent import Agent
import json
import random

class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.agents = []

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
            self.nodes[node1_number].edges[len(self.nodes[node1_number].edges)] = node2_number
            self.nodes[node2_number].edges[len(self.nodes[node2_number].edges)] = node1_number

    def print_graph(self):
        print("Nodes:")
        for node_number, node in self.nodes.items():
            print(f"  Node {node_number}: ({node.x}, {node.y})")
            print(f"    Neighbors: {node.neighbors}")
            print(f"    Ports: {node.edges}")
        print("Edges:")
        for edge in self.edges:
            print(f"  Edge between Node {edge[0]} and Node {edge[1]}")
        print("Agents:")
        for agent in self.agents:
            print(f"  Agent {agent.id} at Node {agent.node_position}")

    def clear_graph(self):
        self.nodes = {}
        self.edges = []
        self.agents = []

    def save_graph(self, filename):
        graph_data = {
            'nodes': {num: {'x': node.x, 'y': node.y} for num, node in self.nodes.items()},
            'edges': self.edges,
            'agents': [{'id': agent.id, 'node_position': agent.node_position} for agent in self.agents]
        }
        with open(f"graphs/{filename}.json", 'w') as f:
            json.dump(graph_data, f, indent=2)
        print(f"Saving graph to {filename}.json")

    def load_graph(self, filename):

        self.clear_graph()

        with open(f"graphs/{filename}.json", 'r') as f:
            graph_data = json.load(f)

        self.nodes = {int(num): Node(int(num), data['x'], data['y']) for num, data in graph_data['nodes'].items()}
        for edge in graph_data['edges']:
            self.add_edge(int(edge[0]), int(edge[1]))

        if 'agents' in graph_data:
            self.agents = [Agent(agent['id'], int(agent['node_position'])) for agent in graph_data['agents']]

        print(f"Loaded graph from {filename}.json")

    def max_degree(self):
        if not self.nodes:
            return 0
        return max(node.degree() for node in self.nodes.values())

    def move_agent(self, agent, port_number):
        current_node = self.nodes[int(agent.node_position)]
        new_pout = port_number
        new_node_position = current_node.edges[new_pout]

        new_node = self.nodes[int(new_node_position)]
        new_pin = 0
        for pin in new_node.edges:
            if int(new_node.edges[pin]) == int(agent.node_position):
                new_pin = pin
                break

        agent.move_to_node(new_node_position, new_pin, new_pout)

    def step_graph(self):
        # Move each agent to the neighbor with port number 1
        for agent in self.agents:
            current_node = self.nodes[int(agent.node_position)]
            if current_node.neighbors:
                self.move_agent(agent, 1)