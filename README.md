A Python typesetting application, licensed under the GPL 3.0 or later.

Runs out of the box on linux systems, start with ``python3.5 main.py test.html``
Try a few example files: ``python3.5 main.py 2014.html``, ``python3.5 main.py 2016.html``
(Other systems may need to install freetype-py and pyhunspell)

Install 
------------
This application should work **out of the box** on a *default* Ubuntu (15.10) installation. It is written in Python 3.5.
However, some libraries necessary for SVG rendering because of [cairoSVG](https://github.com/Kozea/CairoSVG)), which depends on the `tinycss` module.
`tinycss` is easily installable through `pip`. 

### Installing pip
`pip` is the ubiquitous python module installer and you may already have it installed. If you do not, the reference command is
````
sudo apt-get install python3-pip
````

### Installing tinycss
````
pip3 install tinycss
````
If `tinycss` still can’t be found, this is most likely because `pip` installed `tinycss` for the wrong version of python. Correct this by running
````
python3.5 /usr/bin/pip3 install tinycss
````
This problem is quite common, and users with the same problem on other platforms should also try running `pip` from python itself should its libraries install in the wrong locations.

Special thanks to the developers of Pygments, Pyphen, and CairoSVG for their valuable free libraries.

![Screenshot](screenshot.png?raw=true "Text")

![Screenshot](screenshot2.png?raw=true "Graphing")

![Screenshot](screenshot3.png?raw=true "Example typesetting")

![Screenshot](screenshot4.png?raw=true "Example typesetting")

![Screenshot](screenshot5.png?raw=true "Example typesetting")
