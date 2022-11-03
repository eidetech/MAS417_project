from stl import mesh
import threading
import numpy as np
import pyvista as pv
from scipy.spatial import Delaunay

class StlGenerator:
    def __init__(self, height_data, thickness):
        self.height_data = height_data
        self.thickness = thickness
        self.graph = False # For debugging purposes

    def find_all_vertices(self):
        """
        Function for finding and storing vertices of all faces of the STL: top, bottom, and four sides
        :return: Nothing
        """
        # Calculate width and height of height_data array
        self.width = len(self.height_data)
        self.height = len(self.height_data[0])
        array_size = np.zeros(self.width * self.height)

        self.top_vertices = [0] * self.height * self.width
        self.grid_2d = [0] * self.height * self.width
        self.bottom_vertices = [0] * self.height * self.width
        self.xx_vertices = [0] * self.height * self.width
        self.xy_vertices = [0] * self.height * self.width
        self.yy_vertices = [0] * self.height * self.width
        self.yx_vertices = [0] * self.height * self.width

        # Top vertices (which is the actual height data points)
        idx = 0
        for y, row in enumerate(self.height_data):
            for x, column in enumerate(row):
                self.top_vertices[idx] = [x,y,self.height_data[x,y]]
                self.grid_2d[idx] = [x, y]
                idx+=1

        # Bottom vertices (which is just a flat plane the size of height_data array)
        idx = 0
        for y, row in enumerate(self.height_data):
            for x, column in enumerate(row):
                self.bottom_vertices[idx] = [x,y, -self.thickness]
                idx+=1

        # yy vertices
        self.yy_vertices = self.height_data[self.width - 1,:self.height]
        # yx vertices
        self.yx_vertices = self.height_data[:self.width, self.height - 1]
        # xx vertices
        self.xx_vertices = self.height_data[:self.width, 0]
        self.xx_vertices = self.xx_vertices[::-1] # TODO: Not sure why I have to reverse the order of this list, could probably select indexes in a smarter way
        # xy vertices
        self.xy_vertices = self.height_data[0,:self.height]

        if self.graph:
            xxplot = pv.Chart2D()
            xxplot.plot(self.xx_vertices)

            xyplot = pv.Chart2D()
            xyplot.plot(self.xy_vertices)

            yxplot = pv.Chart2D()
            yxplot.plot(self.yx_vertices)

            yyplot = pv.Chart2D()
            yyplot.plot(self.yy_vertices)

            pl = pv.Plotter(shape=(2, 2))
            pl.subplot(0, 0)
            pl.add_chart(xxplot)
            pl.add_title("xx plot", color='black')
            pl.set_background('white', all_renderers=False)
            pl.subplot(0, 1)
            pl.add_chart(xyplot)
            pl.add_title("xy plot", color='black')
            pl.set_background('white', all_renderers=False)
            pl.subplot(1, 0)
            pl.add_chart(yxplot)
            pl.add_title("yx plot", color='black')
            pl.set_background('white', all_renderers=False)
            pl.subplot(1, 1)
            pl.add_chart(yyplot)
            pl.add_title("yy plot", color='black')
            pl.set_background('white', all_renderers=False)
            pl.show()

    def create_top_mesh(self):
        self.top_faces = Delaunay(self.grid_2d).simplices
        self.top_mesh = mesh.Mesh(np.zeros(self.top_faces.shape[0], dtype=mesh.Mesh.dtype))
        for i, f in enumerate(self.top_faces):
            for j in range(3):
                self.top_mesh.vectors[i][j] = self.top_vertices[f[j]]
        self.top_mesh.save('top_mesh.stl')
    def create_bottom_mesh(self):
        self.bottom_faces = Delaunay(self.grid_2d).simplices
        self.bottom_mesh = mesh.Mesh(np.zeros(self.bottom_faces.shape[0], dtype=mesh.Mesh.dtype))
        for i, f in enumerate(self.bottom_faces):
            for j in range(3):
                self.bottom_mesh.vectors[i][j] = self.bottom_vertices[f[j]]
        self.bottom_mesh.save('bottom_mesh.stl')

    def combine_meshes(self):
        combined = mesh.Mesh(np.concatenate([self.top_mesh.data, self.bottom_mesh.data]))
        combined.save('combined.stl')

    #def generate_stl(self, filename):
        #stl_mesh = mesh.Mesh(self.height_data)
        #stl_mesh.save(filename+'.stl')