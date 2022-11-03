from wms.get_wms import GetWMS
from stl_generator.stl_generator import StlGenerator

if __name__ == "__main__":
    wms = GetWMS(debug=False, visualize=True) # get_wms object
    wms.dev_input() # Provide developer data input
    wms.calculate_width_height() # Calculate width and height of image
    wms.calculate_height_data() # Calculate the height data for the chosen geographical area
    stl = StlGenerator(wms.get_height_data()) # stl generator object
    stl.find_all_vertices()

    #stl.generate_stl(filename="geiranger.stl") # Generate the finished .stl file