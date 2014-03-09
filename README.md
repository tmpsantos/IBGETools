IBGETools
=========

## ibge_kml_maker.py

![alt tag](https://raw.github.com/tmpsantos/IBGETools/master/docs/screenshot.png)

### Ache o código da cidade no site do IBGE:

http://www.ibge.gov.br/home/geociencias/areaterritorial/area.shtm

Pará de Minas por exemplo é 3147105.

### Baixe o arquivo de mapas da sua cidade e descompacte:

ftp://geoftp.ibge.gov.br/mapas_estatisticos/censo_2010/mapas_de_setores_censitarios/MG/3147105.zip

Atenção! Use o arquivo do **censo_2010**.

### Instale as dependências

Testado no Ubuntu 13.10 em um Intel 64-bits:

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
$ ../ibge_kml_maker.py [path_para_os_diretorio_com_os_pdfs] > out.kml
```
Exemplo:
```
$ ../ibge_kml_maker.py ../../osm/3147105/MSU/ > out.kml
```

Usando o plugin PicLayer para o JSOM, abra o arquivo .kml.
