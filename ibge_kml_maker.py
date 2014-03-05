#!/usr/bin/python

import fnmatch
import os
import sys

from IBGETools.Map import MapFactory


def GetMapFromPath(map_path):
    ibge_map = MapFactory(map_path)

    if not ibge_map:
        print >> sys.stderr, "Not supported: " + map_path
        return ibge_map

    # Brute force some scale factors in a attempt to get
    # the coordinated recognized by the OCR.
    if not ibge_map.IsValid():
        ibge_map.SetScaleFactor(4)

    if not ibge_map.IsValid():
        ibge_map.SetScaleFactor(5)

    if not ibge_map.IsValid():
        print >> sys.stderr, "Error parsing: " + map_path
        return None

    return ibge_map


def SaveMapImage(basename, ibge_map):
    # Restore the default scale factor before saving to disk,
    # we don't want terabytes of maps.
    ibge_map.SetScaleFactor(3)

    image = ibge_map.GetMapImage()
    image.write("%s.png" % basename)


def DumpGroundOverlay(basename, ibge_map):
    north = "{0:.10f}".format(ibge_map.GetY())
    south = "{0:.10f}".format(ibge_map.GetHeight() + ibge_map.GetY())
    east = "{0:.10f}".format(ibge_map.GetWidth() + ibge_map.GetX())
    west = "{0:.10f}".format(ibge_map.GetX())

    print "    <GroundOverlay>"
    print "      <Icon>"
    print "        <href>", "%s.png" % basename, "</href>"
    print "      </Icon>"
    print "      <LatLonBox>"
    print "        <north>", north, "</north>"
    print "        <south>", south, "</south>"
    print "        <east>", east, "</east>"
    print "        <west>", west, "</west>"
    print "      </LatLonBox>"
    print "    </GroundOverlay>"


def Main():
    if len(sys.argv) is not 2 or not os.path.isdir(sys.argv[1]):
        print >> sys.stderr, "Usage: %s <path to map pack>" % sys.argv[0]
        sys.exit(1)

    map_paths = []
    for root, _, filenames in os.walk(sys.argv[1]):
        for filename in fnmatch.filter(filenames, '[0-9]*.pdf'):
            map_paths.append(os.path.join(root, filename))

    print '<?xml version="1.0" encoding="UTF-8"?>'
    print '<kml xmlns="http://www.opengis.net/kml/2.2">'
    print "  <Folder>"

    for map_path in map_paths:
        ibge_map = GetMapFromPath(map_path)
        if not ibge_map:
            continue

        basename = os.path.splitext(os.path.basename(map_path))[0]

        SaveMapImage(basename, ibge_map)
        DumpGroundOverlay(basename, ibge_map)

    print "  </Folder>"
    print "</kml>"


if __name__ == "__main__":
    Main()
