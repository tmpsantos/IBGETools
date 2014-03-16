IBGETools
=========

[Looking for instructions in english? Click here.](docs/README_en.md)

![alt tag](https://raw.github.com/tmpsantos/IBGETools/master/docs/screenshot.png)

### Ache o código da cidade no site do IBGE:

http://www.ibge.gov.br/home/geociencias/areaterritorial/area.shtm

Pará de Minas por exemplo é 3147105.

### Baixe o arquivo de mapas da sua cidade e descompacte:

ftp://geoftp.ibge.gov.br/mapas_estatisticos/censo_2010/mapas_de_setores_censitarios/MG/3147105.zip

**Atenção!** Use o arquivo do censo_2010.

### Instale as dependências

Testado no Ubuntu 13.10 em um Intel 64-bits:

* python-pdfminer

`$ sudo apt-get install python-pdfminer`

* python-wand

`$ sudo apt-get install python-wand`

* python-concurrent.futures

`$ sudo apt-get install python-concurrent.futures`

* python-tesseract

Esta dependência não vem por default no Ubuntu 13.10. O pacote está disponível no link abaixo.

https://code.google.com/p/python-tesseract/downloads/list

No meu caso, instalei o python-tesseract_0.8-1.8_amd64.deb. É provável que em versões mais antigas do Ubuntu seja necessário instalar manualmente a libtesseract além dos bindings para python.

* python-gdal (apenas para --tiles)

`$ sudo apt-get install python-gdal`

* TileMill (apenas para --tiles)

Siga as intruções no link abaixo:

https://www.mapbox.com/tilemill/docs/linux-install/#terminal_installation

### Como usar a ferramenta:

```
$ git clone https://github.com/tmpsantos/IBGETools.git
$ cd IBGETools
$ mkdir out; cd out
```
#### Gerando um arquivo KML para o PicLayer ou Google Earth:
```
$ ../ibgetools --kml --id parademinas ../../osm/3147105/MSU/
```

#### Gerando tiles para abrir no browser ou layer TMS no JOSM:
```
$ ../ibgetools --tiles --id parademinas ../../osm/3147105/MSU/
$ ./parademinas.sh
```
Faça upload do arquivo .mbtiles para sua conta no Mapbox (até 50 MB é gratuito) ou crie você mesmo um servidor TileStream.

**Atenção!** O script para gerar tiles pode demorar, mas não se assuste com a estimativa de tempo inicial, porque ela está errada. Não é tão lento quanto parece.
