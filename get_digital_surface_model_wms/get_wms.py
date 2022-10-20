from io import BytesIO
from PIL import Image, ImageFilter
import requests
import numpy as np
import pyvista as pv

def main():
    # TODO: "Classify" this python file

    # Bool for enabling/disabling visualization of mesh
    visualize = True

    # Bool for enabling/disabling debugging
    debug = False

    # API get request details
    wms_url = "https://wms.geonorge.no/skwms1/wms.hoyde-dom?"
    query_data = {'VERSION': '1.3.0',
                  'REQUEST': 'GetMap',
                  'FORMAT': 'image/png',
                  'STYLES': 'default',
                  'LAYERS': 'DOM:None',
                  'CRS': 'EPSG:32633',
                  'BBOX': '280581.05308146186,6902727.670430477,283107.12974533665,6911610.535459495',
                  'WIDTH': '1014',
                  'HEIGHT': '611'}
    # TODO: Make width, height and bbox input dynamic

    # Make the request and store returned data in response
    response = requests.get(wms_url, query_data) # TODO: Add query timeout and print HTTP response in debug mode
    # Open the response image as binary data
    bin_img = Image.open(BytesIO(response.content))
    # Blur image to filter "noise". Makes topology surface smoother
    blur_img = bin_img.filter(ImageFilter.BoxBlur(5)) # TODO: Maybe filtering constant should be a parameter for the user to input?
    # Convert the blurred binary image to numpy array
    np_img = np.asarray(blur_img)

    #img_bin.show() # Show downloaded image

    # Define width and height of image TODO: These variables should also be dynamic
    width = 1014
    height = 611

    # Preallocate empty array with the size of the image
    height_data_size = np.zeros(1014*611)

    if debug:
        print(height_data_size.shape) # Shows the initial shape of the array

    # Creating and reshaping the arrays to width, height
    height_data_x = np.array(height_data_size).reshape(width, height)
    height_data_y = np.array(height_data_size).reshape(width, height)
    height_data_z = np.array(height_data_size).reshape(width, height)

    if debug:
        print(height_data_z.shape) # Should return a Numpy array with shape width, height

    scale = 4 # Scaling factor for the terrain height point difference (Himalaya factor)

    for y, row in enumerate(np_img):
        for x, column in enumerate(row):
            height_data_z[x,y] = column[0] * scale # Populate the z array with the value of the red color in the pixel of that row and column (only one color is needed as R=G=B)
            height_data_x[x,y] = int(x)            # Populate the x array with the x index of the z value stored in height_data_z
            height_data_y[x,y] = int(y)            # Populate the y array with the y index of the z value stored in height_data_z

    # Add xyz coordinates into a single array (so that height_data_3d represents the (x, y, z) value of all the data points
    height_data_3d = np.c_[height_data_x.reshape(-1), height_data_y.reshape(-1), height_data_z.reshape(-1)]

    if debug:
        print(height_data_3d)

    if(visualize):
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

if __name__ == "__main__":
    main()
