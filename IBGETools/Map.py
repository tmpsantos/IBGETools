from PythonMagick import Geometry, Image
from pyPdf import PdfFileReader
from OCR import OCR

# This is a naive attempt to find a generic offset and bounding box
# that should work on every map format.
_MAGIC_COORDINATE_OFFSET_ = 22
_MAGIC_COORDINATE_BBOX_WIDTH_ = 50
_MAGIC_COORDINATE_BBOX_HEIGHT_ = 15


class Map:
    def __init__(self, map_path):
        self._map_path = map_path
        self._map_image = None
        self._ocr = OCR()

        # The OCR gets a bit buggy for scale factors
        # smallers than 4.
        self._scale_factor = 4

        self._x = 0.
        self._y = 0.
        self._width = 0.
        self._height = 0.

    def IsValid(self):
        return self.WIDTH > 0

    def SetScaleFactor(self, factor):
        self._scale_factor = factor

        if self._map_image:
            self._GenerateImage()

    def GetMapImage(self):
        return self._CropGeometry(self._GetMapGeometry())

    def GetX(self):
        if self._x:
            return self._x

        map_geometry = self._GetMapGeometry()

        offset = _MAGIC_COORDINATE_OFFSET_ * self._scale_factor
        width = _MAGIC_COORDINATE_BBOX_WIDTH_ * self._scale_factor
        height = _MAGIC_COORDINATE_BBOX_HEIGHT_ * self._scale_factor

        coordinate_geometry = Geometry(width, height,
                map_geometry.xOff(), map_geometry.yOff() - offset)

        image = self._CropGeometry(coordinate_geometry)
        self._x = self._ocr.GetDecimalDegrees(image)

        return self._x

    def GetY(self):
        if self._y:
            return self._y

        map_geometry = self._GetMapGeometry()

        offset = _MAGIC_COORDINATE_OFFSET_ * self._scale_factor
        width = _MAGIC_COORDINATE_BBOX_HEIGHT_ * self._scale_factor
        height = _MAGIC_COORDINATE_BBOX_WIDTH_ * self._scale_factor

        coordinate_geometry = Geometry(width, height,
                map_geometry.xOff() - offset, map_geometry.yOff())

        image = self._CropGeometry(coordinate_geometry)
        image.rotate(90)
        self._y = self._ocr.GetDecimalDegrees(image)

        return self._y

    def _CropGeometry(self, geometry):
        if not self._map_image:
            self._GenerateImage()

        image = Image(self._map_image)
        image.crop(geometry)

        return image

    def _GetMapGeometry(self):
        width = self.WIDTH - self.MARGIN_LEFT - self.MARGIN_RIGHT
        height = self.HEIGHT - self.MARGIN_TOP - self.MARGIN_BOTTOM

        width *= self._scale_factor
        height *= self._scale_factor
        margin_left = self.MARGIN_LEFT * self._scale_factor
        margin_top = self.MARGIN_TOP * self._scale_factor

        return Geometry(width, height, margin_left, margin_top)

    def _GenerateImage(self):
        scaled_density = 72 * self._scale_factor

        self._map_image = Image()
        self._map_image.density("%dx%d" % (scaled_density, scaled_density))
        self._map_image.read(self._map_path)


class MapInvalid(Map):
    WIDTH = 0
    HEIGHT = 0

    MARGIN_LEFT = 0
    MARGIN_RIGHT = 0
    MARGIN_TOP = 0
    MARGIN_BOTTOM = 0


class MapA4Landscape(Map):
    WIDTH = 842
    HEIGHT = 595

    MARGIN_LEFT = 37
    MARGIN_RIGHT = 33
    MARGIN_TOP = 38
    MARGIN_BOTTOM = 109


class MapA3Portrait(Map):
    WIDTH = 842
    HEIGHT = 1190

    MARGIN_LEFT = 60
    MARGIN_RIGHT = 40
    MARGIN_TOP = 44
    MARGIN_BOTTOM = 168


def MapFactory(map_path):
    map_pdf = PdfFileReader(file(map_path, "rb"))

    if not map_pdf or not map_pdf.getNumPages() is 1:
        return MapInvalid(map_path)

    map_page = map_pdf.getPage(0)
    width = map_page.bleedBox.getWidth()
    height = map_page.bleedBox.getHeight()

    if (width == MapA4Landscape.WIDTH and height == MapA4Landscape.HEIGHT):
        return MapA4Landscape(map_path)
    if (width == MapA3Portrait.WIDTH and height == MapA3Portrait.HEIGHT):
        return MapA3Portrait(map_path)
    else:
        return MapInvalid(map_path)
