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
#  sketchappreader.py
#
from classes import *

class SketchAppReader(SketchAppBase):

  def read(self, path):
    """Read a sketch file and answer a SketchDocument that contains the interpreted data.

    >>> path = '../Test/TestImage.sketch'
    >>> reader = SketchAppReader()
    >>> skf = reader.read(path)
    >>> skf.document.do_objectID is not None
    True
    >>> len(skf.pages)
    1
    >>> pageId, page = sorted(skf.pages.items())[0]
    >>> page.frame, page.isLocked, page.isVisible, page.name
    ((x=0 y=0 w=0 h=0), False, True, 'Page 1')
    >>> artboard = page.layers[0]
    >>> artboard
    <artboard name=Artboard1 frame=(x=50 y=-7 w=576 h=783)>
    >>> artboard.layers
    [<shapeGroup name=Rectangle>, <bitmap name=Bitcount_cheese_e>]
    >>> bitmap = artboard.layers[1]
    >>> bitmap.frame
    (x=300 y=192 w=216 h=216 constrain=True)
    """

    assert path.endswith('.'+FILETYPE_SKETCH)
    fileName = path.split('/')[-1] # Use file name as document name and storage of images

    skf = SketchFile(path)

    # Construct the directory name to store images. Create the directory if it does not exist.
    # aPath/fileName.sketch --> aPath/fileName_images/
    # Answer the newly constructed image path.
    imagesPath = skf.imagesPath 
    if not os.path.exists(imagesPath):
      os.makedirs(imagesPath)

    zf = zipfile.ZipFile(path, mode='r') # Open the file.sketch as Zip.
    zipInfo = zf.NameToInfo

    # Set general document info
    if DOCUMENT_JSON in zipInfo:
      fc = zf.read(DOCUMENT_JSON)
      d = json.loads(fc)
      skf.document = SketchDocument(d)
    else:
      return None # Cannot readw this file.
    
    # Set general user info
    if USER_JSON in zipInfo:
      fc = zf.read(USER_JSON)
      d = json.loads(fc)
      skf.user = SketchUser(d)
    
    # Set general meta info
    if META_JSON in zipInfo:
      fc = zf.read(META_JSON)
      d = json.loads(fc)
      skf.meta = SketchMeta(d)
    
    # Read pages and build self.imagesId2Path dictionary, as we find sId-->name relations.
    for key in zipInfo:
      if key.startswith(PAGES_JSON): # This much be a page.
        fc = zf.read(key)
        sketchPageInfo = json.loads(fc)
        # Reading pages/layers will find all docment images, and store them in self.imagesId2Path
        sketchPage = SketchPage(sketchPageInfo)
        skf.pages[sketchPage['do_objectID']] = sketchPage

    # Find all imaes used in the file tree, so we can save them with their layer name.
    # Note that for now this is not a safe method, in case there are layers with
    # the same name in the document that refer to different bitmap files.
    # Also not that renaming the files in the _images/ folder, will disconnect them
    # from placements by bitmap layers.
    # TODO: Solve this later, creating unique file names.
    for image in skf.find('bitmap'): # Recursively find all bitmap layers.
      imageBinary = zf.read(image.image._ref)
      # If the image cannot be found by key, then use BitMap id as used in the file.
      # Export the image as separate file in _images directory.
      fbm = open(imagesPath + image.name + '.png', 'wb')
      fbm.write(imageBinary)
      fbm.close()

    # Save any previews in the _images/ directory too.
    # Note that there may be an potential naming conflict here, in case a layer is called 
    # "preview". TODO: To be solved later.
    for key in zipInfo:
      if key.startswith(PREVIEWS_JSON): # This is a preview image
        previewBinary = zf.read(key)
        fp = open(imagesPath + key.split('/')[-1], 'wb') # Save in _images/ folder
        fp.write(previewBinary)
        fp.close()

    return skf


if __name__ == '__main__':
  import doctest
  import sys
  sys.exit(doctest.testmod()[0])
