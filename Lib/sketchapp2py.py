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
#  sketchapp2py.py
#
from classes import *

def sketchapp2Py(path):
  """Read a sketch file and answer a SketchDocument that contains the interpreted data.

  >>> path = 'TestImage.sketch'
  >>> doc = sketchapp2Py(path)
  >>> doc.currentPageIndex
  0
  >>> doc.do_objectID is not None
  True
  >>> len(doc.pages)
  1
  >>> page = doc.pages[0]
  >>> page.frame, page.isLocked, page.isVisible
  (<rect x=0 y=0 w=0 h=0 constain=False>, False, True)
  """


  assert path.endswith('.'+FILETYPE_SKETCH)
  #fileName = path.split('/')[-1] # Use file name as document name
  #doc = doc.makeImagesPath(path) # Make local images path. Create directory if it does not exist

  f = zipfile.ZipFile(path, mode='r') # Open the file.sketch as Zip.
  zipInfo = f.NameToInfo
  # Set general document info
  if DOCUMENT_JSON in zipInfo:
    fc = f.read(DOCUMENT_JSON)
    d = json.loads(fc)
    doc = SketchDocument(d)
  else:
    return None # Cannot read
  
  # Read pages and build self.imagesId2Path dictionary, as we find sId-->name relations.
  for key in zipInfo:
    if key.startswith(PAGES_JSON): # This much be a page.
      fc = f.read(key)
      sketchPage = json.loads(fc)
      doc.pages.append(SketchPage(sketchPage))

  '''
  # Now scan images and save them as file in _local, preferrably with their original name.
  for key in zipInfo:
    if key.startswith(IMAGES_JSON): # This must be an image
      imageBinary = f.read(key)
      localImagePath = self.imagesId2Path.get(key, key.split('/')[-1])
      fh = open(localImagePath, 'wb')
      fh.write(imageBinary)
      fh.close()

  
    elif infoName.startswith(PREVIEWS_JSON):
      doc.previews.append(SketchPreview(fc))
    else:
      print('Unknown info name', infoName)
  '''
  return doc


if __name__ == '__main__':
  import doctest
  import sys
  sys.exit(doctest.testmod()[0])
