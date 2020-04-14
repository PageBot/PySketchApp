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
#  Write the Sketch classes into a valid Sketch file.
#
#  Inspect sketch file:
#  https://xaviervia.github.io/sketch2json/
#  https://developer.sketch.com/file-format/
#
#  https://gist.github.com/xaviervia/edbea95d321feacaf0b5d8acd40614b2
#  This description is not complete. 
#  Additions made where found in the Reading specification of this context.
#
#  Webviewer
#  https://github.com/AnimaApp/sketch-web-viewer
#
import os
from sketchapp2py.sketchclasses import *
from sketchapp2py.sketchappreader import SketchAppReader
from sketchapp2py.sketchappwriter import SketchAppWriter

RESOURCES_PATH = '/'.join(__file__.split('/')[:-1])
RESOURCES_TEMPLATE_PATH = RESOURCES_PATH + '/Resources/Template.sketch' # Default template document.

class SketchApi:
    """
    >>> api = SketchApi()
    >>> api
    <SketchApi path=Template.sketch>
    >>> api.sketchFile
    <SketchFile path=Template.sketch>
    >>> api.sketchFile.path.endswith('/Resources/Template.sketch')
    True
    >>> api.filePath == api.sketchFile.path
    True
    >>> path = 'Resources/TemplateSquare.sketch'
    >>> api = SketchApi(path)
    >>> page = api.selectPage(0)
    >>> page, api.page
    (<page name=Page 1>, <page name=Page 1>)
    >>> page.name 
    'Page 1'
    >>> len(page.layers[0]), page.artBoards, len(page.artBoards[0])
    (6, [<SketchArtboard name=Artboard 1 w=576 h=783>], 6)
    >>> artBoard = page.artBoards[0]
    >>> e = artBoard.layers[3]
    >>> e, e.name
    (<rectangle name=Rectangle Middle Right>, 'Rectangle Middle Right')
    >>> e = page.find(pattern='Top Left')[0]
    >>> e.name, e.frame
    ('Rectangle Top Left', <rect x=60 y=0 w=216 h=168>)
    >>> #e.style['fills']   
    """
    def __init__(self, path=None):
        if path is None:
            path = RESOURCES_TEMPLATE_PATH
        self.sketchFile = SketchAppReader().read(path)
        self.page = None # Current selected page or artboard
        self.layer = None # Curerent selected layer
        self._fill = None # Current fill color
        self._stroke = None # Current stroke color
        self._path = None # Current open path-plygon to add points to

    def __repr__(self):
        return '<%s path=%s>' % (self.__class__.__name__, self.sketchFile.path.split('/')[-1])

    def _get_filePath(self):
        return self.sketchFile.path
    filePath = property(_get_filePath)

    def _getFill(self, **kwargs):
        fill = kwargs.get('fill', self._fill) or BLACK_COLOR
        assert len(fill) in (3, 4)
        if len(fill) == 3:
            r, g, b = fill
            return SketchColor(red=r, green=g, blue=b)
        r, g, b, a = fill
        return SketchColor(red=r, green=g, blue=b, alpha=a)

    def _getStyle(self, **kwargs):
        style = SketchStyle()
        style.fills = [self._getFill(**kwargs)]
        return style

    def save(self, path=None):
        """Save the current self.skethFile as sketch file.

        >>> if not os.path.exists('_export'):
        ...     os.mkdir('_export')
        >>> api = SketchApi()
        >>> api.selectLayer(name='Artboard 1')
        <SketchArtboard name=Artboard 1 w=576 h=783>
        >>> api.rect(x=100, y=110, width=200, height=210, name='Rectangle')
        <shapeGroup name=Rectangle>
        >>> api.save('_export/Save.sketch')
        >>> api.sketchFile
        <SketchFile path=Template.sketch>
        """
        if path is None:
            path = self.path
        SketchAppWriter().write(path, self.sketchFile)

    def newPage(self, w=None, h=None):
        pass

    def newDrawing(self, path=None):
        pass

    def newGroup(self, x=None, y=None, w=None, h=None, name=None, **kwargs):
        """
        >>> api = SketchApi()
        >>> page = api.selectPage(0)
        >>> layers = api.selectLayer(name='Artboard 1').layers
        >>> len(layers)
        0
        >>> g = api.newGroup(10, 20, 110, 120, fill=(0,0, 0.5))
        >>> len(layers)
        1
        >>> g.style.fills[0]
        <color red=0 green=0 blue=0.5 alpha=0>
        """
        assert self.layer is not None
        if w is None:
            w = DEFAULT_WIDTH
        if h is None:
            h = DEFAULT_HEIGHT

        style = self._getStyle(**kwargs)
        frame = SketchRect(x=x or 0, y=y or 0, width=w, height=h)
        name = name or DEFAULT_NAME
        g = SketchGroup(do_objectID=newObjectID(), style=style, frame=frame, name=name, **kwargs)
        self.layer.append(g)
        return g

    def selectPage(self, index):
        """Selectt the page with this index. Answer None if the page does not exist.

        >>> api = SketchApi()
        >>> len(api.sketchFile.pages)
        1
        >>> api.selectPage(0)
        <page name=Page 1>
        >>> api.selectLayer(name='Artboard 1')
        <SketchArtboard name=Artboard 1 w=576 h=783>
        >>> r = api.rect(x=0, y=0, width=100, height=100)
        >>> api.save('_export/SelectPage.sketch')
        """
        self.page = page = self.sketchFile.orderedPages[index]
        return page

    def selectLayer(self, _class=None, name=None, pattern=None):
        """Select the layer on the current page, indicated by _class,
        exact name or matching pattern.

        >>> api = SketchApi()
        >>> page = api.selectPage(0)
        >>> api.selectLayer(name='Artboard 1')
        <SketchArtboard name=Artboard 1 w=576 h=783>
        >>> artboard = api.selectLayer(pattern='board')
        >>> artboard
        <SketchArtboard name=Artboard 1 w=576 h=783>
        """
        if self.page is None:
            self.page = self.selectPage(0)

        if self.page is not None:
            layers = self.page.find(_class=_class, name=name, pattern=pattern)
            if layers:
                self.layer = layers[0] # Select the first that matches.
        return self.layer

    def getSize(self):
        w = h = 0
        for page in self.getPages():
            for artboard in page.layers:
                w = max(w, artboard.frame.width - artboard.frame.x)
                h = max(h, artboard.frame.height - artboard.frame.y)
        return w, h

    def getPages(self):
        """Answer the list of SketchPage instances.

        >>> api = SketchApi()
        >>> api.getPages()
        [<page name=Page 1>]
        """
        return self.sketchFile.orderedPages

    def getArtboards(self):
        """Answer the list of artboards on the current page.

        """
        if self.page is None:
            self.page = self.selectPage(0)

        if self.page is not None:
            return self.page.find(_class=SketchArtboard)
        return []

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

    def oval(self, x, y, w, h, name=None, **kwargs):
        """Draw the oval with current fill and stroke.

        >>> api = SketchApi()
        >>> page = api.selectPage(0)
        >>> api.selectLayer(name='Artboard 1')
        <SketchArtboard name=Artboard 1 w=576 h=783>
        >>> artboard = api.selectLayer(pattern='board')
        >>> artboard
        <SketchArtboard name=Artboard 1 w=576 h=783>
        >>> layers = artboard.layers
        >>> len(layers)
        0
        >>> g = api.oval(100, 110, 200, 210, fill=(1, 0, 0.5, 0.25))
        >>> len(layers)
        1
        >>> layers[0].style.fills
        [<color red=1 green=0 blue=0.5 alpha=0.25>]
        """
        if w is None:
            w = DEFAULT_WIDTH
        if h is None:
            h = DEFAULT_HEIGHT

        style = self._getStyle(**kwargs)
        frame = dict(_class='rect', x=x, y=x, width=w, height=h)
        name = name or DEFAULT_NAME
        g = SketchShapeGroup(do_objectID=newObjectID(), style=style, frame=frame, 
            name=name, **kwargs)
        self.layer.append(g)

        rFrame = dict(_class='rect', x=0, y=0, width=w, height=h)
        r = SketchOval(parent=g, frame=rFrame, do_objectID=newObjectID(), name='Path')
        r.points = [
            SketchCurvePoint(parent=r, curveFrom='{0, 0}', curveTo='{0, 0}', point='{0, 0}'),
            SketchCurvePoint(parent=r, curveFrom='{1, 0}', curveTo='{1, 0}', point='{1, 0}'),
            SketchCurvePoint(parent=r, curveFrom='{1, 1}', curveTo='{1, 1}', point='{1, 1}'),
            SketchCurvePoint(parent=r, curveFrom='{0, 1}', curveTo='{1, 1}', point='{0, 1}'),
        ]
        g.layers.append(r)
        return g

    def rect(self, x=None, y=None, w=None, h=None, name=None, **kwargs):
        """Draw the rectangle with current fill and stroke.

        >>> api = SketchApi()
        >>> page = api.selectPage(0)
        >>> api.selectLayer(name='Artboard 1')
        <SketchArtboard name=Artboard 1 w=576 h=783>
        >>> artboard = api.selectLayer(pattern='board')
        >>> artboard
        <SketchArtboard name=Artboard 1 w=576 h=783>
        >>> layers = artboard.layers
        >>> len(layers)
        0
        >>> r = api.rect(100, 110, 200, 210, fill=(1, 0, 0, 0.5))
        >>> len(layers)
        1
        >>> r.style.fills
        [<color red=1 green=0 blue=0 alpha=0.5>]
        """
        if w is None:
            w = DEFAULT_WIDTH
        if h is None:
            h = DEFAULT_HEIGHT

        style = self._getStyle(**kwargs)
        frame = dict(_class='rect', x=x, y=x, width=w, height=h)
        name = name or DEFAULT_NAME
        g = SketchShapeGroup(do_objectID=newObjectID(), style=style, frame=frame, 
            name=name, **kwargs)
        self.layer.append(g)

        rFrame = dict(_class='rect', x=0, y=0, width=w, height=h)
        r = SketchRectangle(parent=g, frame=rFrame, do_objectID=newObjectID(), name='Path')
        r.points = [
            SketchCurvePoint(parent=r, curveFrom='{0, 0}', curveTo='{0, 0}', point='{0, 0}'),
            SketchCurvePoint(parent=r, curveFrom='{1, 0}', curveTo='{1, 0}', point='{1, 0}'),
            SketchCurvePoint(parent=r, curveFrom='{1, 1}', curveTo='{1, 1}', point='{1, 1}'),
            SketchCurvePoint(parent=r, curveFrom='{0, 1}', curveTo='{1, 1}', point='{0, 1}'),
        ]
        g.layers.append(r)
        return g

    def fill(self, r, g=None, b=None, a=None):
        # Covering API inconsistencies in DrawBot
        if g is not None or b is not None:
            assert not isinstance(r, (tuple, list))
            r, g, b = r or 0, g or 0, b or 0
        elif isinstance(r, (list, tuple)):
            if len(r) == 3:
                r, g, b = r
            elif len(r) == 4:
                r, g, b, a = r
            else:
                raise ValueError
        self._fill = r, g, b, a

    setFillColor = setStrokeColor = stroke = fill

    def cmykFill(self, c, m=None, y=None, k=None, a=None):
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
