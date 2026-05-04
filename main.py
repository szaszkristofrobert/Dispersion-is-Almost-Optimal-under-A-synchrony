from ui import UI
from graph import Graph

if __name__ == "__main__":
    graph = Graph()
    app = UI(graph)

    app.mainloop()
