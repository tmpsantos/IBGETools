# Degrees per pixel at zoom 19:
# http://wiki.openstreetmap.org/wiki/Zoom_levels
_DEGREES_PER_PIXEL_ = 0.0005 / 256

# If we do a hit test on every pixel, it would take forever. Instead
# we do sampling. Larger the sample, faster, but we might miss some tiles.
_SAMPLE_ = _DEGREES_PER_PIXEL_ * 500


def coordinates_range(start, stop):
    while start < stop:
        yield start
        start += _SAMPLE_


class Rectangle(object):
    def __init__(self):
        self._is_visible = False

    def GetX(self):
        raise NotImplementedError()

    def GetY(self):
        raise NotImplementedError()

    def GetWidth(self):
        raise NotImplementedError()

    def GetHeight(self):
        raise NotImplementedError()

    def GetLeft(self):
        return self.GetX()

    def GetTop(self):
        return self.GetY()

    def GetRight(self):
        return self.GetLeft() + self.GetWidth()

    def GetBottom(self):
        return self.GetTop() - self.GetHeight()

    def IsVisible(self):
        return self._is_visible

    def SetVisible(self, visible):
        self._is_visible = visible

    def Contains(self, x, y):
        return (self.GetLeft() <= x <= self.GetRight() and
                self.GetBottom() <= y <= self.GetTop())

    def __gt__(self, other):
        return (abs(self.GetWidth() * self.GetHeight()) >
                abs(other.GetWidth() * other.GetHeight()))


class Region(Rectangle):
    def __init__(self):
        super(Region, self).__init__()

        self._left = None
        self._top = None
        self._right = None
        self._bottom = None

        self._rectangles = []

    def AddRectangle(self, rectangle):
        self._rectangles.append(rectangle)

        if self._left is None:
            self._left = rectangle.GetLeft()
            self._top = rectangle.GetTop()
            self._right = rectangle.GetRight()
            self._bottom = rectangle.GetBottom()
            return

        self._left = min(self._left, rectangle.GetLeft())
        self._top = max(self._top, rectangle.GetTop())
        self._right = max(self._right, rectangle.GetRight())
        self._bottom = min(self._bottom, rectangle.GetBottom())

    def FilterHiddenRectangles(self):
        rectangles = sorted(self._rectangles, reverse=True)

        # Poor man's occlusion culling.
        for x in coordinates_range(self.GetLeft(), self.GetRight()):
            for y in coordinates_range(self.GetBottom(), self.GetTop()):
                for rectangle in rectangles:
                    if rectangle.Contains(x, y):
                        rectangle.SetVisible(True)
                        break

        self._rectangles = filter(lambda x: x.IsVisible(), rectangles)

    def GetRectangles(self):
        return self._rectangles

    def GetX(self):
        return self._left

    def GetY(self):
        return self._top

    def GetWidth(self):
        return self._right - self._left

    def GetHeight(self):
        return self._top - self._bottom
