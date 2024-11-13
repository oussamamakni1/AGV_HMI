import networkx as nx
import matplotlib.pyplot as plt
from input import start_location, target_location, obstacles
from warehouse_MAP import warehouse_graph


def dijkstra_path_planning(graph, start, target, obstacles=None, invert_first_turn=False):
    # Check if the start node has more than one edge
    if graph.degree(start) > 1:
        print(f"Warning: The start node {start} has more than one edge connected to it. "
              f"The path planning might not work as expected.")
    if obstacles is None:
        obstacles = []

    # Create a copy of the graph to not affect the original graph
    graph_copy = graph.copy()

    # Remove obstacles from the copied graph
    graph_copy.remove_nodes_from(obstacles)

    # Use Dijkstra's algorithm on the modified graph
    path = nx.shortest_path(graph_copy, source=start, target=target, weight='weight')

    # Extract RFID and directions for the path
    rfid_tags = [graph.nodes[node]['rfid'] for node in path]
    directions = [f"[Backup,{path[1]}]"]

    start_location_degree = graph.degree(start_location)
    if start_location_degree == 1:

            directions.append("[down]")

    # Include "backup" direction before the first movement

    for i in range(1, len(path) - 1):
        current_node = path[i]
        edge_direction = determine_direction(graph, path, i, current_node, target, invert_first_turn)
        directions.append(edge_direction)
    # Check if the current node is the node before the last node
    # Run the appropriate code based on the location degree
    target_location_degree = graph.degree(target_location)
    if target_location_degree == 1:

        if len(path) >= 2 and current_node == path[-2]:
            directions.append("[UP]")
    # Include final direction at the destination node
    directions.append(f"[Finish,{target}]")

    return rfid_tags, directions, path


def determine_direction(graph, path, current_index, current_node, target_node, invert_first_turn=False):
    # Check if the current node is the target node
    if current_node == target_node:
        return f"[Stop,{current_node}]"

    # Determine direction based on the relative positions of nodes
    prev_node = path[current_index - 1]
    next_node = path[current_index + 1]

    prev_vector = (graph.nodes[prev_node]['pos'][0] - graph.nodes[current_node]['pos'][0],
                   graph.nodes[prev_node]['pos'][1] - graph.nodes[current_node]['pos'][1])

    next_vector = (graph.nodes[next_node]['pos'][0] - graph.nodes[current_node]['pos'][0],
                   graph.nodes[next_node]['pos'][1] - graph.nodes[current_node]['pos'][1])

    # Calculate the cross product to determine the turn direction
    cross_product = prev_vector[0] * next_vector[1] - prev_vector[1] * next_vector[0]

    # Invert the sign of the cross product to correct turn directions
    cross_product *= -1

    if current_index == 1 and invert_first_turn:
        # Invert the direction at the second point only if invert_first_turn is True
        return f"[Right,{current_node}]" if cross_product > 0 else (
            f"[Left,{current_node}]" if cross_product < 0 else f"[180,{current_node}]")
    else:
        if cross_product > 0:
            # Turn left
            return f"[Left,{current_node}]"
        elif cross_product < 0:
            # Turn right
            return f"[Right,{current_node}]"
        else:
            # Go straight
            return f"[Straight,{current_node}]"


def draw_warehouse_graph(graph, pos, path_edges=None, obstacles=None):
    degrees = dict(graph.degree)

    # Separate nodes with only one edge and others
    square_nodes = [node for node, degree in degrees.items() if degree == 1]
    circular_nodes = [node for node, degree in degrees.items() if degree > 1]

    # Draw nodes with one edge as squares
    nx.draw_networkx_nodes(graph, pos, nodelist=square_nodes, node_size=700, node_color='skyblue', node_shape='s')

    # Draw other nodes as circles
    nx.draw_networkx_nodes(graph, pos, nodelist=circular_nodes, node_size=250, node_color='c', node_shape='o')

    nx.draw_networkx_edges(graph, pos)
    nx.draw_networkx_labels(graph, pos, font_size=10, font_color='black')

    if path_edges:
        nx.draw_networkx_edges(graph, pos, edgelist=path_edges, edge_color='r', width=2)

    if obstacles:
        nx.draw_networkx_nodes(graph, pos, nodelist=obstacles, node_color='red', node_size=300)

    labels = nx.get_edge_attributes(graph, 'rfid')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)
    plt.show()


# imported data
branched_warehouse_graph, branched_pos = warehouse_graph()
nx.set_node_attributes(branched_warehouse_graph, branched_pos, 'pos')

rfid_path_branched, directions_branched, numeric_path_branched = dijkstra_path_planning(
    branched_warehouse_graph, start_location, target_location, obstacles, invert_first_turn=True
)
# Display the output in the console

#print(f"Path: {numeric_path_branched}")
#print("Directions:")
#for direction_branched in directions_branched:
    #print(direction_branched)
# Draw the warehouse graph with the path

path_edges_branched = list(zip(numeric_path_branched, numeric_path_branched[1:]))
#draw_warehouse_graph(branched_warehouse_graph, branched_pos, path_edges_branched, obstacles)


def save_path_to_file(output_file, directions, path):
    with open(output_file, 'w') as file:
        file.write(f"Path: {path}\n")
        file.write("Directions:\n")
        for direction in directions:
            file.write(f"{direction}\n")


# imported data
output_file_path = 'path.txt'
save_path_to_file(output_file_path, directions_branched, numeric_path_branched)
print(f"Path and directions saved to {output_file_path}")

