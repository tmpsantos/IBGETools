import os
import stat

def KMLFileWriter(kml, id, maps_list):
    kml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    kml.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    kml.write("  <Folder>\n")

    for ibge_map in maps_list:
        north = "{0:.10f}".format(ibge_map.GetY())
        south = "{0:.10f}".format(ibge_map.GetHeight() + ibge_map.GetY())
        east = "{0:.10f}".format(ibge_map.GetWidth() + ibge_map.GetX())
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



def TileScriptFileWriter(script, id, maps_list):
    # Shell script standard header
    script.write("#!/bin/sh\n\n")

    translate_options = str(
            "-co INTERLEAVE=PIXEL -co COMPRESS=LZW -co PHOTOMETRIC=RGB " \
            "-of GTiff")
    # Wild guess taken from here:
    # http://wiki.osgeo.org/wiki/Brazilian_Coordinate_Reference_Systems
    source_projection = str(
            "+datum=WGS84 +proj=latlong +ellps=GRS80 +towgs84=0,0,0 +no_defs")

    for ibge_map in maps_list:
        north = "{0:.10f}".format(ibge_map.GetY())
        south = "{0:.10f}".format(ibge_map.GetHeight() + ibge_map.GetY())
        east = "{0:.10f}".format(ibge_map.GetWidth() + ibge_map.GetX())
        west = "{0:.10f}".format(ibge_map.GetX())

        coordinates = "%s %s %s %s" % (west, north, east, south)

        basename = os.path.splitext(os.path.basename(ibge_map.GetPath()))[0]
        name = "%s_%s" % (id, basename)

        # TODO: This command translate a TIFF to a GeoTIFF. This could be done
        # by us when saving the map to image and then we could remove this step.
        script.write(
                "gdal_translate %s -a_srs '%s' -a_ullr %s %s.tif %s_geo.tif\n" %
                (translate_options, source_projection, coordinates, name, name))

    # Apparently only GDAL can read sparse files properly. It saves us a _lot_
    # of disk space when a municipality has empty areas between towns.
    merge_options = str(
            "-co COMPRESS=LZW -co TILED=YES -co SPARSE_OK=TRUE "
            "-co BLOCKXSIZE=512 -co BLOCKYSIZE=512 --config GDAL_CACHEMAX 2047")
    # I ran a few tests on this one, ranges on the images varies from 1 to 6. 2
    # was a good compromise to keep the merged file in a reasonable size.
    pixel_size = "0.000002 0.000002"

    script.write(
            "gdal_merge.py %s -ps %s -o %s.tif %s_*_geo.tif\n" %
            (merge_options, pixel_size, id, id))

    tiles_options = "-w openlayers -n"
    tiles_zoom = "5-19"

    script.write(
            "gdal2tiles.py %s -z %s -t %s %s.tif %s\n" %
            (tiles_options, tiles_zoom, id, id, id))

    script_stat = os.fstat(script.fileno())
    os.fchmod(script.fileno(), script_stat.st_mode | stat.S_IEXEC)
