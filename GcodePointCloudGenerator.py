import numpy as np


class GcodePointCloudGenerator:
    def __init__(self, filename):
        self.filename = filename
        self.points = None

    def generate_point_cloud(self):
        with open(self.filename, 'r') as f:
            lines = f.readlines()

        x = []
        y = []
        z = []
        for line in lines:
            if line.startswith('G1'):
                # Parse out the X, Y, and Z coordinates
                parts = line.split()
                for part in parts:
                    if part.startswith('X'):
                        if len(part) > 1:
                            x.append(float(part[1:]))
                    elif part.startswith('Y'):
                        if len(part) > 1:
                            y.append(float(part[1:]))
                    elif part.startswith('Z'):
                        if len(part) > 1:
                            z.append(float(part[1:]))

        # Convert the X, Y, and Z lists to numpy arrays
        x = np.array(x)
        y = np.array(y)
        z = np.array(z)

        # Stack the X, Y, and Z arrays together
        self.points = np.vstack((x, y, z)).T

        return self.points
