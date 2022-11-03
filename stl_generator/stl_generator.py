from stl import mesh
import threading
import numpy as np
import pyvista as pv

class StlGenerator:
    def __init__(self, height_data):
        self.height_data = height_data
        self.graph = False

    def find_all_vertices(self):
        """
        Function for finding and storing vertices of all faces of the STL: top, bottom, and four sides
        :return: Nothing
        """
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

        # yy vertices
        yy_vertices = self.height_data[width - 1,:height]
        # yx vertices
        yx_vertices = self.height_data[:width, height - 1]
        # xx vertices
        xx_vertices = self.height_data[:width, 0]
        xx_vertices = xx_vertices[::-1] # TODO: Not sure why I have to reverse the order of this list, could probably select indexes in a smarter way
        # xy vertices
        xy_vertices = self.height_data[0,:height]

        if self.graph:
            xxplot = pv.Chart2D()
            xxplot.plot(xx_vertices)

            xyplot = pv.Chart2D()
            xyplot.plot(xy_vertices)

            yxplot = pv.Chart2D()
            yxplot.plot(yx_vertices)

            yyplot = pv.Chart2D()
            yyplot.plot(yy_vertices)

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


    #def generate_stl(self, filename):
        #stl_mesh = mesh.Mesh(self.height_data)
        #stl_mesh.save(filename+'.stl')