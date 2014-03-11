import StringIO
from wand.image import Image
from pdfminer.pdfparser import PDFDocument, PDFParser, PDFStream

from OCR import OCR

# This is a naive attempt to find a generic offset and bounding box
# that should work on every map format. The OFFSET here is the distance
# in px from the coordinates label to the the rectangle containing the map.
_BBOX_OFFSET_ = 40
_BBOX_WIDTH_ = 200
_BBOX_HEIGHT_ = 40


class _Geometry:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class Map:
    def __init__(self, map_image, map_path):
        self._map_image = map_image
        self._map_path = map_path
        self._ocr = OCR()

        self._x = 0.
        self._y = 0.
        self._width = 0.
        self._height = 0.

        self.GetWidth()
        self.GetHeight()

    def IsValid(self):
        if not self._map_image:
            return False

        if self._x == 0 or self._y == 0:
            return False

        if self._width == 0 or self._height == 0:
            return False

        if self._width < 0.001 or self._width > 0.05:
            return False

        if self._height > -0.001 or self._height < -0.05:
            return False

        map_geometry = self._GetMapGeometry()

        height_pixel_ratio = self.GetHeight() / map_geometry.height
        width_pixel_ratio = self.GetWidth() / map_geometry.width

        # The ratio should not be very different from each other, otherwise
        # we OCR'ed one of the coordinates wrong.
        if (abs(height_pixel_ratio) - abs(width_pixel_ratio)) > 0.0001:
            return False

        return True

    def Dispose(self):
        self._map_image.close()
        self._map_image = None

    def GetPath(self):
        return self._map_path

    def GetMapImage(self):
        if not self.IsValid():
            return None

        # The reality here is we store a bit more than just the
        # map image, but the whole contents of the PDF including
        # the coordinates, logos, etc. So when the map is requested,
        # we need to slice it from this image.
        return self._CropGeometry(self._GetMapGeometry())

    def GetX(self):
        if self._x:
            return self._x

        map_geometry = self._GetMapGeometry()

        offset = _BBOX_OFFSET_
        width = _BBOX_WIDTH_
        height = _BBOX_HEIGHT_

        coordinate_geometry = _Geometry(map_geometry.x,
                map_geometry.y - offset - height, width, height)

        image = self._CropGeometry(coordinate_geometry)
        self._x = self._ocr.GetDecimalDegrees(image)

        return self._x

    def GetY(self):
        if self._y:
            return self._y

        map_geometry = self._GetMapGeometry()

        offset = _BBOX_OFFSET_
        width = _BBOX_HEIGHT_
        height = _BBOX_WIDTH_

        coordinate_geometry = _Geometry(map_geometry.x - offset - width,
                map_geometry.y, width, height)

        image = self._CropGeometry(coordinate_geometry)
        image.rotate(90)
        self._y = self._ocr.GetDecimalDegrees(image)

        return self._y

    def GetWidth(self):
        if self._width:
            return self._width

        map_geometry = self._GetMapGeometry()

        offset = _BBOX_OFFSET_
        width = _BBOX_WIDTH_
        height = _BBOX_HEIGHT_

        x_offset = map_geometry.x + map_geometry.width
        y_offset = map_geometry.y + map_geometry.height

        coordinate_geometry = _Geometry(x_offset - width, y_offset + offset,
                width, height)

        image = self._CropGeometry(coordinate_geometry)
        self._width = self._ocr.GetDecimalDegrees(image) - self.GetX()

        return self._width

    def GetHeight(self):
        if self._height:
            return self._height

        map_geometry = self._GetMapGeometry()

        offset = _BBOX_OFFSET_
        width = _BBOX_HEIGHT_
        height = _BBOX_WIDTH_

        x_offset = map_geometry.x + map_geometry.width
        y_offset = map_geometry.y + map_geometry.height

        coordinate_geometry = _Geometry(x_offset + offset, y_offset - height,
                width, height)

        image = self._CropGeometry(coordinate_geometry)
        image.rotate(90)
        self._height = self._ocr.GetDecimalDegrees(image) - self.GetY()

        return self._height

    def _CropGeometry(self, geometry):
        x1 = geometry.x
        y1 = geometry.y
        x2 = geometry.x + geometry.width
        y2 = geometry.y + geometry.height

        return self._map_image[x1:x2, y1:y2]

    def _GetMapGeometry(self):
        width = self.WIDTH - self.MARGIN_LEFT - self.MARGIN_RIGHT
        height = self.HEIGHT - self.MARGIN_TOP - self.MARGIN_BOTTOM

        return _Geometry(self.MARGIN_LEFT, self.MARGIN_TOP, width, height)


