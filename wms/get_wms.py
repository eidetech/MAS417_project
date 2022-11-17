from io import BytesIO
from PIL import Image, ImageFilter
import requests
import numpy as np
from colorama import init, AnsiToWin32, Fore, Style
import sys
stream = AnsiToWin32(sys.stderr).stream

class GetWMS:
    def __init__(self, debug):
        """
        Constructor
        :param debug:
        """
        # Variable for showing debugging info or not
        self.debug = debug

        # Initialize variables
        self.height_data = None
        self.thickness = None
        self.filename = None

    def user_input(self):
        """
        user_input is used for retrieving input data from user to the program
        """
        global bbox2string, input_list, width, height
        print(Fore.LIGHTBLUE_EX, file=stream)
        print("######################## MAP TO 3D-PRINT-MODEL ########################")
        print("#   This program converts a terrain model of a chosen Norwegian       #\n#   geographic area to a .stl file for 3d printing.                   #")
        print("#   1. First go to Google Maps and find the center point of an area   #\n#   in Norway you want to print a height model of.                    #")
        print("#   2. Then enter the coordinates, the size of area in meters,        #\n#   a scaling factor, the thickness of the 3d-print and a filname.    #")
        print("#######################################################################")
        print(Fore.LIGHTYELLOW_EX, file=stream)
        print("Examples: \nGaustadtoppen[ 59.854102, 8.648146, 2000, 1, 10, gaustadtoppen.stl ] \nGeiranger[ 62.119509, 7.148389, 15000, 0.5, 10, geiranger.stl ]\n")

        n = 6  # number of input_list elements
        print(Fore.LIGHTBLUE_EX, file=stream)
        input_list = list(input("Enter the following values, separated by comma: lat, lon, size, scale factor, print thickness, filename.stl: ").strip().split(','))[:n]
        print(Style.RESET_ALL, file=stream)
        deg2meter_list = [40000 * 2, 90000 * 2]
        # Convert the 7 first input entries to float numbers
        for i in range(5):
            input_list[i] = float(input_list[i])

        bbox = [input_list[1] - (input_list[2] / deg2meter_list[0]),
                input_list[0] - (input_list[2] / deg2meter_list[1]),
                input_list[1] + (input_list[2] / deg2meter_list[0]),
                input_list[0] + (input_list[2] / deg2meter_list[1])]
        bbox2string = ','.join(str(i) for i in bbox)

        height = 500
        width = 500

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
                      'CRS': 'CRS:84',  # Geoedic system to enter google map coordinates in decimal degrees
                      'BBOX': str(bbox2string),
                      'WIDTH': str(width),
                      'HEIGHT': str(height)}

        # Make the request and store returned data in response
        print(f"[INFO]: API request sent...")
        response = requests.get(wms_url, query_data, verify=True, timeout=1000)
        if (response.status_code == 200):
            print(f"[INFO]: API data received.")

            if self.debug:
                print(
                    f"[DEBUG]: HTTP status code: {response.status_code}, elapsed time to get response: {response.elapsed.microseconds / 1000}ms")

            # Open the response image as binary data
            bin_img = Image.open(BytesIO(response.content))
            # Blur image to filter "noise". Makes topology surface smoother
            blur_img = bin_img.filter(ImageFilter.BoxBlur(5))
            # Convert the blurred binary image to numpy array
            np_img = np.asarray(blur_img)

            return np_img
        else:
            return 0

    def calculate(self):
        """
        calculate_height_data uses the numpy image to calculate the height data matrix and visualize the height data using PyVista
        :return: Nothing
        """
        np_img = self.__get_api_data()
        if (isinstance(np_img, np.ndarray)):

            # Preallocate empty array with the size of the image
            height_data_size = np.zeros(width * height)

            if self.debug:
                print(height_data_size.shape)  # Shows the initial shape of the array

            # Creating and reshaping the array to width, height
            height_data_z = np.array(height_data_size).reshape(width, height)

            if self.debug:
                print(height_data_z.shape)  # Should return a Numpy array with shape width, height

            scale = input_list[3]  # Scaling factor for the terrain height point difference (Himalaya factor)

            for y, row in enumerate(np_img):
                for x, column in enumerate(row):
                    height_data_z[x, y] = column[0] * scale  # Populate the z array with the value of the red color in the pixel of that row and column (only one color is needed as R=G=B)

            height_data_z = height_data_z[::-1]  # Invert z array so that the image shows the correct view (If this is not done, the image will be inverted when compared to an actual map).
            self.height_data = height_data_z  # Data for STL generator
            self.thickness = input_list[4]
            self.filename = input_list[5]

if __name__ == "__main__":
    wms = GetWMS(debug=False)  # get_wms object
    wms.user_input()  # Provide input
    wms.calculate()  # Calculate height data based on input
    print(wms.height_data)
