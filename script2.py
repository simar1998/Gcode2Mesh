import numpy as np
import re
import open3d as o3d

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


def poisson_surface_reconstruction(point_cloud, depth=8, scale=1.1, linear_fit=True):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(point_cloud)

    # Compute normals
    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

    # Poisson surface reconstruction
    mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=depth, scale=scale,
                                                                        linear_fit=linear_fit)

    # Remove duplicated and degenerate triangles
    mesh.remove_duplicated_vertices()
    mesh.remove_degenerate_triangles()

    # Create a visualizer object
    visualizer = o3d.visualization.VisualizerWithKeyCallback()

    # Create a window to display the point cloud and mesh
    visualizer.create_window(window_name='Open3D', width=800, height=600)

    # Add the point cloud geometry to the visualizer
    visualizer.add_geometry(pcd)

    # Add the mesh geometry to the visualizer
    visualizer.add_geometry(mesh)

    # Define a simple key-callback function to close the window when the 'Q' key is pressed
    def close_window(vis):
        vis.close()
        return False

    # Register the key-callback function to the visualizer
    visualizer.register_key_callback(ord("Q"), close_window)

    # Run the visualizer
    visualizer.run()

    # Close the visualizer
    visualizer.destroy_window()

    return mesh

def create_stl_mesh(points):
    num_points = len(points)
    data = np.zeros(num_points, dtype=mesh.Mesh.dtype)

    for i, point in enumerate(points):
        data['vectors'][i] = np.array([point, point, point])

    return mesh.Mesh(data)

def create_point_cloud(gcode_data):
    points = []
    for x, y, z in gcode_data:
        x = round(float(x), 5)
        y = round(float(y), 5)
        z = round(float(z), 5)
        points.append([x, y, z])
    return np.array(points)

def save_point_cloud(point_cloud, output_file):
    np.savetxt(output_file, point_cloud, delimiter=",")

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




if __name__ == '__main__':
    file_path = "C:\\Users\\yoyok\\Desktop\\CE3_Voron_Design_Cube_v7.gcode"
    mesh_output_path = 'output_mesh.ply'
    output_path = 'output_image_13.png'  # Replace with your desired output file path
    gcode_data, min_coord, max_coord = extract_gcode_data(file_path)
    pointcloud = create_point_cloud(gcode_data)
    save_point_cloud(pointcloud,'pc.csv')
    print("Min Coordinates: ", min_coord)
    print("Max Coordinates: ", max_coord)
    mesh = poisson_surface_reconstruction(pointcloud)
    o3d.io.write_triangle_mesh(mesh_output_path, mesh)