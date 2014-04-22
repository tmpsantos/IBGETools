import StringIO

from pdfminer.pdfparser import PDFDocument, PDFParser, PDFStream
from wand.api import library
from wand.image import Color, Image

from OCR import OCR
from Geometry import Rectangle

# This is a naive attempt to find a generic offset and bounding box
# that should work on every map format. The OFFSET here is the distance
# in px from the coordinates label to the the rectangle containing the map.
_BBOX_OFFSET_ = 10
_BBOX_WIDTH_ = 130
_BBOX_HEIGHT_ = 60

# The image object on all IBGE PDFs is indexed
# at ID 6. We also probe for a few properties.
_PDF_OBJ_INDEX_ = 6


def _GetMargins(image):
    width, height = image.size
    vslice = image[width / 2:width / 2 + 1, 0:height]
    hslice = image[height / 2]

    black = Color('#000')

    left = 1
    for y in hslice:
        if y == black:
            break
        left += 1

    right = 1
    for y in reversed(hslice):
        if y == black:
            break
        right += 1

    top = 1
    for row in vslice:
        if row[0] == black:
            break
        top += 1

    bottom = 1
    for row in reversed(vslice):
        if row[0] == black:
            break
        bottom += 1

    return left, top, right, bottom


class Map(Rectangle):
    def __init__(self, map_image, map_path):
        super(Map, self).__init__()

        self._map_image = map_image
        self._map_path = map_path
        self._ocr = OCR()

        self._margin_left = self.MARGIN_LEFT
        self._margin_top = self.MARGIN_TOP
        self._margin_right = self.MARGIN_RIGHT
        self._margin_bottom = self.MARGIN_BOTTOM

        self._x = OCR.INVALID_COORDINATE
        self._y = OCR.INVALID_COORDINATE
        self._width = OCR.INVALID_COORDINATE
        self._height = OCR.INVALID_COORDINATE

        self._RefreshCoordinates()

    def IsValid(self):
        if not self._map_image:
            return False

        if (self._x == OCR.INVALID_COORDINATE or
                self._y == OCR.INVALID_COORDINATE or
                self._width == OCR.INVALID_COORDINATE or
                self._height == OCR.INVALID_COORDINATE):
            return False

        if self._width < 0.001 or self._width > 1.0:
            return False

        if self._height < 0.001 or self._height > 1.0:
            return False

        _, _, width, height = self._GetMapGeometry()

        height_pixel_ratio = self.GetHeight() / height
        width_pixel_ratio = self.GetWidth() / width

        # The ratio should not be very different from each other, otherwise
        # we OCR'ed one of the coordinates wrong.
        if (abs(height_pixel_ratio) - abs(width_pixel_ratio)) > 0.0001:
            return False

        return True

    def Dispose(self):
        self._map_image.close()
        self._map_image = None
        self._ocr = None

    def GetPath(self):
        return self._map_path

    def GetMapImage(self):
        if not self.IsValid():
            return None

        # The reality here is we store a bit more than just the
        # map image, but the whole contents of the PDF including
        # the coordinates, logos, etc. So when the map is requested,
        # we need to slice it from this image.
        return self._CropGeometry(*self._GetMapGeometry())

    def GetX(self):
        if self._x != OCR.INVALID_COORDINATE:
            return self._x

        x, y, _, _ = self._GetMapGeometry()

        offset = _BBOX_OFFSET_
        width = _BBOX_WIDTH_
        height = _BBOX_HEIGHT_

        image = self._CropGeometry(x, y - offset - height, width, height)
        self._x = self._ocr.GetDecimalDegrees(image)

        return self._x

    def GetY(self):
        if self._y != OCR.INVALID_COORDINATE:
            return self._y

        x, y, _, _ = self._GetMapGeometry()

        offset = _BBOX_OFFSET_
        width = _BBOX_HEIGHT_
        height = _BBOX_WIDTH_

        image = self._CropGeometry(x - offset - width, y, width, height)
        image.rotate(90)
        self._y = self._ocr.GetDecimalDegrees(image)

        return self._y

    def GetWidth(self):
        if self._width != OCR.INVALID_COORDINATE:
            return self._width

        self._width = self._GetX2()
        if self._width != OCR.INVALID_COORDINATE:
            self._width -= self.GetX()

        return self._width

    def GetHeight(self):
        if self._height != OCR.INVALID_COORDINATE:
            return self._height

        self._height = self._GetY2()
        if self._height != OCR.INVALID_COORDINATE:
            self._height = abs(self._height - self.GetY())

        return self._height

    def SaveMapImageAsPNG(self, basename):
        image = self.GetMapImage()

        image.resize(image.width / 2, image.height / 2)
        image.save(filename="%s.png" % basename)

    def SaveMapImageAsTIFF(self, basename):
        image = self.GetMapImage()

        # If we don't add the alpha channel, the tiles will get an empty
        # black background.
        image.alpha_channel = True

        # Set compression to LZW, using the low level API here because
        # this function is not supported by the high level bindings yet.
        library.MagickSetCompression(image.wand, 11)

        # TODO: Ideally we should save as a GeoTIFF with the coordinates
        # tags. That would spare us one unnecessary step on the pipeline for
        # generating tiles.
        image.save(filename="%s.tif" % basename)

    def _GetX2(self):
        x, y, map_width, map_height = self._GetMapGeometry()

        offset = _BBOX_OFFSET_
        width = _BBOX_WIDTH_
        height = _BBOX_HEIGHT_

        x_offset = x + map_width
        y_offset = y + map_height

        image = self._CropGeometry(
                x_offset - width, y_offset + offset, width, height)

        return self._ocr.GetDecimalDegrees(image)

    def _GetY2(self):
        x, y, map_width, map_height = self._GetMapGeometry()

        offset = _BBOX_OFFSET_
        width = _BBOX_HEIGHT_
        height = _BBOX_WIDTH_

        x_offset = x + map_width
        y_offset = y + map_height

        image = self._CropGeometry(
                x_offset + offset, y_offset - height + _BBOX_OFFSET_, width, height)
        image.rotate(90)

        return self._ocr.GetDecimalDegrees(image)

    def _RefreshCoordinates(self):
        self.GetWidth()
        self.GetHeight()

        if self.IsValid():
            return

        # We have some corrupted PDFs with the top margin
        # misplaced compared to the "sane" PDFs. We try
        # to detect the margin and ultimately, interpolate
        # the upper coordinate using degrees per pixel.
        left, top, right, bottom = _GetMargins(self._map_image)

        self._margin_left = left
        self._margin_top = top
        self._margin_right = right
        self._margin_bottom = bottom

        # Margin detection can really screw up things. I'm being
        # a bit lazy here and not checking for the scenarios that
        # can go wrong. Pokemon exception handling FTW.
        try:
            self.GetWidth()
            self.GetHeight()
        except:
            return

        if self.IsValid():
            return

        y2 = self._GetY2()
        if y2 == OCR.INVALID_COORDINATE:
            return

        pixel_width = self.WIDTH - self._margin_left - self._margin_right
        pixel_height = self.HEIGHT - self._margin_top - self._margin_bottom

        self._height = self._width / float(pixel_width) * pixel_height
        self._y = y2 + self._height

    def _CropGeometry(self, x1, y1, width, height):
        x2 = x1 + width
        y2 = y1 + height

        return self._map_image[x1:x2, y1:y2]

    def _GetMapGeometry(self):
        width = self.WIDTH - self._margin_left - self._margin_right
        height = self.HEIGHT - self._margin_top - self._margin_bottom

        return self._margin_left, self._margin_top, width, height


