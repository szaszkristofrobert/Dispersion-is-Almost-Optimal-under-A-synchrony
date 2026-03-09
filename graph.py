from node import Node
import json

class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = []

    def add_node(self, node_number, x, y):
        node = Node(node_number, x, y)
        self.nodes[node_number] = node

    def add_edge(self, node1_number, node2_number):
        if node1_number in self.nodes.keys() and node2_number in self.nodes.keys():
            self.edges.append([node1_number, node2_number]) 

    def print_graph(self):
        print("Nodes:")
        for node_number, node in self.nodes.items():
            print(f"Node {node_number}: ({node.x}, {node.y})")
        print("Edges:")
        for edge in self.edges:
            print(f"Edge between Node {edge[0]} and Node {edge[1]}")
    
    def clear_graph(self):
        self.nodes = {}
        self.edges = []

    def save_graph(self, filename):
        graph_data = {
            'nodes': {num: {'x': node.x, 'y': node.y} for num, node in self.nodes.items()},
            'edges': self.edges
        }
        with open(f"graphs/{filename}.json", 'x') as f:
            json.dump(graph_data, f, indent=2)
        print(f"Saving graph to {filename}.json")

    def load_graph(self, filename):
        with open(f"graphs/{filename}.json", 'r') as f:
            graph_data = json.load(f)
        self.nodes = {int(num): Node(int(num), data['x'], data['y']) for num, data in graph_data['nodes'].items()}
        self.edges = graph_data['edges']
        print(f"Loaded graph from {filename}.json")