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
        Function for finding and storing vertices of all faces of the STL: top, bottom, and four sides.
        With some optional graphing used for understanding the orientation of each face.
        """
        # Calculate width and height of height_data array
        self.width = len(self.height_data)
        self.height = len(self.height_data[0])
        #array_size = np.zeros(self.width * self.height)

        # Initialize arrays for storing vertices
        self.top_vertices = [0] * self.height * self.width
        self.grid_2d = [0] * self.height * self.width

        #xx_vertices_top = [0] * self.width # TODO: width or height here?
        self.xy_vertices_top = [0] * self.width # TODO: width or height here?
        self.yy_vertices_top = [0] * self.width # TODO: width or height here?
        self.yx_vertices_top = [0] * self.width # TODO: width or height here?
        self.xx_side_2d = [0] * 2 * self.height
        self.xy_side_2d = [0] * self.height * self.width
        self.yy_side_2d = [0] * self.height * self.width
        self.yx_side_2d = [0] * self.height * self.width

        self.bottom_vertices = [0] * self.height * self.width
        self.bottom_data = self.height_data * 0 - self.thickness

        # Top vertices (which is the actual height data points)
        idx = 0
        for y, row in enumerate(self.height_data):
            for x, column in enumerate(row):
                self.top_vertices[idx] = [x,y,self.height_data[x,y]] # Create an array containing [x,y,z] coordinate for the top vertices
                self.grid_2d[idx] = [x, y]
                idx+=1

        # Bottom vertices (which is just a flat plane the size of height_data array)
        idx = 0
        for y, row in enumerate(self.height_data):
            for x, column in enumerate(row):
                self.bottom_vertices[idx] = [x,y, -self.thickness] # Create an array containing [x,y,z] coordinate for the bottom vertices
                idx+=1

        # Side vertices
        idx = 0
        for y, row in enumerate(self.height_data):
            for x, column in enumerate(row):
                if(idx < self.width):
                    self.xy_vertices_top[idx] = [499,x, self.height_data[self.width-1, x]]
                    self.yy_vertices_top[idx] = [0, x, self.height_data[0, x]]
                idx+=1

        xx_vertices_top = self.top_vertices[:self.width]
        xx_vertices_bottom = [[pt[0], 0, -self.thickness] for pt in xx_vertices_top]

        self.xx_vertices = xx_vertices_top + xx_vertices_bottom

        xx_vertices_top = xx_vertices_top[::-1]
        self.yx_vertices_top = self.top_vertices[-self.width:]

        self.xx = [idx[2] for idx in xx_vertices_top]
        # Create 2d vector arrays for sides
        idx = 0
        for i in range(0,len(self.xx)):
            self.xx_side_2d[i] = [i, self.xx[i]]
            #self.xy_side_2d[idx] = [self.width, y]
            #self.yy_side_2d[idx] = [0, y]
            #self.yx_side_2d[idx] = [x, self.height]

        for i in range(self.width, 2*self.width):
            self.xx_side_2d[i] = [i-self.width, 0]

        if self.graph:
            xxplot = pv.Chart2D()
            xx = [idx[2] for idx in xx_vertices_top]
            xxplot.plot(xx)

            xyplot = pv.Chart2D()
            xy = [idx[2] for idx in self.xy_vertices_top]
            xyplot.plot(xy)

            yxplot = pv.Chart2D()
            yx = [idx[2] for idx in self.yx_vertices_top]
            yxplot.plot(yx)

            yyplot = pv.Chart2D()
            yy = [idx[2] for idx in self.yy_vertices_top]
            yyplot.plot(yy)

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
        """
        Create the top mesh based on top vertices. Creating faces using the 2D grid which consists of [x,y] points for
        the z values. Then updating the mesh vectors with the z value from the top vertices array.
        """
        self.top_faces = Delaunay(self.grid_2d).simplices # Simplices returns an array containing triangles from the triangulation
        self.top_mesh = mesh.Mesh(np.zeros(self.top_faces.shape[0], dtype=mesh.Mesh.dtype))
        for i, f in enumerate(self.top_faces):
            for j in range(3):
                self.top_mesh.vectors[i][j] = self.top_vertices[f[j]]
        self.top_mesh.save('top_mesh.stl')
    def create_bottom_mesh(self):
        """
        Create the bottom mesh based on bottom vertices. Creating faces using the 2D grid which consists of [x,y] points for
        the z values. Then updating the mesh vectors with the z value from the top vertices array.
        """
        self.bottom_faces = Delaunay(self.grid_2d).simplices # Simplices returns an array containing triangles from the triangulation
        self.bottom_mesh = mesh.Mesh(np.zeros(self.bottom_faces.shape[0], dtype=mesh.Mesh.dtype))
        for i, f in enumerate(self.bottom_faces):
            for j in range(3):
                self.bottom_mesh.vectors[i][j] = self.bottom_vertices[f[j]]
        self.bottom_mesh.save('bottom_mesh.stl')

    def create_side_meshes(self):
        # Create matrices for holding the indexes of the vertices that make up all the triangles
        self.xx_faces = np.zeros([len(self.xx_vertices), 3], dtype=int) # Array for storing triangles, size = [number of vertices, 3] (row, col)
        #self.yy_faces = np.zeros([len(self.yy_vertices), 3], dtype=int)

        # Fill matrices with indexes that make up all of the triangles on xx and yy sides (xx is the as yx, and yy is the same as xy)
        idx = 0
        for i in range(self.width - 1):
            self.xx_faces[idx] = [i, i + 1, self.width + i]  # First triangle
            self.xx_faces[idx + 1] = [i + 1, self.width + i + 1, self.width + i]  # Opposite triangle

            #self.yy_faces[idx] = [i, i + 1, self.width + i]  # First triangle
            #self.yy_faces[idx + 1] = [i + 1, self.width + i + 1, self.width + i]  # Opposite triangle
            idx += 2

        # Create meshes based on the faces created above
        self.xx_mesh = mesh.Mesh(np.zeros(self.xx_faces.shape[0], dtype=mesh.Mesh.dtype))
        #self.xy_mesh = mesh.Mesh(np.zeros(self.yy_faces.shape[0], dtype=mesh.Mesh.dtype))
        #self.yy_mesh = mesh.Mesh(np.zeros(self.yy_faces.shape[0], dtype=mesh.Mesh.dtype))
        #self.yx_mesh = mesh.Mesh(np.zeros(self.xx_faces.shape[0], dtype=mesh.Mesh.dtype))

        #
        for i, f in enumerate(self.xx_faces):
            for j in range(3):
                self.xx_mesh.vectors[i][j] = self.xx_vertices[f[j]]
                #self.yx_mesh.vectors[i][j] = self.yx_vertices[f[j]]

        #for i, f in enumerate(self.yy_faces):
        #    for j in range(3):
        #        self.yy_mesh.vectors[i][j] = self.yy_vertices[f[j]]
        #        self.xy_mesh.vectors[i][j] = self.xy_vertices[f[j]]

    def combine_meshes(self):
        """
        Combining top, bottom and side meshes into a single mesh and saving it in .stl format with provided filename.
        """
        self.combined_mesh = mesh.Mesh(np.concatenate([self.top_mesh.data, self.bottom_mesh.data, self.xx_mesh.data]))#,
                                                     #  self.xy_mesh.data, self.yy_mesh.data, self.yx_mesh.data]))

    def generate_stl(self, filename):
        """
        Generate .stl with provided filename based on the combined mesh.
        :param filename: Filename for the .stl file
        """
        self.combined_mesh.save(filename)