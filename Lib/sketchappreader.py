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

  def __init__(self, overwriteImages=False):
    self.overwriteImages = overwriteImages
    # Key is SketchBitmap.do_objectID, value is path of exported image file.
    self.imagesId2Path = {} 

  def makeImagesDirectory(self, path):
    """Construct the directory name to store images. Create the directory if it does not exist.
    aPath/fileName.sketch --> aPath/fileName_images/
    Answer the newly constructed image path.
    """
    exportImagesPath = '/'.join(path.split('/')[:-1]) + '/' + '.'.join(path.split('.')[:-1]) + '_images/' 
    if not os.path.exists(exportImagesPath):
      os.makedirs(exportImagesPath)
    return exportImagesPath

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
    imagesPath = self.makeImagesDirectory(path) # Make the sketchName_images/ directory if it does not exist.

    skf = SketchFile()

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

    # Now scan images and save them as file in _images, preferrably with their original name.
    # If the image already exists and self.overWriteImages is False, then keep the saved file.
    for key in zipInfo:
      if key.startswith(IMAGES_JSON): # This must be an image
        imageBinary = zf.read(key)
        # If the image cannot be found by key, then use BitMap id as used in the file.
        imageFileName = self.imagesId2Path.get(key, key.split('/')[-1])
        # Export the image as separate file in _images directory.
        fbm = open(imagesPath + imageFileName, 'wb')
        fbm.write(imageBinary)
        fbm.close()

    '''
      elif infoName.startswith(PREVIEWS_JSON):
        doc.previews.append(SketchPreview(fc))
      else:
        print('Unknown info name', infoName)
    '''
    return skf


if __name__ == '__main__':
  import doctest
  import sys
  sys.exit(doctest.testmod()[0])
