#!/usr/bin/python

import sys

from IBGETools.Map import MapFactory

map_path = sys.argv[1]
ibge_map = MapFactory(map_path)

if not ibge_map.IsValid():
    sys.exit(1)

ibge_map.SetScaleFactor(3)

image = ibge_map.GetMapImage()
image.write(map_path + ".gif")
