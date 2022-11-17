from wms.get_wms import GetWMS
from stl_generator.stl_generator import StlGenerator
import numpy as np

if __name__ == "__main__":
    wms = GetWMS(debug=False)  # get_wms object
    wms.user_input()  # Provide input
    wms.calculate()  # Calculate height data based on input
    if (isinstance(wms.height_data, np.ndarray)):  # Check if valid data was provided by API
        stl = StlGenerator(wms.height_data, wms.thickness)  # stl generator object
        stl.generate_stl(filename=wms.filename)  # Generate the finished .stl file
        stl.visualize()  # Visualize the generated .stl file with pyVista
    else:
        print(f"      [ERROR]: API did not respond, therefore no STL was created.")