import numpy as np

from wms.get_wms import GetWMS
from stl_generator.stl_generator import StlGenerator
import numpy as np

if __name__ == "__main__":
    wms = GetWMS(debug=False) # get_wms object
    wms.user_input() # Provide developer data input
    wms.calculate_width_height() # Calculate width and height of image
    wms.calculate_height_data() # Calculate the height data for the chosen geographical area
    thickness = 10 # TODO: Should be a parameter for the user to input
    filename = "geiranger.stl" # TODO: Should be a parameter for the user to input
    if(isinstance(wms.get_height_data(), np.ndarray)):
        stl = StlGenerator(wms.get_height_data(), thickness) # stl generator object
        stl.generate_stl(filename=filename) # Generate the finished .stl file
        stl.visualize()
    else:
        print(f"[ERROR]: API did not respond, therefore no STL was created.")