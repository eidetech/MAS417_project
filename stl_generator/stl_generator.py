from stl import mesh
import threading
import numpy as np
import pyvista as pv

class StlGenerator:
    def __init__(self, height_data):
        self.height_data = height_data

    def find_all_vertices(self):
        """
        Function for finding and storing vertices of all faces of the STL: top, bottom, and four sides
        :return: Nothing
        """
        print(self.height_data)
        # Calculate width and height of height_data array
        width = len(self.height_data)
        height = len(self.height_data[0])
        array_size = np.zeros(width * height)

        top_vertices = [0] * height * width
        bottom_vertices = [0] * height * width
        xx_vertices = [0] * height * width
        xy_vertices = [0] * height * width
        yy_vertices = [0] * height * width
        yx_vertices = [0] * height * width

        # Top vertices (which is the actual height data points)
        top_vertices = self.height_data

        # Bottom vertices (which is just a flat plane the size of height_data array)
        bottom_vertices =  np.array(array_size).reshape(width, height)

        # xx vertices
        xx_vertices = self.height_data[0, :height]
        #print(xx_vertices)
        # xy vertices

        # yy vertices

        # yx vertices

        chart = pv.Chart2D()
        chart.plot(xx_vertices)
        chart.show()

    #def generate_stl(self, filename):
        #stl_mesh = mesh.Mesh(self.height_data)
        #stl_mesh.save(filename+'.stl')