# The WIDTH and HEIGHT corresponds to the size of the PDF page. Every document
# is expected to have a rectangle with a map inside, the MARGINs are the
# distance from the borders of this rectangle to the corner of the page.
class MapA4Portrait(Map):
    WIDTH = 2480
    HEIGHT = 3508

    MARGIN_LEFT = 152
    MARGIN_RIGHT = 112
    MARGIN_TOP = 137
    MARGIN_BOTTOM = 452


class MapA4Landscape(Map):
    WIDTH = 3508
    HEIGHT = 2480

    MARGIN_LEFT = 153
    MARGIN_RIGHT = 135
    MARGIN_TOP = 157
    MARGIN_BOTTOM = 451


class MapA3Portrait(Map):
    WIDTH = 3508
    HEIGHT = 4961

    MARGIN_LEFT = 248
    MARGIN_RIGHT = 166
    MARGIN_TOP = 184
    MARGIN_BOTTOM = 704


class MapA3Landscape(Map):
    WIDTH = 4961
    HEIGHT = 3508

    MARGIN_LEFT = 249
    MARGIN_RIGHT = 254
    MARGIN_TOP = 213
    MARGIN_BOTTOM = 703


class MapA2Portrait(Map):
    WIDTH = 4961
    HEIGHT = 7016

    MARGIN_LEFT = 230
    MARGIN_RIGHT = 174
    MARGIN_TOP = 283
    MARGIN_BOTTOM = 899


class MapA2Landscape(Map):
    WIDTH = 7016
    HEIGHT = 4961

    MARGIN_LEFT = 230
    MARGIN_RIGHT = 242
    MARGIN_TOP = 259
    MARGIN_BOTTOM = 898


class MapA1Portrait(Map):
    WIDTH = 7016
    HEIGHT = 9933

    MARGIN_LEFT = 373
    MARGIN_RIGHT = 287
    MARGIN_TOP = 416
    MARGIN_BOTTOM = 1320


def _MakePPMImage(width, height, data):
    buffer = StringIO.StringIO()

    buffer.write("P6\n")
    buffer.write("%d %d\n" % (width, height))
    buffer.write("255\n")
    buffer.write(data)

    image = Image()
    image.read(blob=buffer.getvalue())

    return image


def MapFactory(map_path):
    try:
        map_file = file(map_path, "rb")
    except:
        return None

    document = PDFDocument()

    parser = PDFParser(map_file)
    parser.set_document(document)

    document.set_parser(parser)
    document.initialize("")

    # The image object on all IBGE PDFs is indexed
    # at ID 6. We also probe for a few properties.
    obj = document.getobj(6)
    if not obj or not isinstance(obj, PDFStream):
        return None

    if not "Width" in obj:
        return None
    if not "Height" in obj:
        return None
    if not "ColorSpace" in obj:
        return None

    width = obj["Width"]
    height = obj["Height"]
    map_class = None

    if (width == MapA4Portrait.WIDTH and height == MapA4Portrait.HEIGHT):
        map_class = MapA4Portrait
    elif (width == MapA4Landscape.WIDTH and height == MapA4Landscape.HEIGHT):
        map_class = MapA4Landscape
    elif (width == MapA3Portrait.WIDTH and height == MapA3Portrait.HEIGHT):
        map_class = MapA3Portrait
    elif (width == MapA3Landscape.WIDTH and height == MapA3Landscape.HEIGHT):
        map_class = MapA3Landscape
    elif (width == MapA2Portrait.WIDTH and height == MapA2Portrait.HEIGHT):
        map_class = MapA2Portrait
    elif (width == MapA2Landscape.WIDTH and height == MapA2Landscape.HEIGHT):
        map_class = MapA2Landscape
    elif (width == MapA1Portrait.WIDTH and height == MapA1Portrait.HEIGHT):
        map_class = MapA1Portrait
    else:
        return none

    return map_class(_MakePPMImage(width, height, obj.get_data()), map_path)
