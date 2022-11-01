from io import BytesIO
from PIL import Image, ImageFilter
import requests
import numpy as np
import pyvista as pv

class GetWMS:
    def __init__(self, debug, visualize):
        """
        Constructor
        :param debug:
        :param visualize:
        """

        # Variable for showing debugging info or not
        self.debug = debug

        # Variable for visualizing the height data or not
        self.visualize = visualize

        # Initialize height data variable
        self.height_data = 0

    def user_input(self):
        """
        user_input is used for retrieving input data from user to the program

        :return: Nothing
        """
        global bbox2string, input_list

        print("----------MAP TO 3D-PRINT-MODEL----------")
        print(
            "This program converts a terrain model of a chosen \nnorwegian geographic area to a .stl file for 3d printing\n")
        print(
            "1. First go to Google Maps and find the center point of \nan area in Norway you want to print a height model of.")
        print("2. Then enter the coordinates, the size of area in meters,\nresolution in pixels and a scaling factor.")
        print(
            "Examples: \nGaustadtoppen[ 59.854102, 8.648146, 2000, 2000, 1000, 1 ] \nGeiranger[ 62.119509, 7.148389, 5000, 2500, 500, 0.5 ]\n")

        n = 6  # number of input_list elements
        input_list = list(map(float, input("Enter lat,lon,width,height,resolution,scalefactor: ").strip().split(',')))[
                     :n]

        bbox = [input_list[1] - (input_list[2] / 50000), input_list[0] - (input_list[3] / 50000),
                input_list[1] + (input_list[2] / 50000), input_list[0] + (input_list[3] / 50000)]
        bbox2string = ','.join(str(i) for i in bbox)

    def dev_input(self):
        """
        dev_input is used for inputting necessary data to the program which will later be provided by user

        :return: Nothing
        """
        global bbox2string, input_list
        # Static Geiranger for dev
        input_list = [0] * 6       # 6x1 array of 0's
        input_list[0] = 62.119509  # Lat
        input_list[1] = 7.148309   # Lon
        input_list[2] = 15000      # Width
        input_list[3] = 15000      # Height
        input_list[4] = 500        # Res
        input_list[5] = 0.5        # Scale/himalaya
        bbox = [input_list[1] - (input_list[2] / 50000), input_list[0] - (input_list[3] / 50000),
                input_list[1] + (input_list[2] / 50000), input_list[0] + (input_list[3] / 50000)]
        bbox2string = ','.join(str(i) for i in bbox)

    def calculate_width_height(self):
        """
        calculate_width_height calculates the width and height of the image retrieved from API based on resolution
        :return: Nothing
        """
        global width, height

        resolution = int(input_list[4])  # resolution of picture width in pixels
        height = int(resolution / (input_list[2] / input_list[3]))
        width = resolution

        print(f"[INFO]: Image resolution: {width} x {height} pixels")

    def __get_api_data(self):
        """
        __get_api_data makes a GET request to the Geonorge WMS API and returns the ready-made data as a "numpy image"
        :return: np_img
        """
        # API get request details
        wms_url = "https://wms.geonorge.no/skwms1/wms.hoyde-dom?"

        query_data = {'VERSION': '1.3.0',
                      'REQUEST': 'GetMap',
                      'FORMAT': 'image/png',
                      'STYLES': 'default',
                      'LAYERS': 'DOM:None',
                      'CRS': 'CRS:84',          # Geoedic system to enter google map coordinates in decimal degrees
                      'BBOX': str(bbox2string),
                      'WIDTH': str(width),
                      'HEIGHT': str(height)}

        # Make the request and store returned data in response
        response = requests.get(wms_url, query_data, verify=True, timeout=10)

        if self.debug:
            print(f"[DEBUG]: HTTP status code: {response.status_code}, elapsed time to get response: {response.elapsed.microseconds/1000}ms")

        # Open the response image as binary data
        bin_img = Image.open(BytesIO(response.content))
        # Blur image to filter "noise". Makes topology surface smoother
        blur_img = bin_img.filter(ImageFilter.BoxBlur(5)) # TODO: Maybe filtering constant should be a parameter for the user to input?
        # Convert the blurred binary image to numpy array
        np_img = np.asarray(blur_img)

        # TODO: the code commented out below is not necessary. Or could be moved to debugging if statement
        #print("[INFO]: Showing surface model image...")
        #npy_img = np.asarray(bin_img)
        #npy2_img = Image.fromarray(np.uint8(npy_img))
        #npy2_img.show()

        return np_img

    def calculate_height_data(self):
        """
        calculate_height_data uses the numpy image to calculate the height data matrix and visualize the height data using PyVista
        :return: Nothing
        """
        np_img = self.__get_api_data()
        # Preallocate empty array with the size of the image
        height_data_size = np.zeros(width*height)

        if self.debug:
            print(height_data_size.shape) # Shows the initial shape of the array

        # Creating and reshaping the arrays to width, height
        height_data_x = np.array(height_data_size).reshape(width, height)
        height_data_y = np.array(height_data_size).reshape(width, height)
        height_data_z = np.array(height_data_size).reshape(width, height)

        if self.debug:
            print(height_data_z.shape) # Should return a Numpy array with shape width, height

        scale = input_list[5] # Scaling factor for the terrain height point difference (Himalaya factor)

        for y, row in enumerate(np_img):
            for x, column in enumerate(row):
                height_data_z[x,y] = column[0] * scale # Populate the z array with the value of the red color in the pixel of that row and column (only one color is needed as R=G=B)
                height_data_x[x,y] = int(x)            # Populate the x array with the x index of the z value stored in height_data_z
                height_data_y[x,y] = int(y)            # Populate the y array with the y index of the z value stored in height_data_z

        # Invert x and y arrays so that the image shows the correct view (If this is not done, the image will be inverted when compared to the actual map).
        height_data_x = height_data_x[::-1]
        height_data_y = height_data_y[::-1]

        # Add xyz coordinates into a single array (so that height_data_3d represents the (x, y, z) value of all the data points
        height_data_3d = np.c_[height_data_x.reshape(-1), height_data_y.reshape(-1), height_data_z.reshape(-1)]

        self.height_data = height_data_z

        if self.debug:
            print(height_data_3d)
            print(height_data_z)


        if(self.visualize):
            print("[INFO]: Calculated point cloud, starting Delaunay triangulation...")
            # Generate PyVista point cloud
            cloud = pv.PolyData(height_data_3d)
            #cloud.plot(point_size=1)

            # Apply Delaunay triangulation to connect points into surfaces
            surf = cloud.delaunay_2d()

            print("[INFO]: Showing result...")

            # Set up plotter
            plotter = pv.Plotter()
            # Add the mesh to the plotter
            #plotter.add_points(height_data_3d, point_size=10, color='orange')
            plotter.add_mesh(surf, color='white')
            # Show the plot in window
            plotter.show(screenshot='topography.png')

    def get_height_data(self):
        """
        get_height_data returns the height_data variable
        :return: height_data
        """
        return self.height_data

if __name__ == "__main__":
    wms = GetWMS(debug=True, visualize=True) # Create wms object
    wms.dev_input() # Add the development input (Geiranger lat lon)
    wms.calculate_width_height() # Calculate the width and height of resulting image TODO: Could be a private function to be called inside class
    wms.calculate_height_data() # Calculate the height data
    print(wms.get_height_data()) # Get the calculated height data for further use in stl generator

