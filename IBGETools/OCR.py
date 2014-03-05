# -*- coding: utf-8 -*-

import re
import tesseract

from PythonMagick import Blob


class OCR:
    def __init__(self):
        api = tesseract.TessBaseAPI()
        api.Init(".", "eng", tesseract.OEM_DEFAULT)
        api.SetPageSegMode(tesseract.PSM_AUTO)
        api.SetVariable("tessedit_char_whitelist", "-0123456789°'\"")
        api.SetVariable("chs_leading_punct", "-")
        api.SetVariable("numeric_punctuation", "-°'\"")

        self._api = api

    def GetDecimalDegrees(self, image):
        blob = Blob()

        # Remove a bit of the anti-aliasing. After this, I got better
        # results distinguishing the 3 from the 8.
        image.sharpen()
        image.sharpen()
        image.sharpen()
        image.sharpen()

        image.magick("PNG")
        image.quality(100)
        image.write(blob)

        tesseract.ProcessPagesBuffer(blob.data, blob.length(), self._api)
        text = self._api.GetUTF8Text().replace(' ', '')
        coordinates = re.split("°|'|\"| ", text)[:3]

        return self._ConvertToDecimalDegrees(coordinates)

    def _ConvertToDecimalDegrees(self, coordinates):
        try:
            degrees = float(coordinates[0])
            minutes = float(coordinates[1]) / 60
            seconds = float(coordinates[2]) / 3600
        except:
            return 0

        if (degrees > 0):
            degrees *= -1

        minutes *= -1
        seconds *= -1

        return degrees + minutes + seconds
