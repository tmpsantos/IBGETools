from PythonMagick import Geometry, Image
from pyPdf import PdfFileReader
from OCR import OCR

# This is a naive attempt to find a generic offset and bounding box
# that should work on every map format. The OFFSET here is the distance
# in px from the coordinates label to the the rectangle containing the map.
_MAGIC_COORDINATE_OFFSET_ = 10
_MAGIC_COORDINATE_BBOX_WIDTH_ = 50
_MAGIC_COORDINATE_BBOX_HEIGHT_ = 15


class Map:
    def __init__(self, map_path):
        self._map_path = map_path
        self._map_image = None

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

    def SetScaleFactor(self, factor):
        if factor is self._scale_factor:
            return

        self._scale_factor = factor

        if self._map_image:
            self._GenerateImage()

        self._RefreshCoordinates()

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
                map_geometry.xOff(), map_geometry.yOff() - offset - height)

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
                map_geometry.xOff() - offset - width, map_geometry.yOff())

        image = self._CropGeometry(coordinate_geometry)
        image.rotate(90)
        self._y = self._ocr.GetDecimalDegrees(image)

        return self._y

    def GetWidth(self):
        if self._width:
            return self._width

        map_geometry = self._GetMapGeometry()

        offset = _MAGIC_COORDINATE_OFFSET_ * self._scale_factor
        width = _MAGIC_COORDINATE_BBOX_WIDTH_ * self._scale_factor
        height = _MAGIC_COORDINATE_BBOX_HEIGHT_ * self._scale_factor

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

        offset = _MAGIC_COORDINATE_OFFSET_ * self._scale_factor
        width = _MAGIC_COORDINATE_BBOX_HEIGHT_ * self._scale_factor
        height = _MAGIC_COORDINATE_BBOX_WIDTH_ * self._scale_factor

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


# The WIDTH and HEIGHT corresponds to the size of the PDF page. Every document
# is expected to have a rectangle with a map inside, the MARGINs are the
# distance from the borders of this rectangle to the corner of the page.
class MapA4Portrait(Map):
    WIDTH = 595
    HEIGHT = 842

    MARGIN_LEFT = 37
    MARGIN_RIGHT = 27
    MARGIN_TOP = 33
    MARGIN_BOTTOM = 109


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


class MapA3Landscape(Map):
    WIDTH = 1190
    HEIGHT = 842

    MARGIN_LEFT = 58
    MARGIN_RIGHT = 61
    MARGIN_TOP = 51
    MARGIN_BOTTOM = 169


class MapA2Portrait(Map):
    WIDTH = 1190
    HEIGHT = 1684

    MARGIN_LEFT = 56
    MARGIN_RIGHT = 42
    MARGIN_TOP = 68
    MARGIN_BOTTOM = 216


class MapA2Landscape(Map):
    WIDTH = 1684
    HEIGHT = 1190

    MARGIN_LEFT = 56
    MARGIN_RIGHT = 59
    MARGIN_TOP = 63
    MARGIN_BOTTOM = 215


def MapFactory(map_path):
    map_pdf = PdfFileReader(file(map_path, "rb"))

    if not map_pdf or not map_pdf.getNumPages() is 1:
        return MapInvalid(map_path)

    map_page = map_pdf.getPage(0)
    width = map_page.bleedBox.getWidth()
    height = map_page.bleedBox.getHeight()

    if (width == MapA4Portrait.WIDTH and height == MapA4Portrait.HEIGHT):
        return MapA4Portrait(map_path)
    if (width == MapA4Landscape.WIDTH and height == MapA4Landscape.HEIGHT):
        return MapA4Landscape(map_path)
    if (width == MapA3Portrait.WIDTH and height == MapA3Portrait.HEIGHT):
        return MapA3Portrait(map_path)
    if (width == MapA3Landscape.WIDTH and height == MapA3Landscape.HEIGHT):
        return MapA3Landscape(map_path)
    if (width == MapA2Portrait.WIDTH and height == MapA2Portrait.HEIGHT):
        return MapA2Portrait(map_path)
    if (width == MapA2Landscape.WIDTH and height == MapA2Landscape.HEIGHT):
        return MapA2Landscape(map_path)
    else:
        return None
