import tkinter as tk
from tkinter import simpledialog
import networkx as nx

GRID_SIZE = 20


class RenameNodeDialog(simpledialog.Dialog):
    def __init__(self, parent, title, node_names):
        self.node_names = node_names
        super().__init__(parent, title=title)

    def body(self, master):
        tk.Label(master, text="Choose a new name for the node:").grid(row=0, column=0)
        self.entry = tk.Entry(master)
        self.entry.grid(row=0, column=1)
        return self.entry

    def apply(self):
        self.result = self.entry.get()


class GraphEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Graph Editor")

        self.init_gui()

        self.selected_node = None
        self.graph = nx.Graph()
        self.node_positions = {}

        self.edge_mode = False
        self.temp_edge = None

    def init_gui(self):
        self.init_canvas()
        self.init_buttons()
        self.create_menu()

    def init_canvas(self):
        self.canvas = tk.Canvas(self.master, width=800, height=600, bg="white")
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)
        self.canvas.bind("<Button-1>", self.add_node)
        self.draw_grid()

    def init_buttons(self):
        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=10)

        self.add_edges_button = tk.Button(button_frame, text="Add Edges", command=self.toggle_edge_mode, padx=10, pady=5)
        self.add_edges_button.pack(side=tk.LEFT)

        self.generate_code_button = tk.Button(button_frame, text="Generate Code and Save", command=self.generate_code_and_save, padx=10, pady=5)
        self.generate_code_button.pack(side=tk.LEFT)

    def draw_grid(self):
        for i in range(0, 800, GRID_SIZE):
            self.canvas.create_line(i, 0, i, 600, fill="lightgray", dash=(2, 2))
        for j in range(0, 600, GRID_SIZE):
            self.canvas.create_line(0, j, 800, j, fill="lightgray", dash=(2, 2))

    def create_menu(self):
        menu_bar = tk.Menu(self.master)
        self.master.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Generate Code and Save", command=self.generate_code_and_save)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.destroy)

    def toggle_edge_mode(self):
        if self.edge_mode:
            self.exit_edge_mode()
        else:
            self.enter_edge_mode()

    def enter_edge_mode(self):
        self.add_edges_button.config(bg="green")
        self.edge_mode = True
        self.bind_edge_events()

    def exit_edge_mode(self):
        self.add_edges_button.config(bg=self.master.cget("bg"))
        self.edge_mode = False
        self.unbind_edge_events()
        if self.temp_edge is not None:
            self.canvas.delete(self.temp_edge)
            self.temp_edge = None

    def bind_edge_events(self):
        self.canvas.bind("<Button-1>", self.start_edge)
        self.canvas.bind("<B1-Motion>", self.drag_edge)
        self.canvas.bind("<ButtonRelease-1>", self.release_edge)

    def unbind_edge_events(self):
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")

    def start_edge(self, event):
        x, y = self.snap_to_grid(event.x, event.y)
        node_id = self.get_node_at_position(x, y)

        if node_id is not None:
            self.selected_node = node_id
            x1, y1 = self.node_positions[node_id]
            self.temp_edge = self.canvas.create_line(x1, y1, x, y, width=2, fill="green", arrow=tk.LAST)

    def drag_edge(self, event):
        if self.temp_edge is not None:
            x, y = event.x, event.y
            self.canvas.coords(self.temp_edge, *self.canvas.coords(self.temp_edge)[:2], x, y)

    def release_edge(self, event):
        if self.edge_mode and self.temp_edge is not None:
            x, y = self.snap_to_grid(event.x, event.y)
            node_id = self.get_node_at_position(x, y)

            if node_id is not None and node_id != self.selected_node:
                self.graph.add_edge(self.selected_node, node_id)
                x1, y1 = self.node_positions[self.selected_node]
                x2, y2 = self.node_positions[node_id]
                self.canvas.create_line(x1, y1, x2, y2, width=2, arrow=tk.LAST, fill="black")
                self.canvas.delete(self.temp_edge)
                self.temp_edge = None
                self.selected_node = None

    def snap_to_grid(self, x, y):
        grid_x = GRID_SIZE * round(x / GRID_SIZE)
        grid_y = GRID_SIZE * round(y / GRID_SIZE)
        return grid_x, grid_y

    def get_node_at_position(self, x, y):
        for node_id, (nx, ny) in self.node_positions.items():
            if nx - 10 <= x <= nx + 10 and ny - 10 <= y <= ny + 10:
                return node_id
        return None

    def add_attributes(self, node_name):
        attributes = simpledialog.askstring("Node Attributes", f"Enter attributes for node {node_name} (comma-separated):")
        if attributes:
            attribute_list = [attr.strip() for attr in attributes.split(',')]
            self.graph.nodes[node_name]['attributes'] = attribute_list

    def add_node(self, event):
        x, y = self.snap_to_grid(event.x, event.y)

        node_name = simpledialog.askstring("Node Name", "Enter RFID(UID):")
        if node_name and node_name not in self.graph.nodes:
            self.graph.add_node(node_name)
            self.node_positions[node_name] = (x, y)

            self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="skyblue", tags=node_name)
            self.canvas.create_text(x, y, text=node_name, fill="red", font=("Helvetica", 10, "bold"))
            self.canvas.tag_bind(node_name, "<Button-1>", lambda event, node=node_name: self.rename_node(node))

            # Call the add_attributes method to prompt the user for attributes
            self.add_attributes(node_name)

    def rename_node(self, node):
        new_name = RenameNodeDialog(self.master, "Rename Node", list(self.graph.nodes))
        if new_name.result:
            self.graph = nx.relabel_nodes(self.graph, {node: new_name.result}, copy=False)
            self.node_positions[new_name.result] = self.node_positions.pop(node)
            self.canvas.itemconfig(node, text=new_name.result)
            self.canvas.tag_bind(new_name.result, "<Button-1>",
                                 lambda event, node=new_name.result: self.rename_node(node))

    def generate_code(self):
        try:
            code = (
                f"import networkx as nx\n"
                f"def create_warehouse_graph():\n"
                f"    G = nx.Graph()\n\n"
                f"    G.add_nodes_from({list(self.graph.nodes)})\n"
                f"    G.add_edges_from({list(self.graph.edges)})\n\n"
                f"    pos = {self.node_positions}\n\n"
                f"    # Assign attributes to nodes\n"
                f"    nx.set_node_attributes(G, {self.get_attributes_dict()}, 'attributes')\n\n"
                f"    return G, pos"
            )
            return code

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_attributes_dict(self):
        attributes_dict = {}
        for node, data in self.graph.nodes(data=True):
            if 'attributes' in data:
                attributes_dict[node] = data['attributes'][0]
        return attributes_dict

    def generate_code_and_save(self):
        code = self.generate_code()
        if code:
            with open("create_warehouse_graph.py", "w") as file:
                file.write(code)
            print(f"Generated code has been saved to 'create_warehouse_graph.py'")
        self.master.destroy()


def main():
    root = tk.Tk()
    app = GraphEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
