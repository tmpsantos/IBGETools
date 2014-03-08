import StringIO
from PythonMagick import Blob, Geometry, Image
from pdfminer.pdfparser import PDFDocument, PDFParser, PDFStream

from OCR import OCR

# This is a naive attempt to find a generic offset and bounding box
# that should work on every map format. The OFFSET here is the distance
# in px from the coordinates label to the the rectangle containing the map.
_MAGIC_COORDINATE_OFFSET_ = 40
_MAGIC_COORDINATE_BBOX_WIDTH_ = 200
_MAGIC_COORDINATE_BBOX_HEIGHT_ = 40


class Map:
    def __init__(self, map_image):
        self._map_image = map_image

        self._ocr = OCR()

        self._x = 0.
        self._y = 0.
        self._width = 0.
        self._height = 0.

        # The OCR gets a bit buggy for scale factors
        # smaller than 3 and bigger than 5.
        self._scale_factor = 5

        self._RefreshCoordinates()

    def IsValid(self):
        if self._x is 0 or self._y is 0:
            return False

        if self._width is 0 or self._height is 0:
            return False

        if self._width < 0.001 or self._width > 0.04:
            return False

        if self._height > -0.001 or self._height < -0.04:
            return False

        map_geometry = self._GetMapGeometry()

        height_pixel_ratio = self.GetHeight() / map_geometry.height()
        width_pixel_ratio = self.GetWidth() / map_geometry.width()

        # The ratio should not be very different from each other, otherwise
        # we OCR'ed one of the coordinates wrong.
        if (abs(height_pixel_ratio) - abs(width_pixel_ratio)) > 0.0001:
            return False

        return True

    def GetMapImage(self):
        return self._CropGeometry(self._GetMapGeometry())

    def GetX(self):
        if self._x:
            return self._x

        map_geometry = self._GetMapGeometry()

        offset = _MAGIC_COORDINATE_OFFSET_
        width = _MAGIC_COORDINATE_BBOX_WIDTH_
        height = _MAGIC_COORDINATE_BBOX_HEIGHT_

        coordinate_geometry = Geometry(width, height,
                map_geometry.xOff(), map_geometry.yOff() - offset - height)

        image = self._CropGeometry(coordinate_geometry)
        self._x = self._ocr.GetDecimalDegrees(image)

        return self._x

    def GetY(self):
        if self._y:
            return self._y

        map_geometry = self._GetMapGeometry()

        offset = _MAGIC_COORDINATE_OFFSET_
        width = _MAGIC_COORDINATE_BBOX_HEIGHT_
        height = _MAGIC_COORDINATE_BBOX_WIDTH_

        coordinate_geometry = Geometry(width, height,
                map_geometry.xOff() - offset - width, map_geometry.yOff())

        image = self._CropGeometry(coordinate_geometry)
        image.rotate(90)
        self._y = self._ocr.GetDecimalDegrees(image)

        return self._y

    def GetWidth(self):
        if self._width:
            return self._width

        map_geometry = self._GetMapGeometry()

        offset = _MAGIC_COORDINATE_OFFSET_
        width = _MAGIC_COORDINATE_BBOX_WIDTH_
        height = _MAGIC_COORDINATE_BBOX_HEIGHT_

        x_offset = map_geometry.xOff() + map_geometry.width()
        y_offset = map_geometry.yOff() + map_geometry.height()

        coordinate_geometry = Geometry(width, height,
                x_offset - width, y_offset + offset)

        image = self._CropGeometry(coordinate_geometry)
        self._width = self._ocr.GetDecimalDegrees(image) - self.GetX()

        return self._width

    def GetHeight(self):
        if self._height:
            return self._height

        map_geometry = self._GetMapGeometry()
        image = self._CropGeometry(map_geometry)

        offset = _MAGIC_COORDINATE_OFFSET_
        width = _MAGIC_COORDINATE_BBOX_HEIGHT_
        height = _MAGIC_COORDINATE_BBOX_WIDTH_

        x_offset = map_geometry.xOff() + map_geometry.width()
        y_offset = map_geometry.yOff() + map_geometry.height()

        coordinate_geometry = Geometry(width, height,
                x_offset + offset, y_offset - height)

        image = self._CropGeometry(coordinate_geometry)
        image.rotate(90)
        self._height = self._ocr.GetDecimalDegrees(image) - self.GetY()

        return self._height

    def _RefreshCoordinates(self):
        if self.IsValid():
            return

        self._x = 0.
        self._y = 0.
        self._width = 0.
        self._height = 0.

        self.GetWidth()
        self.GetHeight()

    def _CropGeometry(self, geometry):
        image = Image(self._map_image)
        image.crop(geometry)

        return image

    def _GetMapGeometry(self):
        width = self.WIDTH - self.MARGIN_LEFT - self.MARGIN_RIGHT
        height = self.HEIGHT - self.MARGIN_TOP - self.MARGIN_BOTTOM

        return Geometry(width, height, self.MARGIN_LEFT, self.MARGIN_TOP)


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


def _MakePPMImage(width, height, data):
    buffer = StringIO.StringIO()

    buffer.write("P6\n")
    buffer.write("%d %d\n" % (width, height))
    buffer.write("255\n")
    buffer.write(data)

    return Image(Blob(buffer.getvalue()))


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

    image = _MakePPMImage(width, height, obj.get_data())

    if (width == MapA4Portrait.WIDTH and height == MapA4Portrait.HEIGHT):
        return MapA4Portrait(_MakePPMImage(width, height, obj.get_data()))
    if (width == MapA4Landscape.WIDTH and height == MapA4Landscape.HEIGHT):
        return MapA4Landscape(_MakePPMImage(width, height, obj.get_data()))
    if (width == MapA3Portrait.WIDTH and height == MapA3Portrait.HEIGHT):
        return MapA3Portrait(_MakePPMImage(width, height, obj.get_data()))
    if (width == MapA3Landscape.WIDTH and height == MapA3Landscape.HEIGHT):
        return MapA3Landscape(_MakePPMImage(width, height, obj.get_data()))
    if (width == MapA2Portrait.WIDTH and height == MapA2Portrait.HEIGHT):
        return MapA2Portrait(_MakePPMImage(width, height, obj.get_data()))
    if (width == MapA2Landscape.WIDTH and height == MapA2Landscape.HEIGHT):
        return MapA2Landscape(_MakePPMImage(width, height, obj.get_data()))
    else:
        return None
