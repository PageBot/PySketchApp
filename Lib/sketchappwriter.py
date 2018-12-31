#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# -----------------------------------------------------------------------------
#
#  P Y 2 S K E T C H A P P 2 P Y
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
#  sketchappwriter.py
#
#  Write the Sketch classes into a valid Sketch file.
#
#  Inspect sketch file:
#  https://xaviervia.github.io/sketch2json/
#
#  https://gist.github.com/xaviervia/edbea95d321feacaf0b5d8acd40614b2
#  This description is not complete. 
#  Additions made where found in the Reading specification of this context.
#
from classes import *

class SketchAppWriter(SketchAppBase):
  """
  >>> from sketchappreader import SketchAppReader
  >>> readPath = '../Test/TestImage.sketch'
  >>> reader = SketchAppReader()
  >>> skf = reader.read(readPath)
  >>> skf
  <sketchFile>
  >>> writePath = '../Test/TestImageWrite.sketch'
  >>> writer = SketchAppWriter()
  >>> writer.write(writePath, skf)
  """

  def write(self, path, sketchFile):
    zf = zipfile.ZipFile(path, mode='w') # Open the file.sketch as Zip.

    tmpPath = '/tmp/'+DOCUMENT_JSON
    f = open(tmpPath, 'w')
    d = sketchFile.document.asJson()
    ds = json.dumps(d)
    f.write(ds)
    f.close()
    zf.write(tmpPath, arcname=DOCUMENT_JSON)
    os.remove(tmpPath)

    tmpPath = '/tmp/'+USER_JSON
    f = open(tmpPath, 'w')
    d = sketchFile.user.asJson()
    ds = json.dumps(d)
    f.write(ds)
    f.close()
    zf.write(tmpPath, arcname=USER_JSON)
    #os.remove(tmpPath)

    tmpPath = '/tmp/'+META_JSON
    f = open(tmpPath, 'w')
    d = sketchFile.meta.asJson()
    ds = json.dumps(d)
    f.write(ds)
    f.close()
    zf.write(tmpPath, arcname=META_JSON)
    os.remove(tmpPath)

    for pageId, page in sorted(sketchFile.pages.items()):
      tmpPath = '/tmp/pages_'+pageId+'.json'
      f = open(tmpPath, 'w')
      d = page.asJson()
      ds = json.dumps(d)
      f.write(ds)
      f.close()

      zf.write(tmpPath, arcname='pages/'+pageId+'.json')
      os.remove(tmpPath)


    # Recursively find all images in the node tree, so we can reconstruct
    # the internal file name from external file name (in _images/)
    imagesPath = sketchFile.imagesPath
    for image in sketchFile.find('bitmap'): # Recursively find all bitmap layers
      zf.write(imagesPath + image.name + '.png', arcname=image.image._ref)

    zf.close()


if __name__ == '__main__':
  import doctest
  import sys
  sys.exit(doctest.testmod()[0])
