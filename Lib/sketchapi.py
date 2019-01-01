#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# -----------------------------------------------------------------------------
#
#  S K E T C H A P P 2 P Y
#
#  Copyright (c) 2016+ Buro Petr van Blokland + Claudia Mens
#  www.pagebot.io
#  Licensed under MIT conditions
#
#  Supporting DrawBot, www.drawbot.com
#  Supporting Flat, xxyxyz.org/flat
#  Supporting Sketch, https://github.com/Zahlii/python_sketch_api
# -----------------------------------------------------------------------------
#
#  sketchapi.py
#
#  This api is compatible with the context builders of PageBot.
#

import os
from sketchappreader import SketchAppReader
from sketchappwriter import SketchAppWriter

RESOURCES_PATH = '/'.join(__file__.split('/')[:-1])

class SketchApi:
    """
    >>> api = SketchApi()
    >>> api.sketchFile
    <sketchFile>
    >>> api.sketchFile.path.endswith('/Resources/Template.sketch')
    True
    """
    def __init__(self, path=None):
        if path is None:
            path = RESOURCES_PATH + '/Resources/Template.sketch'
        self.sketchFile = SketchAppReader().read(path)
    
    def save(self, path):
        """Save the current self.skethFile as sketch file.

        >>> api = SketchApi()
        >>> api.save('_export/Text.sketch')
        >>> api.sketchFile
        """
        SketchAppWriter().write(path, self.sketchFile)

    def newPage(self, w=None, h=None):
        pass

    def newDrawing(self, path=None):
        pass

    def frameDuration(self, v):
        pass

    def restore(self):
        pass

    def drawPath(self):
        pass

    def newPath(self):
        pass

    def scale(self, sx, sy):
        pass

    def translate(self, x, y):
        pass

    def moveTo(self, p):
        pass

    lineTo = moveTo

    def curveTo(self, bcp1, bcp2, p):
        pass

    def openTypeFeatures(self, **openTypeFeatures):
        pass

    def closePath(self):
        pass

    def line(self, p1, p2):
        pass

    def oval(self, x, y, w, h):
        pass

    def rect(self, x, y, w, h):
        pass

    def line(self, p1, p2):
        pass

    def fill(self, r, g=None, b=None, a=None, alpha=None):
        # Covering API inconsistencies in DrawBot
        pass

    setFillColor = setStrokeColor = stroke = fill

    def cmykFill(self, c, m=None, y=None, k=None, a=None, alpha=None):
        # Covering API inconsistencies in DrawBot
        pass

    cmykStroke = cmykFill

    def strokeWidth(self, w):
        pass

    def sizes(self):
        return dict(screen=(800, 600))

    def installedFonts(self, pattern=None):
        return []

    def font(self, font):
        pass

    def fontSize(self, fontSize):
        pass

    def textSize(self, s):
        return 10, 10

    def hyphenation(self, language):
        pass

    def image(self, path, p, pageNumber=0, alpha=None):
        pass

    def imageSize(self, path):
        """Answers the image size of our test image

        path = getResourcesPath() + '/images/peppertom_lowres_398x530.png'
        """
        return 398, 530

    def clipPath(self, clipPath):
        pass

    def numberOfImages(self, path):
        return 1

    def transform(self, t):
        pass

    def rotate(self, angle, center=None):
        pass

    def text(self, s, p):
        pass

    def textBox(self, s, r):
        pass

    def saveImage(self, path, multipage=True):
        pass

    def installFont(self, fontPath):
        self._installedFonts.append(fontPath)
        if os.path.exists(fontPath):
            return path2Name(fontPath)
        return None

    def fontName2FontPath(self, fontName):
        """We cannot tell the relation of the font name and the font path for
        DrawBot without OS X unless it is a path."""
        if os.path.exists(fontName):
            return fontName
        return None

    def FormattedString(self, s):
        class FS:
            def __init__(self, s):
                self.s = s
        return FS(s)

    def ImageObject(self, path):
        return NoneImageObject(path)

if __name__ == '__main__':
    import doctest
    import sys
    sys.exit(doctest.testmod()[0])
