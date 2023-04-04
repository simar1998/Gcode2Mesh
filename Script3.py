import re
import numpy as np
import matplotlib.pyplot as plt
import numpy
from stl import mesh
from mpl_toolkits.mplot3d import Axes3D


def extract_gcode_data(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    data = []
    min_coord = np.array([float('inf')] * 3)
    max_coord = np.array([float('-inf')] * 3)

    last_position = np.zeros(3)
    for line in lines:
        if line.startswith('G0') or line.startswith('G1'):
            command = re.findall(r'G[01]', line)[0]
            x = float(re.findall(r'X-?\d+\.?\d*', line)[0][1:]) if 'X' in line else last_position[0]
            y = float(re.findall(r'Y-?\d+\.?\d*', line)[0][1:]) if 'Y' in line else last_position[1]
            z = float(re.findall(r'Z-?\d+\.?\d*', line)[0][1:]) if 'Z' in line else last_position[2]
            e = float(re.findall(r'E-?\d+\.?\d*', line)[0][1:]) if 'E' in line else None
            new_position = np.array([x, y, z])

            if e is not None and e > 0:
                min_coord = np.minimum(min_coord, new_position)
                max_coord = np.maximum(max_coord, new_position)

            data.append((command, x, y, z, e))
            last_position = new_position

    return np.array(data, dtype=object), min_coord, max_coord

def create_stl_mesh(points):
    num_points = len(points)
    data = np.zeros(num_points, dtype=mesh.Mesh.dtype)

    for i, point in enumerate(points):
        data['vectors'][i] = np.array([point, point, point])

    return mesh.Mesh(data)

def set_axes_equal(ax):
    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = abs(x_limits[1] - x_limits[0])
    x_middle = np.mean(x_limits)
    y_range = abs(y_limits[1] - y_limits[0])
    y_middle = np.mean(y_limits)
    z_range = abs(z_limits[1] - z_limits[0])
    z_middle = np.mean(z_limits)

    max_range = max([x_range, y_range, z_range])

    ax.set_xlim3d([x_middle - max_range / 2, x_middle + max_range / 2])
    ax.set_ylim3d([y_middle - max_range / 2, y_middle + max_range / 2])
    ax.set_zlim3d([z_middle - max_range / 2, z_middle + max_range / 2])


def plot_gcode_data(gcode_data, output_path, max_cords, min_cords):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    last_position = np.zeros(3)
    lines = []
    for command, x, y, z, e in gcode_data:
        x = x if x is not None else last_position[0]
        y = y if y is not None else last_position[1]
        z = z if z is not None else last_position[2]
        if command == 'G1' and e is not None and e > 0:
            lines.append([last_position.copy(), [x, y, z]])

        last_position = np.array([x, y, z])
    lines = np.array(lines)

    file_path = "C:\\Users\\yoyok\\Desktop\\CE3_Voron_Design_Cube_v7.gcode"
    data, min_coord, max_coord = extract_gcode_data(file_path)

    points = np.array([[x, y, z] for _, x, y, z, _ in data], dtype=float)

    current_z = None
    alternate = False
    for line in lines:
        if current_z != line[0, 2]:
            current_z = line[0, 2]
            alternate = not alternate

        if alternate:
            ax.plot(line[:, 0], line[:, 1], line[:, 2], color='black')
        else:
            ax.plot(line[:, 0], line[:, 1], line[:, 2], color='lightgrey')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_xlim([min_cords[0], max_cords[0]])
    ax.set_ylim([min_cords[1], max_cords[1]])
    ax.set_zlim([min_cords[2], max_cords[2]])
    ax.view_init(elev=30, azim=30)
    ax.set_axis_off()
    set_axes_equal(ax)
    ax.mouse_init()  # Enable mouse interaction
    plt.show()  # Display plot in interactive window

    plt.savefig(output_path, dpi=300)
    plt.close(fig)

    stl_mesh = create_stl_mesh(points)
    stl_mesh.save('output.stl')


if __name__ == '__main__':
    file_path = "C:\\Users\\yoyok\\Desktop\\CE3_Voron_Design_Cube_v7.gcode"
    output_path = 'output_image_13.png'  # Replace with your desired output file path
    gcode_data, min_coord, max_coord = extract_gcode_data(file_path)
    print("Min Coordinates: ", min_coord)
    print("Max Coordinates: ", max_coord)
    plot_gcode_data(gcode_data, output_path, max_coord, min_coord)