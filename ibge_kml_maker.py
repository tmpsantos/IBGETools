#!/usr/bin/python

import fnmatch
import os
import sys

from wand.api import library

from IBGETools.Map import MapFactory
from IBGETools.Utils import KMLFileWriter


def ScanDirectoryForPDFs(directory):
    pdf_paths = []

    for root, _, filenames in os.walk(directory):
        # All IBGE PDFs we are interested at start with a number,
        # so we can rule out a few by filtering the file name.
        for filename in fnmatch.filter(filenames, "[0-9]*.pdf"):
            pdf_paths.append(os.path.join(root, filename))

    return pdf_paths


def GetMapFromPath(map_path):
    ibge_map = MapFactory(map_path)

    if not ibge_map:
        print >> sys.stderr, "Not supported: " + map_path
        return ibge_map

    if not ibge_map.IsValid():
        print >> sys.stderr, "Error parsing: " + map_path
        return None

    return ibge_map


def SaveMapImageAsPNG(ibge_map, basename):
    image = ibge_map.GetMapImage()

    image.resize(image.width / 2, image.height / 2)
    image.save(filename="%s.png" % basename)


def Main():
    if len(sys.argv) is not 2 or not os.path.isdir(sys.argv[1]):
        print >> sys.stderr, "Usage: %s <path to map pack>" % sys.argv[0]
        sys.exit(1)

    map_paths = ScanDirectoryForPDFs(sys.argv[1])
    map_list = []
    for map_path in map_paths:
        ibge_map = GetMapFromPath(map_path)
        if not ibge_map:
            continue

        map_list.append(ibge_map)
        basename = os.path.splitext(os.path.basename(map_path))[0]

        SaveMapImageAsPNG(ibge_map, basename)
        ibge_map.Dispose()

    KMLFileWriter(sys.stdout, map_list)


if __name__ == "__main__":
    Main()
