from stl import mesh
import threading as thr
import numpy as np
import pyvista as pv
from scipy.spatial import Delaunay
import time

class StlGenerator:
    def __init__(self, height_data, thickness):
        self.height_data = height_data
        self.thickness = thickness
        self.graph = False # For debugging purposes when naming vertices

        # Create a thread for each of the meshing processes
        self.mesh_threads = [thr.Thread(target=self.__create_top_mesh),
                             thr.Thread(target=self.__create_bottom_mesh),
                             thr.Thread(target=self.__create_side_meshes)]

        self.filename = None

    # Function for starting all the meshing threads
    def __start_mesh_threads(self):
        for i in range(len(self.mesh_threads)):
            self.mesh_threads[i].start()

    # Function for stopping all the threads
    def __stop_mesh_threads(self):
        for i in range(len(self.mesh_threads)):
            self.mesh_threads[i].join()

    def __find_all_vertices(self):
        """
        Function for finding and storing vertices of all faces of the STL: top, bottom, and four sides.
        With some optional graphing used for understanding the orientation of each face.
        """
        # Calculate width and height of height_data array
        self.width = len(self.height_data)
        self.height = len(self.height_data[0])

        # Initialize arrays for storing vertices
        self.top_vertices = [0] * self.height * self.width
        self.bottom_vertices = [0] * self.height * self.width
        self.grid_2d = [0] * self.height * self.width # Flat 2D grid of all the data points in height_data. Used for Delaunay triangulation of the top/bottom surfaces

        xy_vertices_top = [0] * self.width
        yy_vertices_top = [0] * self.width

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
        # Filling xx, xy, yy, yx arrays with vertex data.
        idx = 0
        for x, row in enumerate(self.height_data):
            for y, column in enumerate(row):
                if(idx < self.width):
                    xy_vertices_top[idx] = [self.width-1, y, self.height_data[self.width-1, y]] # Fixed x of width-1, increasing y and selecting z values from height data with fixed x of width-1 and increasing y
                    yy_vertices_top[idx] = [0, y, self.height_data[0, y]] # Fixed x of 0, increasing y and selecting z values from height data with fixed x of 0 and increasing y
                idx+=1

        # Completing xx vertex array
        xx_vertices_top = self.top_vertices[:self.width] # Fill xx_vertices with the indexes from top_vertices that go along the x axis (fixed y axis of 0) (selecting the first 500 elements, since the top_vertices array conveniently start with the xx values) )
        xx_vertices_bottom = [[idx[0], 0, -self.thickness] for idx in xx_vertices_top] # Make bottom array with specified thickness
        self.xx_vertices = xx_vertices_top + xx_vertices_bottom # Append all bottom indexes to the top array
        xx_vertices_top = xx_vertices_top[::-1] # Reverse, so that it becomes the correct orientation for plotting

        # Completing xy vertex array
        xy_vertices_bottom = [[self.width-1, idx[1], -self.thickness] for idx in xy_vertices_top] # Make bottom array with specified thickness
        self.xy_vertices = xy_vertices_top + xy_vertices_bottom # Append all bottom indexes to the top array

        # Completing yy vertex array
        yy_vertices_bottom = [[0,idx[1], -self.thickness] for idx in yy_vertices_top] # Make bottom array with specified thickness
        self.yy_vertices = yy_vertices_top + yy_vertices_bottom # Append all bottom indexes to the top array
        
        # Completing yx vertex array
        yx_vertices_top = self.top_vertices[-self.width:] # Selecting the last 500 elements of the top_vertices, since the top_vertices array conveniently end with the yx values (is the opposite side of xx)
        yx_vertices_bottom = [[idx[0], self.width-1, -self.thickness] for idx in yx_vertices_top] # Make bottom array with specified thickness
        self.yx_vertices = yx_vertices_top + yx_vertices_bottom # Append all bottom indexes to the top array

        # Optional graphing used for understanding the orientation of each face.
        if self.graph:
            xxplot = pv.Chart2D()
            xx = [idx[2] for idx in xx_vertices_top]
            xx = xx[::-1]
            xxplot.plot(xx)

            xyplot = pv.Chart2D()
            xy = [idx[2] for idx in xy_vertices_top]
            xyplot.plot(xy)

            yxplot = pv.Chart2D()
            yx = [idx[2] for idx in yx_vertices_top]
            yx = yx[::-1]
            yxplot.plot(yx)

            yyplot = pv.Chart2D()
            yy = [idx[2] for idx in yy_vertices_top]
            yy = yy[::-1]
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

    def __create_top_mesh(self):
        """
        Create the top mesh based on top vertices. Creating faces using the 2D grid which consists of [x,y] points for
        the z values. Then updating the mesh vectors with the z value from the top vertices array.
        """
        self.top_faces = Delaunay(self.grid_2d).simplices # Simplices returns an array containing triangles from the triangulation
        self.top_mesh = mesh.Mesh(np.zeros(self.top_faces.shape[0], dtype=mesh.Mesh.dtype))
        for i, f in enumerate(self.top_faces):
            for j in range(3):
                self.top_mesh.vectors[i][j] = self.top_vertices[f[j]]

    def __create_bottom_mesh(self):
        """
        Create the bottom mesh based on bottom vertices. Creating faces using the 2D grid which consists of [x,y] points for
        the z values. Then updating the mesh vectors with the z value from the top vertices array.
        """
        self.bottom_faces = Delaunay(self.grid_2d).simplices # Simplices returns an array containing triangles from the triangulation
        self.bottom_mesh = mesh.Mesh(np.zeros(self.bottom_faces.shape[0], dtype=mesh.Mesh.dtype))
        for i, f in enumerate(self.bottom_faces):
            for j in range(3):
                self.bottom_mesh.vectors[i][j] = self.bottom_vertices[f[j]]

    def __create_side_meshes(self):
        """
        Create the side meshes by "triangulating manually". The faces array is created manually, and then combined with
        the vertices, this function creates all of the side meshes (xx, xy, yy, yx)
        """
        self.faces = np.zeros([len(self.xx_vertices), 3], dtype=int) # Array for storing triangles, size = [number of vertices, 3] (row, col)

        # Fill matrices with indexes that make up all of the triangles on xx and yy sides (xx is the same as yx, and yy is the same as xy)
        # The reason for using self.width as index, is that the first len(width) elements are top vertices, and the next len(width) elements are bottom elements
        # More visually, it looks like this: [498, 0, 43.0], [499, 0, 43.5], [0, 0, -10], [1, 0, -10], (element 498, 499, 500, 501 for a 500x500 image with 10 thickness)
        idx = 0
        for i in range(self.width - 1):
            self.faces[idx] = [i, i + 1, self.width + i]  # First triangle (two height vertices and one bottom vertex (starting at index width)
            self.faces[idx + 1] = [i + 1, self.width + i + 1, self.width + i]  # Opposite triangle (two height vertices and one bottom vertex (starting at index width)
            idx += 2  # Increasing index by two sice two triangles have been created in a single loop

        # Initialize meshes based on the face "template" created above
        self.xx_mesh = mesh.Mesh(np.zeros(self.faces.shape[0], dtype=mesh.Mesh.dtype))
        self.xy_mesh = mesh.Mesh(np.zeros(self.faces.shape[0], dtype=mesh.Mesh.dtype))
        self.yy_mesh = mesh.Mesh(np.zeros(self.faces.shape[0], dtype=mesh.Mesh.dtype))
        self.yx_mesh = mesh.Mesh(np.zeros(self.faces.shape[0], dtype=mesh.Mesh.dtype))

        # Fill the mesh vectors with vertices
        for i, f in enumerate(self.faces):
            for j in range(3):
                self.xx_mesh.vectors[i][j] = self.xx_vertices[f[j]]
                self.yx_mesh.vectors[i][j] = self.yx_vertices[f[j]]
                self.yy_mesh.vectors[i][j] = self.yy_vertices[f[j]]
                self.xy_mesh.vectors[i][j] = self.xy_vertices[f[j]]

    def __combine_meshes(self):
        """
        Combining top, bottom and side meshes into a single mesh and saving it in .stl format with provided filename.
        """
        self.combined_mesh = mesh.Mesh(np.concatenate([self.top_mesh.data, self.bottom_mesh.data, self.xx_mesh.data,
                                                       self.yx_mesh.data, self.xy_mesh.data, self.yy_mesh.data]))

    def generate_stl(self, filename):
        """
        Generate .stl with provided filename based on the combined mesh.
        :param filename: Filename for the .stl file
        """
        print(f"[INFO]: Generating STL file.")
        self.filename = filename
        self.__find_all_vertices()        # Find vertices of top, bottom and sides of the model
        self.__start_mesh_threads()       # Start meshing top, bottom and sides
        self.__stop_mesh_threads()        # Stop meshing top, bottom and sides
        self.__combine_meshes()           # Combine the top, bottom and side meshes to one mesh
        self.combined_mesh.save(filename) # Save the combined mesh into a .stl file with given filename
        print(f"[INFO]: Saved STL file.")

    def visualize(self):
        print(f"[INFO]: Opening visualization window of generated STL.")
        plotter = pv.Plotter()
        mesh = pv.read(self.filename)
        plotter.add_mesh(mesh)
        plotter.add_axes(line_width=5, labels_off=False)
        plotter.add_title(self.filename)
        plotter.camera.elevation = 20
        plotter.show()