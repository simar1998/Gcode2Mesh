import numpy as np

from PointCloudToSTLConverter import PointCloudToSTLConverter


class GCodeToPointCloud:
    def __init__(self, gcode_file):
        self.gcode_file = gcode_file
        self.points = []

    def parse_gcode(self):
        with open(self.gcode_file, "r") as file:
            lines = file.readlines()

        current_pos = np.array([0.0, 0.0, 0.0])
        for line in lines:
            line = line.strip()
            if line.startswith("G1") or line.startswith("G0"):
                tokens = line.split(" ")
                new_pos = current_pos.copy()
                for token in tokens[1:]:
                    if token.startswith("X"):
                        try:
                            new_pos[0] = float(token[1:])
                        except ValueError:
                            pass
                    elif token.startswith("Y"):
                        try:
                            new_pos[1] = float(token[1:])
                        except ValueError:
                            pass
                    elif token.startswith("Z"):
                        try:
                            new_pos[2] = float(token[1:])
                        except ValueError:
                            pass
                self.points.append(new_pos)
                current_pos = new_pos

    def get_point_cloud(self):
        return np.array(self.points)

    #def save_point_cloud(self, output_file):
        #np.savetxt(output_file, self.points, delimiter=",")

# Usage:
gcode_to_point_cloud = GCodeToPointCloud("C:\\Users\\yoyok\\Desktop\\CE3_Voron_Design_Cube_v7.gcode")
gcode_to_point_cloud.parse_gcode()
point_cloud = gcode_to_point_cloud.get_point_cloud()
#gcode_to_point_cloud.save_point_cloud("output/point_cloud.csv")
converter = PointCloudToSTLConverter(point_cloud)
stl_filename = converter.generate_stl(num_samples=5000)