#!/usr/bin/python

import sys
import os

from IBGETools.Map import MapFactory

map_path = sys.argv[1]
ibge_map = MapFactory(map_path)

if not ibge_map:
    sys.exit(1)

if not ibge_map.IsValid():
    ibge_map.SetScaleFactor(3)

if not ibge_map.IsValid():
    ibge_map.SetScaleFactor(5)

if not ibge_map.IsValid():
    print "Error parsing: " + map_path
