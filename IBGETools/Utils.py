import os
import stat

from jinja2 import Environment, FileSystemLoader


def _GetJinjaTemplate(name):
    this_directory = os.path.dirname(os.path.realpath(__file__))
    templates_directory = os.path.join(this_directory, "templates")
    environment = Environment(loader=FileSystemLoader(templates_directory))

    return environment.get_template(name)


def KMLFileWriter(kml, id, region):
    def ItemList():
        for ibge_map in region.GetRectangles():
            basename = os.path.splitext(os.path.basename(ibge_map.GetPath()))[0]
            href = "%s_%s.png" % (id, basename)

            item = {"href": href,
                    "north": ibge_map.GetTop(),
                    "south": ibge_map.GetBottom(),
                    "east": ibge_map.GetRight(),
                    "west": ibge_map.GetLeft()}

            yield item

    template = _GetJinjaTemplate("kml.jinja")
    kml.write(template.render(item_list=ItemList()))


def TileScriptFileWriter(script, id, region):
    # Shell script standard header
    script.write("#!/bin/sh\n\n")

    translate_options = "-of vrt"
    # Wild guess taken from here:
    # http://wiki.osgeo.org/wiki/Brazilian_Coordinate_Reference_Systems
    source_projection = str(
            "+datum=WGS84 +proj=latlong +ellps=GRS80 +towgs84=0,0,0 +no_defs")

    current_path = os.getcwd()

    for ibge_map in region.GetRectangles():
        north = "{0:.10f}".format(ibge_map.GetY())
        south = "{0:.10f}".format(ibge_map.GetY() - ibge_map.GetHeight())
        east = "{0:.10f}".format(ibge_map.GetX() + ibge_map.GetWidth())
        west = "{0:.10f}".format(ibge_map.GetX())

        coordinates = "%s %s %s %s" % (west, north, east, south)

        # Use absolute paths on the .vrt files so tools like TileMill can
        # open it. GDAL doesn't have this limitation.
        basename = os.path.splitext(os.path.basename(ibge_map.GetPath()))[0]
        name = os.path.join(current_path, "%s_%s" % (id, basename))

        script.write(
                "gdal_translate %s -a_srs '%s' -a_ullr %s %s.tif %s.vrt\n" %
                (translate_options, source_projection, coordinates, name, name))

    merge_options = "-resolution highest"
    script.write(
            "gdalbuildvrt %s -o %s.vrt %s_*.vrt\n" %
            (merge_options, id, os.path.join(current_path, id)))

    # TODO: Create the project file

    north = "{0:.10f}".format(region.GetTop())
    south = "{0:.10f}".format(region.GetBottom())
    east = "{0:.10f}".format(region.GetRight())
    west = "{0:.10f}".format(region.GetLeft())

    bbox = "%s,%s,%s,%s" % (west, south, east, north)

    tiles_options = str(
            "export %s %s.mbtiles --format=mbtiles --metatile=16" % (id, id))
    tiles_zoom = "--minzoom=8 --maxzoom=19"

    script.write(
            "node /usr/share/tilemill/index.js %s %s --bbox=%s\n" %
            (tiles_options, tiles_zoom, bbox))

    script_stat = os.fstat(script.fileno())
    os.fchmod(script.fileno(), script_stat.st_mode | stat.S_IEXEC)
