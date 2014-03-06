import os

def KMLFileWriter(kml_file, maps_list):
    kml_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    kml_file.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    kml_file.write("  <Folder>\n")

    for ibge_map in maps_list:
        north = "{0:.10f}".format(ibge_map.GetY())
        south = "{0:.10f}".format(ibge_map.GetHeight() + ibge_map.GetY())
        east = "{0:.10f}".format(ibge_map.GetWidth() + ibge_map.GetX())
        west = "{0:.10f}".format(ibge_map.GetX())

        basename = os.path.splitext(os.path.basename(ibge_map.GetPath()))[0]

        kml_file.write("    <GroundOverlay>\n")
        kml_file.write("      <Icon>\n")
        kml_file.write("        <href>" + "%s.png" % basename + "</href>\n")
        kml_file.write("      </Icon>\n")
        kml_file.write("      <LatLonBox>\n")
        kml_file.write("        <north>" + north + "</north>\n")
        kml_file.write("        <south>" + south + "</south>\n")
        kml_file.write("        <east>" + east + "</east>\n")
        kml_file.write("        <west>" + west + "</west>\n")
        kml_file.write("      </LatLonBox>\n")
        kml_file.write("    </GroundOverlay>\n")

    kml_file.write("  </Folder>\n")
    kml_file.write("</kml>\n")
