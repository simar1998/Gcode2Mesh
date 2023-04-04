import point2mesh
import numpy as np


class PointCloudToSTLConverter:
    def __init__(self, point_cloud):
        self.point_cloud = point_cloud
        self.stl_filename = None

    def generate_stl(self, num_samples=10000):
        # Create a PointSet object from the point cloud
        point_set = point2mesh.PointSet(self.point_cloud)

        # Create a Poisson reconstruction object from the PointSet
        poisson_reconstruction = point2mesh.Poisson(point_set)

        # Generate a mesh from the Poisson reconstruction
        mesh = poisson_reconstruction.reconstruct(num_samples=num_samples)

        # Create an STL writer object from the mesh
        stl_writer = point2mesh.StlWriter(mesh)

        # Generate the STL file from the mesh
        self.stl_filename = 'output.stl'
        stl_writer.write(self.stl_filename)

        return self.stl_filename
