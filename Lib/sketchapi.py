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
from sketchclasses import *
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
        self.page = None # Current selected page or artboard
        self.layer = None # Curerent selected layer

    def save(self, path):
        """Save the current self.skethFile as sketch file.

        >>> api = SketchApi()
        >>> api.selectLayer(name='Artboard 1')
        >>> api.rect(100, 100, 200, 200)
        >>> api.save('_export/Text.sketch')
        >>> api.sketchFile
        <sketchFile>
        """
        SketchAppWriter().write(path, self.sketchFile)

    def newPage(self, w=None, h=None):
        pass

    def newDrawing(self, path=None):
        pass

    def selectPage(self, index):
        """Selectt the page with this index. Answer None if the page does not exist.

        >>> api = SketchApi()
        >>> len(api.sketchFile.pages)
        1
        >>> api.selectPage(0)
        <page name=Page 1>
        >>> api.selectLayer(name='Artboard 1')
        <artboard name=Artboard 1 frame=(x=48 y=-291 w=576 h=783)>
        >>> api.rect(0, 0, 100, 100)

        """
        self.page = page = self.sketchFile.orderedPages[index]
        return page

    def selectLayer(self, _class=None, name=None, pattern=None):
        """Select the layer on the current page, indicated by _class,
        exact name or matching pattern.

        >>> api = SketchApi()
        >>> page = api.selectPage(0)
        >>> api.selectLayer(name='Artboard 1')
        <artboard name=Artboard 1 frame=(x=48 y=-291 w=576 h=783)>
        >>> api.selectLayer(pattern='board')
        <artboard name=Artboard 1 frame=(x=48 y=-291 w=576 h=783)>
        """
        if self.page is None:
            self.page = self.   selectPage(0)

        if self.page is not None:
            layers = self.page.find(_class=_class, name=name, pattern=pattern)
            if layers:
                self.layer = layers[0] # Select the first that matches.
        return self.layer

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
        """Draw the rectangle with current fill and stroke."""

        frame = dict(_class='rect', x=x, y=y, width=w, height=h)
        d = dict(frame=frame)
        g = SketchShapeGroup(d, parent=self.layer)
        g.do_objectID = newObjectID()
        self.layer.layers.append(g)

        frame = dict(_class='rect', x=0, y=0, width=w, height=h)
        d = dict(frame=frame)
        r = SketchRect(d, parent=g)
        r.do_objectID = newObjectID()

        g.layers = [r]

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


if __name__ == '__main__':
    import doctest
    import sys
    sys.exit(doctest.testmod()[0])
