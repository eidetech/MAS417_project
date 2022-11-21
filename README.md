# MAS417 project
## A piece of Norway STL generator
 ![example_stl](https://raw.githubusercontent.com/eidetech/MAS417_project/main/example_stl.png)
 
To use this software, clone the repository to your computer, alternatively download and extract the zip file found inside the green code tab, open a terminal and navigate to the project folder and run the following command:
```
pip install -r requirements.txt
```
If everything installs without problems, you are ready to run the program using the following command:
```
python app.py
```
If you for some strange reason have trouble to run the software or you will not install Python 3.8+, and have Docker installed, there is a Docker image on DockerHub that can be used:
```
docker pull tollak/mas 417 project:stlGen
docker run -i -t mas 417 prosject:stlGen
```

When the software is running you can go to Google maps and find a point of interest you want to print, then copy the coordinates and paste them into the terminal.

![googleMapExample](https://raw.githubusercontent.com/eidetech/MAS417_project/main/maps.png)

Then separated with comma you enter the width of the square area around your selected point you want to print in meters, a scaling factor, the tickness of the print, and at the end a filname with the .stl extention.
Like this:
```
62.119509, 7.148389, 15000, 0.5, 10, geiranger.stl
```
A stl file is then stored in the same directory where you run the program.