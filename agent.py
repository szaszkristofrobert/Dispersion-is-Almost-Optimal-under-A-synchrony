class Agent:
    def __init__(self, id, node_position):
        self.id = id
        self.node_position = node_position # Alpha in the paper
        self.pin = 0 # Port number the agent used to enter the node, 0 if it hasn't moved yet
        self.pout = 0 # Port number the agent will use to exit the node, 0 if it hasn't moved yet

    def move_to_node(self, new_node_position, new_pin, new_pout):
        self.node_position = new_node_position
        self.pin = new_pin
        self.pout = new_pout