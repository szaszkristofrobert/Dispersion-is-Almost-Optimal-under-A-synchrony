import tkinter as tk
import customtkinter as ctk
from graph import Graph


class UI:
    def __init__(self, graph):
        self.graph = graph
        self.window = ctk.CTk()
        self.window.title("Dispersion Simulator")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.window.after(1, self.window.wm_state, 'zoomed')

        self.window.grid_columnconfigure(0, weight=4)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        self.graph_pane = tk.Canvas(self.window, bg="#1E1E1E", highlightthickness=0)
        self.graph_pane.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        self.graph_pane.bind("<Button-1>", self.on_canvas_left_click)

        control_pane = ctk.CTkFrame(self.window, corner_radius=10)
        control_pane.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        control_pane.grid_rowconfigure(0, weight=1)
        control_pane.grid_columnconfigure(0, weight=1)

        self.terminal = ctk.CTkTextbox(control_pane, fg_color="#000000", text_color="#00FF00", font=("Consolas", 12),
                                       wrap="word", corner_radius=8)
        self.terminal.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 20))

        controls_frame = ctk.CTkFrame(control_pane, fg_color="transparent")
        controls_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        ctk.CTkLabel(controls_frame, text="Controls", font=("Arial", 16, "bold")).grid(row=0, column=0, pady=(0, 10))

        ctk.CTkButton(controls_frame, text="Print Graph", command=self.graph.print_graph).grid(row=1, column=0,
                                                                                               sticky="ew", pady=5)
        ctk.CTkButton(controls_frame, text="Clear Graph", fg_color="#C92A2A", command=self.clear_ui_and_graph).grid(
            row=2, column=0, sticky="ew", pady=(5, 15))

        self.filename_entry = ctk.CTkEntry(controls_frame, placeholder_text="filename")
        self.filename_entry.insert(0, "test_graph")
        self.filename_entry.grid(row=3, column=0, sticky="ew", pady=5)

        ctk.CTkButton(controls_frame, text="Save Graph", command=self.safe_save).grid(row=4, column=0, sticky="ew",
                                                                                      pady=5)
        ctk.CTkButton(controls_frame, text="Load Graph", command=self.safe_load).grid(row=5, column=0, sticky="ew",
                                                                                      pady=5)
        ctk.CTkButton(controls_frame, text="Step Graph", fg_color="#2B8A3E", command=self.step_graph).grid(row=6,
                                                                                                           column=0,
                                                                                                           sticky="ew",
                                                                                                           pady=(15,
                                                                                                                 10))

        self.first_node_clicked = None
        self.write_to_terminal("Rendszer indítva. Tölts be egy gráfot, vagy kattints a bal oldali vászonra!")

    def draw_graph(self):
        self.graph_pane.delete("all")

        for edge in self.graph.edges:
            n1 = self.graph.nodes[edge[0]]
            n2 = self.graph.nodes[edge[1]]
            self.graph_pane.create_line(n1.x, n1.y, n2.x, n2.y, fill="#444", width=2, tags="edge")

        for node_num, node in self.graph.nodes.items():
            settled_here = any(a.node_position == node_num and a.settled for a in self.graph.agents)
            active_count = sum(1 for a in self.graph.agents if a.node_position == node_num and not a.settled)

            color = "lime"
            if settled_here: color = "red"

            radius = 12
            self.graph_pane.create_oval(node.x - radius, node.y - radius, node.x + radius, node.y + radius, fill=color,
                                        outline="white", tags=("node", f"node_text_{node_num}"))
            self.graph_pane.create_text(node.x, node.y, text=f"N{node_num}", fill="black", font=("Arial", 8, "bold"),
                                        tags=("node", f"node_text_{node_num}"))

            if active_count > 0:
                self.graph_pane.create_oval(node.x + 15, node.y - 15, node.x + 25, node.y - 5, fill="yellow")
                self.graph_pane.create_text(node.x + 20, node.y - 10, text=str(active_count), fill="black",
                                            font=("Arial", 7, "bold"))

        self.graph_pane.tag_bind("node", "<Button-1>", self.on_node_left_click)
        self.graph_pane.tag_bind("node", "<Button-3>", self.on_node_right_click)
        self.graph_pane.tag_lower("edge")

    def step_graph(self):
        res = self.graph.step_graph()
        self.draw_graph()

        # Logok kiírása a UI terminálba
        if self.graph.action_logs:
            for log_msg in self.graph.action_logs:
                self.write_to_terminal(log_msg)
            self.graph.action_logs.clear()

        if res == "DISPERSION_FINISHED":
            self.write_to_terminal("\n*** Disperzió befejeződött: minden ágens letelepedett vagy a gráf bejárva. ***\n")

    def clear_ui_and_graph(self):
        self.graph.clear_graph()
        self.graph_pane.delete("all")
        self.terminal.delete("1.0", tk.END)
        self.write_to_terminal("Graph and logs cleared.")

    def safe_save(self):
        fn = self.filename_entry.get().strip()
        if fn:
            self.graph.save_graph(fn)
            self.write_to_terminal(f"Saved to: graphs/{fn}.json")

    def safe_load(self):
        fn = self.filename_entry.get().strip()
        if fn:
            self.graph.load_graph(fn)
            self.draw_graph()
            self.write_to_terminal(f"Loaded: graphs/{fn}.json")

    def on_canvas_left_click(self, event):
        if not self.graph_pane.find_overlapping(event.x - 1, event.y - 1, event.x + 1, event.y + 1):
            node_number = len(self.graph.nodes) + 1
            self.graph.add_node(node_number, event.x, event.y)
            self.draw_graph()

    def on_node_left_click(self, event):
        num = self.find_node_number_at(event.x, event.y)
        if self.first_node_clicked is None:
            self.first_node_clicked = num
        else:
            self.graph.add_edge(int(self.first_node_clicked), int(num))
            self.draw_graph()
            self.first_node_clicked = None

    def on_node_right_click(self, event):
        num = self.find_node_number_at(event.x, event.y)
        if num:
            self.graph.add_agent(int(num))
            self.draw_graph()

    def find_node_number_at(self, x, y):
        items = self.graph_pane.find_overlapping(x - 1, y - 1, x + 1, y + 1)
        for item in items:
            for tag in self.graph_pane.gettags(item):
                if tag.startswith("node_text_"):
                    return tag.split("_")[2]
        return None

    def write_to_terminal(self, text):
        self.terminal.insert(tk.END, text + "\n")
        self.terminal.see(tk.END)

    def mainloop(self):
        self.window.mainloop()

