class Node:
    def __init__(self, node_number, x, y):
        self.node_number = node_number
        self.x = x
        self.y = y
        self.neighbors = set()
        self.edges = {0: node_number}

    def degree(self):
        return len(self.neighbors)