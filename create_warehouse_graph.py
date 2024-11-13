import networkx as nx
import matplotlib.pyplot as plt


def create_warehouse_graph():
    G = nx.Graph()

    G.add_nodes_from(['A', 'A2'])
    G.add_edges_from([('A', 'A2')])

    pos = {'A': (160, 280), 'A2': (220, 280)}

    # Assign attributes to nodes
    nx.set_node_attributes(G, {'A': 'B', 'A2': 'B2'}, 'attributes')

    return G, pos



def visualize_warehouse_graph(graph, pos):
    degrees = dict(graph.degree)

    # Separate nodes with only one edge and others
    square_nodes = [node for node, degree in degrees.items() if degree == 1]
    circular_nodes = [node for node, degree in degrees.items() if degree > 1]

    # Draw nodes with one edge as squares
    nx.draw_networkx_nodes(graph, pos, nodelist=square_nodes, node_size=700, node_color='blue', node_shape='s')

    # Draw other nodes as circles
    nx.draw_networkx_nodes(graph, pos, nodelist=circular_nodes, node_size=250, node_color='skyblue', node_shape='o')

    nx.draw_networkx_edges(graph, pos)
    nx.draw_networkx_labels(graph, pos, font_size=10, font_color='black')

    plt.show()


# Example usage for visualization
branched_warehouse_graph, branched_pos = create_warehouse_graph()

visualize_warehouse_graph(branched_warehouse_graph, branched_pos)