# The WIDTH and HEIGHT corresponds to the size of the PDF page. Every document
# is expected to have a rectangle with a map inside, the MARGINs are the
# distance from the borders of this rectangle to the corner of the page.
class MapA4Portrait(Map):
    WIDTH = 2480
    HEIGHT = 3508

    MARGIN_LEFT = 249
    MARGIN_RIGHT = 248
    MARGIN_TOP = 285
    MARGIN_BOTTOM = 414


class MapA4Landscape(Map):
    WIDTH = 3508
    HEIGHT = 2480

    MARGIN_LEFT = 249
    MARGIN_RIGHT = 236
    MARGIN_TOP = 284
    MARGIN_BOTTOM = 390


class MapA3Portrait(Map):
    WIDTH = 3508
    HEIGHT = 4961

    MARGIN_LEFT = 237
    MARGIN_RIGHT = 236
    MARGIN_TOP = 268
    MARGIN_BOTTOM = 372


class MapA3Landscape(Map):
    WIDTH = 4961
    HEIGHT = 3508

    MARGIN_LEFT = 273
    MARGIN_RIGHT = 236
    MARGIN_TOP = 280
    MARGIN_BOTTOM = 385


class MapA2Portrait(Map):
    WIDTH = 4961
    HEIGHT = 7016

    MARGIN_LEFT = 250
    MARGIN_RIGHT = 242
    MARGIN_TOP = 346
    MARGIN_BOTTOM = 375


class MapA2Landscape(Map):
    WIDTH = 7016
    HEIGHT = 4961

    MARGIN_LEFT = 226
    MARGIN_RIGHT = 225
    MARGIN_TOP = 308
    MARGIN_BOTTOM = 390


class MapA1Portrait(Map):
    WIDTH = 7016
    HEIGHT = 9933

    MARGIN_LEFT = 373
    MARGIN_RIGHT = 287
    MARGIN_TOP = 416
    MARGIN_BOTTOM = 1320


class MapA1Landscape(Map):
    WIDTH = 9933
    HEIGHT = 7016

    MARGIN_LEFT = 375
    MARGIN_RIGHT = 333
    MARGIN_TOP = 335
    MARGIN_BOTTOM = 1318


def _MakePPMImage(width, height, data):
    buffer = StringIO.StringIO()

    buffer.write("P6\n")
    buffer.write("%d %d\n" % (width, height))
    buffer.write("255\n")
    buffer.write(data)

    image = Image()
    image.read(blob=buffer.getvalue())

    return image


def _ProcessWeirdPDF(document):
    # Process some weird PDFs in the SP dataset (so far)
    # which each have one object for each image scanline.
    index = _PDF_OBJ_INDEX_
    buffer = StringIO.StringIO()

    while True:
        obj = document.getobj(index)
        if not obj or not isinstance(obj, PDFStream):
            break

        buffer.write(obj.get_data())
        index += 1

    return buffer.getvalue(), index - _PDF_OBJ_INDEX_


def MapFactory(map_path):
    try:
        map_file = file(map_path, "rb")
    except:
        return None

    document = PDFDocument()

    try:
        parser = PDFParser(map_file)
        parser.set_document(document)
        document.set_parser(parser)
        document.initialize("")
    except:
        return None

    obj = document.getobj(_PDF_OBJ_INDEX_)
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

    weird_pdf = height == 1

    data = None
    if weird_pdf:
        data, height = _ProcessWeirdPDF(document)
    else:
        data = obj.get_data()

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
    elif (width == MapA1Landscape.WIDTH and height == MapA1Landscape.HEIGHT):
        map_class = MapA1Landscape
    else:
        return None

    return map_class(_MakePPMImage(width, height, data), map_path)
