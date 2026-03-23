import tkinter as tk
from tkinter import scrolledtext
import customtkinter as ctk


class UI:
    def __init__(self, graph):
        self.graph = graph
        self.window = ctk.CTk()

        ctk.set_appearance_mode("dark")
        self.window.after(1, self.window.wm_state, 'zoomed')

        self.window.grid_columnconfigure(0, weight=20)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        self.graph_pane = tk.Canvas(self.window, bg="black")
        self.graph_pane.grid(row=0, column=0, sticky="nsew")
        self.graph_pane.bind("<Button-1>", self.on_canvas_left_click)

        control_pane = tk.Frame(self.window, bg="lightgray")
        control_pane.grid(row=0, column=1, sticky="nsew")
        control_pane.grid_rowconfigure(1, weight=1)
        control_pane.grid_columnconfigure(0, weight=1)
        
        # Controls header
        tk.Label(control_pane, text="Controls", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="n", pady=(5, 2))
        
        # Print Graph button under controls text
        tk.Button(control_pane, text="Print Graph", command=self.graph.print_graph).grid(row=2, column=0, sticky="n", pady=(0, 10))
        tk.Button(control_pane, text="Clear Graph", command=lambda: [self.graph.clear_graph(), self.graph_pane.delete("all")]).grid(row=3, column=0, sticky="n", pady=(0, 10))

        # Save Graph button and filename text input under Print Graph button
        self.filename_entry = tk.Entry(control_pane, textvariable=tk.StringVar(value="filename"))
        self.filename_entry.grid(row=4, column=0, sticky="n", pady=(0, 10))
        tk.Button(control_pane, text="Save Graph", command=lambda: self.graph.save_graph(self.filename_entry.get())).grid(row=5, column=0, sticky="n", pady=(0, 10))
        tk.Button(control_pane, text="Load Graph", command=lambda: self.load_graph(self.filename_entry.get())).grid(row=6, column=0, sticky="n", pady=(0, 10))

        # Terminal takes remaining space
        self.terminal = scrolledtext.ScrolledText(
            control_pane, 
            bg="black", 
            fg="lime", 
            font=("Consolas", 10),
            wrap=tk.WORD
        )
        self.terminal.grid(row=0, column=0, sticky="nsew", padx=5, pady=(0, 5))

        self.first_node_clicked = None 
            
    def mainloop(self):
        self.window.mainloop()

    def on_canvas_left_click(self, event):
        if self.graph_pane.find_overlapping(event.x-1, event.y-1, event.x+1, event.y+1):
            pass
        elif self.first_node_clicked is not None:
            self.write_to_terminal("Edge creation cancelled")
            self.first_node_clicked = None
        else:
            node_number = len(self.graph_pane.find_withtag("node")) // 2 + 1

            self.graph.add_node(node_number, event.x, event.y)
            self.draw_node(event.x, event.y, "lime", node_number=node_number)
            self.write_to_terminal(f"Node created at center: ({event.x}, {event.y})")

    def draw_node(self, x, y, color, node_number):
        radius = 10
        node_id = self.graph_pane.create_oval(
            x - radius, y - radius,
            x + radius, y + radius,
            fill=color, outline="green", width=3,
            tags="node"
        )

        text_id = self.graph_pane.create_text(
            x, y,  # Center at exact click position
            text=f"N{node_number}",
            fill="black",
            font=("Arial", 8, "bold"),
            tags=("node", f"node_text_{node_number}")
        )
        # Bind left click to the oval  
        self.graph_pane.tag_bind("node", "<Button-1>", self.on_node_left_click)
        # Bind right click to the oval  
        self.graph_pane.tag_bind("node", "<Button-3>", self.on_node_right_click)

    def draw_edge(self, node1_number, node2_number):         
        node1 = self.graph.nodes[int(node1_number)]
        node2 = self.graph.nodes[int(node2_number)]
        self.graph_pane.create_line(node1.x, node1.y, node2.x, node2.y, fill="lime", width=2, tags="edge")
        self.graph_pane.tag_lower("edge")

    def on_node_right_click(self, event):
        node_number = self.find_node_number_at(event.x, event.y)
        self.graph.add_agent(node_number)
        self.draw_graph()
        self.write_to_terminal(f"Agent placed on node N{node_number}")

    def on_node_left_click(self, event):
        node_number = self.find_node_number_at(event.x, event.y)
        if self.first_node_clicked is None:
            self.first_node_clicked = node_number
            self.write_to_terminal(f"Node N{node_number} selected for edge creation")
        else:
            self.graph.add_edge(int(self.first_node_clicked), int(node_number))
            self.draw_edge(self.first_node_clicked, node_number)
            self.write_to_terminal(f"Edge created between N{self.first_node_clicked} and N{node_number}")
            self.first_node_clicked = None

    def find_node_number_at(self, x, y):
        # Find which node was clicked  
        overlapping_items = self.graph_pane.find_overlapping(x-1, y-1, x+1, y+1)
        node_number = None
        
        # Check text items first (they have node number in tags)
        for item in overlapping_items:
            tags = self.graph_pane.gettags(item)
            for tag in tags:
                if tag.startswith("node_text_"):
                    node_number = tag.split("_")[2]  # Extract number from "node_text_3"
                    break
            if node_number:
                break
        return node_number

    def write_to_terminal(self, text):
        self.terminal.insert(tk.END, text+"\n")
        self.terminal.see(tk.END)

    def load_graph(self, filename):
        self.graph.load_graph(filename)
        self.graph_pane.delete("all")  # Clear existing graph

        self.draw_graph()

    def draw_graph(self):
        self.graph_pane.delete("all")

        for node_number, node in self.graph.nodes.items():
            agent_number = self.node_agent_number(node_number)
            if agent_number > 0:
                self.draw_node(node.x, node.y, "red", node_number=node_number)
                agent_id = self.graph_pane.create_text(
                    node.x+20, node.y+10,  # Center at exact click position
                    text=agent_number,
                    fill="red",
                    font=("Arial", 8, "bold"),
                    tags=("node", f"node_text_{node_number}")
                )
            else:
                self.draw_node(node.x, node.y, "lime", node_number=node_number)

        for edge in self.graph.edges:
            self.draw_edge(edge[0], edge[1])

    def node_agent_number(self, node_number):
        agent_number = 0
        for agent in self.graph.agents:
            if int(agent.node_position) == int(node_number):
                agent_number += 1
        return agent_number