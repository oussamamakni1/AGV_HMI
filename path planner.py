from warehouse_MAP import warehouse_graph as create_warehouse_graph
import os

def find_previous_point(path, current_point):
    if current_point in path:
        index = path.index(current_point)
        if index > 0:
            return path[index - 1]
        else:
            # If the current point is the last point, consider it a valid point
            return path[-1]
    else:
        return None  # Current point not found in the path


def update_input_file(previous_point, start_location, target_location, file_path='input.py'):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Find and update the previous_location, start_location, and target_location variables
    for i, line in enumerate(lines):
        previous_point = previous_point.replace("'", "").replace("[", "").replace("]", "")
        start_location = start_location.replace("'", "").replace("[", "").replace("]", "")
        target_location = target_location.replace("'", "").replace("[", "").replace("]", "")
        if 'previous_location' in line:
            lines[i] = f'previous_location = \'{previous_point}\'\n'
        if 'start_location' in line:
            lines[i] = f'start_location = \'{start_location}\'\n'
        if 'target_location' in line:
            lines[i] = f'target_location = \'{target_location}\'\n'

    # Write the modified content back to input.py
    with open(file_path, 'w') as file:
        file.writelines(lines)


def run_appropriate_code(location):
    graph, _ = create_warehouse_graph()
    # Check the degree of the location node
    location_degree = graph.degree(location)
    # Run the appropriate code based on the location degree
    if location_degree == 1:
        print("run_edge_start_code")
        os.system('python edge_start.py')
    else:
        print("run_middle_start_code")
        os.system('python middle_start.py')


def main():
    while True:
        # Read path.txt
        with open('path.txt', 'r') as file:
            lines = file.readlines()

        # Extract points from Path line
        path = [point.strip() for point in lines[0].split(':')[1][1:-1].split(',')]

        # Take manual input
        user_input = input("Enter 'ready' to proceed or 'exit' to quit: ")

        if user_input.lower() == 'exit':
            break  # Exit the loop if the user enters 'exit'
        elif user_input.lower() != 'ready':
            print(f"Invalid input. Please enter 'ready' or 'exit'.")
            continue

        # Ask for start_location
        start_location_input = input("Enter the current point as the start location: ")
        start_location_input = "'" + start_location_input + "'"
        target_location_input = input("Enter the target location: ")
        target_location_input = "'" + target_location_input + "'"
        target_location = target_location_input.replace("'", "").replace("[", "").replace("]", "")
        previous_point_start = find_previous_point(path, start_location_input)

        if previous_point_start:
            previous_point_start = previous_point_start.replace("'", "").replace("[", "").replace("]", "")
            start_location = start_location_input.replace("'", "").replace("[", "").replace("]", "")
            update_input_file(previous_point_start, start_location, target_location)
        else:
            print(f"{start_location_input} is not in the path or is the starting point.")
            start_location = start_location_input.strip("'\"")
            update_input_file('non', start_location, target_location)

        run_appropriate_code(start_location)


if __name__ == "__main__":
    main()
