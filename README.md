IBGETools
=========

![alt tag](https://raw.github.com/tmpsantos/IBGETools/master/docs/screenshot.png)

### Ache o código da cidade no site do IBGE:

http://www.ibge.gov.br/home/geociencias/areaterritorial/area.shtm

Pará de Minas por exemplo é 3147105.

### Baixe o arquivo de mapas da sua cidade e descompacte:

ftp://geoftp.ibge.gov.br/mapas_estatisticos/censo_2010/mapas_de_setores_censitarios/MG/3147105.zip

**Atenção!** Use o arquivo do censo_2010.

### Instale as dependências

Testado no Ubuntu 13.10 em um Intel 64-bits:

* python-gdal

`$ sudo apt-get install python-gdal`

* python-pdfminer

`$ sudo apt-get install python-pdfminer`

* python-wand

`$ sudo apt-get install python-wand`

* python-tesseract

Esta dependência não vem por default no Ubuntu 13.10. O pacote está disponível no link abaixo.

https://code.google.com/p/python-tesseract/downloads/list

No meu caso, instalei o python-tesseract_0.8-1.8_amd64.deb. É provável que em versões mais antigas do Ubuntu seja necessário instalar manualmente a libtesseract além dos bindings para python.

### Como usar a ferramenta:

```
$ git clone https://github.com/tmpsantos/IBGETools.git
$ cd IBGETools
$ mkdir out; cd out
```
## Gerando um arquivo KML para o PicLayer ou Google Earth:
```
$ ../ibgetools --kml --id parademinas ../../osm/3147105/MSU/
```
## Gerando tiles para abrir no browser ou layer TMS no JOSM (recomendado):
```
$ ../ibgetools --tiles --id parademinas ../../osm/3147105/MSU/
$ ./parademinas_make_tiles.sh
$ cd parademinas; python -m SimpleHTTPServer
```
Com o servidor HTTP rodando, abra o JOSM e adicione a seguinte layer TMS:
```
http://localhost:8000/{zoom}/{x}/{-y}.png
```
**Atenção!** O script make_tiles pode demorar uma eternidade.
