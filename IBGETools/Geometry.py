class Rectangle(object):
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
