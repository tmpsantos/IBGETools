import tesseract

from PythonMagick import Blob


class OCR:
    def __init__(self):
        api = tesseract.TessBaseAPI()
        api.Init(".","eng",tesseract.OEM_DEFAULT)
        api.SetPageSegMode(tesseract.PSM_AUTO)
        api.SetVariable("tessedit_char_whitelist", "-0123456789")

        self._api = api

    def GetDecimalDegrees(self, image):
        blob = Blob()
        image.magick("JPEG")
        image.write(blob)

        tesseract.ProcessPagesBuffer(blob.data, blob.length(), self._api)
        coordinates = self._api.GetUTF8Text().split(' ')[:3]

        return self._ConvertToDecimalDegrees(coordinates)

    def _ConvertToDecimalDegrees(self, coordinates):
        degrees = float(coordinates[0])
        minutes = float(coordinates[1]) / 60
        seconds = float(coordinates[2]) / 3600

        if (degrees < 0):
            minutes *= -1
            seconds *= -1

        return degrees + minutes + seconds
