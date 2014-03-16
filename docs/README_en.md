IBGETools
=========

![alt tag](https://raw.github.com/tmpsantos/IBGETools/master/docs/screenshot.png)

### Find out the id for your city at the IBGE website:

http://www.ibge.gov.br/home/geociencias/areaterritorial/area.shtm

Pará de Minas for instance is 3147105.

### Download the PDF pack and unzip:

ftp://geoftp.ibge.gov.br/mapas_estatisticos/censo_2010/mapas_de_setores_censitarios/MG/3147105.zip

**Warning!** "MG" on this URL stands for the state, change it accordingly.

### Install the script dependencies:

Tested on Ubuntu 13.10 Intel 64-bits:

* python-jinja2

`$ sudo apt-get install python-jinja2`

* python-pdfminer

`$ sudo apt-get install python-pdfminer`

* python-wand

`$ sudo apt-get install python-wand`

* python-concurrent.futures

`$ sudo apt-get install python-concurrent.futures`

* python-tesseract

This dependency is not availiable by default on the Ubuntu 13.10 repositories. Install it from the link below.

https://code.google.com/p/python-tesseract/downloads/list

* python-gdal (for --tiles only)

`$ sudo apt-get install python-gdal`

* TileMill (for --tiles only)

Follow the instructions of the link below.

https://www.mapbox.com/tilemill/docs/linux-install/#terminal_installation

### How to use the tool:

```
$ git clone https://github.com/tmpsantos/IBGETools.git
$ cd IBGETools
$ mkdir out; cd out
```
#### Generating a KML file for PicLayer or Google Earth:
```
$ ../ibgetools --kml --id parademinas ../../osm/3147105/MSU/
```

#### Generating tiles to use as TMS layer or visualize on a web browser:
```
$ ../ibgetools --tiles --id parademinas ../../osm/3147105/MSU/
$ ./parademinas.sh
```
You can upload the .mbtiles file to a free Mapbox account (up to 50 MB) or you can self-host using TileStream.

**Warning!** The tile generation script can take a while, but don't be scared of the ETA. It is not exactly right and will get reasonable after a few minutes.
