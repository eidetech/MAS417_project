# MAS417 project
## A piece of Norway STL generator

<p align="center">
<img width="300" alt="Geiranger" src="https://raw.githubusercontent.com/eidetech/MAS417_project/main/example_stl.png">
</p>
 
To use this software, clone the repository to your computer, alternatively download and extract the zip file found inside the green code tab, open a terminal and navigate to the project folder and run the following command:
```
pip install -r requirements.txt
```
If everything installs without problems, you are ready to run the program using the following command:
```
python app.py
```
If you for some strange reason have trouble to run the software there is a Docker image on DockerHub that can be used. However this version does not vizualize the stl before saving:
```
docker pull tollak/mas 417 project:stlGen
docker run -i -t mas 417 prosject:stlGen
```

When the software is running go to Google maps and find the point of interest you want to print, then copy the coordinates and paste them into the terminal.

<p align="center">
<img width="300" alt="Google Maps example" src="https://raw.githubusercontent.com/eidetech/MAS417_project/main/maps.png">
</p>

Then separated with comma you enter the width, in meters, of the square area around your selected point, a scaling factor, the tickness of the print, and a filename with .stl extention.
See example:
```
62.119509, 7.148389, 15000, 0.5, 10, geiranger.stl
```
A stl file is then stored in the working directory.