from ui import UI
from graph import Graph
import tkinter as tk

if __name__ == "__main__":
    graph = Graph()
    app = UI(graph)

    app.mainloop()
