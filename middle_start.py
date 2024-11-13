# middle_start.py
import networkx as nx
import matplotlib.pyplot as plt
from warehouse_MAP import warehouse_graph
from input import previous_location, start_location, target_location, obstacles


def dijkstra_path_planning_with_previous(graph, start, target, obstacles=None, previous_location=None):
    if obstacles is None:
        obstacles = []

    # Create a copy of the graph to not affect the original graph
    graph_copy = graph.copy()

    # Remove obstacles from the copied graph
    graph_copy.remove_nodes_from(obstacles)

    # Use Dijkstra's algorithm on the modified graph
    path = nx.shortest_path(graph_copy, source=start, target=target, weight='rfid')

    # Extract RFID and directions for the path
    rfid_tags = [graph.nodes[node]['rfid'] for node in path]
    directions = []

    for i in range(len(path) - 1):
        current_node = path[i]
        next_node = path[i + 1]
        prev_node = path[i - 1] if i > 0 else previous_location  # Use previous_location for the first movement

        # Check if the next_node is the same as the previous_location
        if prev_node is not None and next_node == prev_node:
            directions.append(f"[180,{current_node}]")
        else:
            edge_direction = determine_direction(graph, path, i, current_node, prev_node, start)
            directions.append(edge_direction)

    # Check if the current node is the node before the last node
    # Run the appropriate code based on the location degree
    location_degree = graph.degree(target_location)
    if location_degree == 1:

        if len(path) >= 2 and current_node == path[-2]:
            directions.append("[UP]")
    # Include final direction at the destination node
    directions.append(f"[Finish,{target}]")

    return rfid_tags, directions, path


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


def determine_direction(graph, path, current_index, current_node, prev_node=None, start_node=None):

    # Determine direction based on the relative positions of nodes
    if current_index < len(path) - 1:
        next_node = path[current_index + 1]

        if prev_node is not None:
            prev_vector = (pos[prev_node][0] - pos[current_node][0],
                           pos[prev_node][1] - pos[current_node][1])
        else:
            prev_vector = None

        next_vector = (pos[next_node][0] - pos[current_node][0],
                       pos[next_node][1] - pos[current_node][1])

        # Calculate the cross product to determine the turn direction
        if prev_vector is not None:
            cross_product = prev_vector[0] * next_vector[1] - prev_vector[1] * next_vector[0]
        else:
            cross_product = 0

        # Invert the sign of the cross product to correct turn directions
        cross_product *= -1

        if cross_product > 0:
            # Turn left
            return f"[left,{current_node}]"
        elif cross_product < 0:
            # Turn right
            return f"[right,{current_node}]"
        else:
            # Go straight
            return f"[straight,{current_node}]"

    # If no turn is needed, move towards the next node
    return f"[straight,{start_node}]"  # Use the start_node as the reference for the first movement
    # Check if the current node is the target node


# Example of usage by reading from the gh.py file
branched_warehouse_graph, pos = warehouse_graph()

# Set node positions
nx.set_node_attributes(branched_warehouse_graph, pos, 'pos')

rfid_path_branched, directions_branched, numeric_path_branched = dijkstra_path_planning_with_previous(
    branched_warehouse_graph, start_location, target_location, obstacles, previous_location
)

#print(f"Path: {numeric_path_branched}")
#print("Directions:")
#for direction_branched in directions_branched:
    #print(direction_branched)

# Draw the warehouse graph with the path
path_edges_branched = list(zip(numeric_path_branched, numeric_path_branched[1:]))
#draw_warehouse_graph(branched_warehouse_graph, pos, path_edges_branched, obstacles)


def save_path_to_file(output_file, rfid_tags, directions, path):
    with open(output_file, 'w') as file:
        file.write(f"Path: {path}\n")
        file.write("Directions:\n")
        for direction in directions:
            file.write(f"{direction}\n")


# Example usage of the modified script
output_file_path = 'path.txt'
save_path_to_file(output_file_path, rfid_path_branched, directions_branched, numeric_path_branched)
#print(f"Path and directions saved to {output_file_path}")
