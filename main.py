from GcodePointCloudGenerator import GcodePointCloudGenerator
from PointCloudToSTLConverter import PointCloudToSTLConverter

if __name__ == '__main__':
    filename = "C:\\Users\\yoyok\\Desktop\\CE3_Voron_Design_Cube_v7.gcode"
    generator = GcodePointCloudGenerator(filename)
    points = generator.generate_point_cloud()
    converter = PointCloudToSTLConverter(points)
    stl_filename = converter.generate_stl(num_samples=5000)


    # Do something with the point cloud data here, such as visualize it
    # using Matplotlib or PyVista.
