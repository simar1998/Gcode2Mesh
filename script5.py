import re
import open3d as o3d
import numpy as np

def parse_gcode_line(line):
    line = line.strip()
    if not (line.startswith("G0") or line.startswith("G1")):
        return None

    gcode_data = {"X": None, "Y": None, "Z": None, "E": None, "F": None}
    pattern = r"([A-Z])([-+]?[0-9]*\.?[0-9]+)"

    for key, value in re.findall(pattern, line):
        if key in gcode_data:
            gcode_data[key] = float(value)

    return gcode_data

def linear_interpolation(start, end, steps):
    step_size = [(e - s) / steps for s, e in zip(start, end)]
    return [tuple(s + i * step for s, step in zip(start, step_size)) for i in range(steps)]

def process_gcode_file(file_path):
    point_cloud = []
    current_position = (0, 0, 0)
    extrusion_length = 0
    interpolation_resolution = 0.1

    with open(file_path, "r") as file:
        for line in file:
            gcode_data = parse_gcode_line(line)
            if not gcode_data:
                continue

            next_position = tuple(gcode_data[key] if gcode_data[key] is not None else current_position[i] for i, key in enumerate("XYZ"))
            next_extrusion_length = gcode_data["E"] if gcode_data["E"] is not None else extrusion_length

            if next_extrusion_length > extrusion_length:
                distance = ((next_position[0] - current_position[0]) ** 2 + (next_position[1] - current_position[1]) ** 2 + (next_position[2] - current_position[2]) ** 2) ** 0.5
                steps = int(distance / interpolation_resolution)

                if steps > 0:
                    interpolated_points = linear_interpolation(current_position, next_position, steps)
                    point_cloud.extend(interpolated_points)

            current_position = next_position
            extrusion_length = next_extrusion_length

    return point_cloud

def poisson_surface_reconstruction(point_cloud, depth=8, scale=1.1, linear_fit=False):


    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(point_cloud)

    cl, ind = pcd.remove_statistical_outlier(nb_neighbors=50, std_ratio=2)
    pcd = pcd.select_by_index(ind)


    # Compute normals
    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.5, max_nn=30))

    # Poisson surface reconstruction
    mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=depth, scale=scale,
                                                                        linear_fit=linear_fit)
    mesh = fix_mesh(mesh)

    mesh = o3d.t.geometry.TriangleMesh.from_legacy(mesh).fill_holes().to_legacy()

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


def fix_mesh(mesh):
    # Ensure that the mesh has normal vectors
    mesh.compute_vertex_normals()

    # Remove any degenerate triangles
    mesh.remove_degenerate_triangles()

    # Remove any duplicate vertices
    mesh.remove_duplicated_vertices()

    # Ensure that all faces are oriented outward
    mesh.remove_unreferenced_vertices()

    mesh.remove_duplicated_vertices()

    return mesh

def save_point_cloud(point_cloud, output_file):
    np.savetxt(output_file, point_cloud, delimiter=",")

if __name__ == "__main__":
    gcode_file_path ="C:\\Users\\yoyok\\Desktop\\CE3_Voron_Design_Cube_v7.gcode"
    mesh_output_path = 'output_mesh_2.ply'
    point_cloud = process_gcode_file(gcode_file_path)
    save_point_cloud(point_cloud, 'pc.csv')
    print("Generated point cloud:")
    for point in point_cloud:
        print(point)
    mesh = poisson_surface_reconstruction(point_cloud)
    o3d.io.write_triangle_mesh(mesh_output_path, mesh)

    output_file = "output.stl"
    o3d.io.write_triangle_mesh(output_file, mesh)