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
#  sketchcompare.py
#
#  Take two SketchApp files and compare them. 
#  Output an oveview of differences.
#
import os
from sketchclasses import *
from sketchappreader import SketchAppReader
from sketchappwriter import SketchAppWriter

CHECK_ID = True

IGNORE = ['userInfo']
if not CHECK_ID:
    IGNORE.append('do_objectID')

def _compare(d1, d2, result):

        if isinstance(v1, SketchBase):
            _compare(v1, v2, result)
        elif isinstance(v1, (list, tuple)):
            for index, vv1 in enumerate(v1):
                vv2 = v2[index]if 
                _compare(vv1, vv2, result)
        elif v1 != v2:
            print(attrName, v1, v2)

    for attrName in d1.ATTRS:
        v1 = getattr(d1, attrName)
        v2 = getattr(d2, attrName)
        if attrName in IGNORE:
            continue

def sketchCompare(path1, path2):
    """
    >>> from sketchappreader import SketchAppReader
    >>> testFileNames = ('TestImage.sketch',
    ...     'TestRectangles.sketch',
    ...     'TestStar.sketch',
    ...     'TestPolygon.sketch',
    ...     'TestOval.sketch',
    ...     'TestABC.sketch',
    ... )
    >>> for fileName in testFileNames:
    ...     reader = SketchAppReader()
    ...     readPath = '../Test/' + fileName
    ...     skf = reader.read(readPath)
    ...     writePath = readPath.replace('.sketch', 'Write.sketch')
    ...     writer = SketchAppWriter()
    ...     writer.write(writePath, skf)
    ...     sketchCompare(readPath, writePath) # Should not give any differences
    """
    reader = SketchAppReader()
    skf1 = reader.read(path1)
    skf2 = reader.read(path2)
    result = []
    _compare(skf1.document, skf2.document, result)
    _compare(skf1.user, skf2.user, result)
    _compare(skf1.meta, skf2.meta, result)

    if result:
        return result
    return None

if __name__ == '__main__':
    import doctest
    import sys
    sys.exit(doctest.testmod()[0])
