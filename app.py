from wms.get_wms import GetWMS
from stl_generator.stl_generator import StlGenerator

if __name__ == "__main__":
    wms = GetWMS(debug=False, visualize=False) # get_wms object
    wms.dev_input() # Provide developer data input
    wms.calculate_width_height() # Calculate width and height of image
    wms.calculate_height_data() # Calculate the height data for the chosen geographical area
    thickness = 10 # TODO: Should be a parameter for the user to input
    stl = StlGenerator(wms.get_height_data(), thickness) # stl generator object
    stl.find_all_vertices()
    stl.create_top_mesh()
    #stl.create_bottom_mesh()
    stl.create_side_meshes()
    #stl.combine_meshes()
    #stl.generate_stl(filename="geiranger.stl") # Generate the finished .stl file