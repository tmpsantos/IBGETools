import os
import stat

def KMLFileWriter(kml, id, region):
    kml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    kml.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    kml.write("  <Folder>\n")

    for ibge_map in region.GetRectangles():
        north = "{0:.10f}".format(ibge_map.GetY())
        south = "{0:.10f}".format(ibge_map.GetY() - ibge_map.GetHeight())
        east = "{0:.10f}".format(ibge_map.GetX() + ibge_map.GetWidth())
        west = "{0:.10f}".format(ibge_map.GetX())

        basename = os.path.splitext(os.path.basename(ibge_map.GetPath()))[0]

        kml.write("    <GroundOverlay>\n")
        kml.write("      <Icon>\n")
        kml.write("        <href>" + "%s_%s.png" % (id, basename) + "</href>\n")
        kml.write("      </Icon>\n")
        kml.write("      <LatLonBox>\n")
        kml.write("        <north>" + north + "</north>\n")
        kml.write("        <south>" + south + "</south>\n")
        kml.write("        <east>" + east + "</east>\n")
        kml.write("        <west>" + west + "</west>\n")
        kml.write("      </LatLonBox>\n")
        kml.write("    </GroundOverlay>\n")

    kml.write("  </Folder>\n")
    kml.write("</kml>\n")



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
