# -*- coding: utf-8 -*-

import re

import tesseract


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
        buffer = image.make_blob()

        tesseract.ProcessPagesBuffer(buffer, len(buffer), self._api)
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

        if (degrees < 0):
            minutes *= -1
            seconds *= -1

        return degrees + minutes + seconds
