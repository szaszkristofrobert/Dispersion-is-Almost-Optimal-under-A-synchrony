class Agent:
    def __init__(self, id, node_position):
        self.id = id
        self.node_position = node_position
        self.pin = 0
        self.pout = 0

        self.settled = False
        self.is_leader = False
        self.is_seeker = False
        self.parent_port = None
        self.tree_label = None

        # A Leader memóriája a visszalépéshez (verem)
        self.path_stack = []

    def move_to_node(self, new_node_position, new_pin, new_pout):
        self.node_position = new_node_position
        self.pin = new_pin
        self.pout = new_pout