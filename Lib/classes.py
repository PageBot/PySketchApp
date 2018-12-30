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
#  classes.py
#
#  Site page opening any sketch file format:
#  https://xaviervia.github.io/sketch2json/
#
#  https://gist.github.com/xaviervia/edbea95d321feacaf0b5d8acd40614b2
#  This description is not complete. 
#  Additions made where found in the Reading specification of this context.
#
#  http://sketchplugins.com/d/87-new-file-format-in-sketch-43
#
#  This source will not import PageBot. But it is written in close
#  conntection to it, so PageBot can read/write Document and Element
#  instances into SketchApp files.
#
import os
import zipfile
import json
import re
import io

FILETYPE_SKETCH = 'sketch' # SketchApp file extension
DOCUMENT_JSON = 'document.json'
USER_JSON = 'user.json'
META_JSON = 'meta.json'
PAGES_JSON = 'pages/'
IMAGES_JSON = 'images/'
PREVIEWS_JSON = 'previews/'

# SketchApp 43 files JSON types

'''
type UUID = string // with UUID v4 format

type SketchPositionString = string // '{0.5, 0.67135115527602085}'

type SketchNestedPositionString = string // '{{0, 0}, {75.5, 15}}'

type Base64String = string

type FilePathString = string

type SketchImageCollection = {
  _class: 'imageCollection',
  images: Unknown // TODO
}
'''

def asColorNumber(v):
  try:
    return min(1, max(0, float(v)))
  except ValueError:
    return 0

def asNumber(v):
  try:
    return float(v)
  except ValueError:
    return 0

def asInt(v):
  try:
    return int(v)
  except ValueError:
    return 0

def asBool(v):
  return bool(v)

def asPoint(p):
  return p

def asId(v):
  return v

class SketchBase:

  def __init__(self, d):
    if d is None:
      d = {}
    self._class = self.CLASS # Forces values to default.
    # Expect dict of attrNames and (method_Or_SketchBaseClass, default) as value
    for attrName, (m, default) in self.ATTRS.items():
      setattr(self, attrName, m(d.get(attrName, default)))

  def __getitem__(self, attrName):
    """Allow addressing as dictionary too."""
    return getattr(self, attrName)

  def __repr__(self):
    s = ['<%s' % self._class]
    for attrName in sorted(self.ATTRS):
      s.append('%s=%s' % (attrName, getattr(self, attrName)))
    return ' '.join(s) + '>'

  def asDict(self):
    d = dict(_class=self._class)
    for attrName, (m, default) in self.ATTRS.items():
      d[attrName] = getattr(self, attrName)
    return d

class SketchColor(SketchBase):
  """
  _class: 'color',
  alpha: number,
  blue: number,
  green: number,
  red: number

  For more color functions see PageBot/toolbox/color

  >>> test = dict(red=0.5, green=0.1, blue=1)
  >>> color = SketchColor(test)
  >>> color.red
  0.5
  >>> sorted(color.asDict())
  ['_class', 'alpha', 'blue', 'green', 'red']
  """
  CLASS = 'color'
  ATTRS = {
    'red': (asColorNumber, 0),
    'green': (asColorNumber, 0),
    'blue': (asColorNumber, 0),
    'alpha': (asColorNumber, 0),
  }

class SketchBorder(SketchBase):
  """
  _class: 'border',
  isEnabled: bool,
  color: SketchColor,
  fillType: number,
  position: number,
  thickness: number

  For usage in PageBot, use equivalent PageBot/elements/Element.getBorderDict()

  >>> test = dict(color=dict(red=1))
  >>> border = SketchBorder(test)
  >>> border.color
  <color alpha=0 blue=0 green=0 red=1>
  """
  CLASS = 'border'
  ATTRS = {
    'isEnabled': (asBool, True),
    'color': (SketchColor, None),
    'fillType': (asNumber, 0),
    'position': (asInt, 0),
    'thickness': (asNumber, 1)
  }

class SketchGradientStop(SketchBase):
  """
  _class: 'gradientStop',
  color: SketchColor,
  position: number
  
  >>> test = dict(color=dict(blue=1), position=1) 
  >>> gs = SketchGradientStop(test)
  >>> gs.color, gs.position
  (<color alpha=0 blue=1 green=0 red=0>, 1)
  """
  CLASS = 'gradientStop'
  ATTRS = {
    'color': (SketchColor, None),
    'position': (asPoint, 0), 
  }

def SketchGradientStopList(dd):
  l = []
  for d in dd:
    l.append(SketchGradientStop(d))
  return l

class SketchGradient(SketchBase):
  """
  _class: 'gradient',
  elipseLength: number,
  from: SketchPositionString,
  gradientType: number,
  shouldSmoothenOpacity: bool,
  stops: [SketchGradientStop],
  to: SketchPositionString

  """
  CLASS = 'gradient'
  ATTRS = {
    'elipseLength': (asNumber, 0),
    'from_': (asPoint, None),  # Initilaizes to (0, 0)
    'gradientType': (asInt, 0),
    'shouldSmoothenOpacity': (asBool, True),
    'stops': (SketchGradientStopList, []),
    'to_': (asPoint, None),
  }
'''
type SketchGraphicsContextSettings = {
  _class: 'graphicsContextSettings',
  blendMode: number,
  opacity: number
}

type SketchInnerShadow = {
  _class: 'innerShadow',
  isEnabled: bool,
  blurRadius: number,
  color: SketchColor,
  contextSettings: SketchGraphicsContextSettings,
  offsetX: 0,
  offsetY: 1,
  spread: 0
}

type SketchFill = {
  _class: 'fill',
  isEnabled: bool,
  color: SketchColor,
  fillType: number,
  gradient: SketchGradient,
  noiseIndex: number,
  noiseIntensity: number,
  patternFillType: number,
  patternTileScale: number
}

type SketchShadow = {
  _class: 'shadow',
  isEnabled: bool,
  blurRadius: number,
  color: SketchColor,
  contextSettings: SketchGraphicsContextSettings,
  offsetX: number,
  offsetY: number,
  spread: number
}

type SketchBlur = {
  _class: 'blur',
  isEnabled: bool,
  center: SketchPositionString,
  motionAngle: number,
  radius: number,
  type: number
}

type SketchEncodedAttributes = {
  NSKern: number,
  MSAttributedStringFontAttribute: {
    _archive: Base64String,
  },
  NSParagraphStyle: {
    _archive: Base64String
  },
  NSColor: {
    _archive: Base64String
  }
}

'''

class SketchRect:
  """
  _class: 'rect',
  constrainProportions: bool,
  height: number,
  width: number,
  x: number,
  y: number
  """
  def __init__(self, d):
    self.x = d.get('x', 0)
    self.y = d.get('y', 0)
    self.w = d.get('width', 100)
    self.h = d.get('height', 100)
    self.constrainProportions = d.get('constrainProportions', False)

  def __repr__(self):
    return '<rect x=%s y=%d w=%d h=%d constain=%s>' % (self.x, self.y, self.w, self.h, self.constrainProportions)

'''
type SketchTextStyle = {
  _class: 'textStyle',
  encodedAttributes: SketchEncodedAttributes
}

type SketchBorderOptions = {
  _class: 'borderOptions',
  do_objectID: UUID,
  isEnabled: bool,
  dashPattern: [], // TODO,
  lineCapStyle: number,
  lineJoinStyle: number
}

type SketchColorControls = {
  _class: 'colorControls',
  isEnabled: bool,
  brightness: number,
  contrast: number,
  hue: number,
  saturation: number
}

type SketchStyle = {
  _class: 'style',
  blur: ?[SketchBlur],
  borders: ?[SketchBorder],
  borderOptions: ?SketchBorderOptions,
  contextSettings: ?SketchGraphicsContextSettings,
  colorControls: ?SketchColorControls,
  endDecorationType: number,
  fills: [SketchFill],
  innerShadows: [SketchInnerShadow],
  miterLimit: number,
  shadows: ?[SketchShadow],
  sharedObjectID: UUID,
  startDecorationType: number,
  textStyle: ?SketchTextStyle
}

type SketchSharedStyle = {
  _class: 'sharedStyle',
  do_objectID: UUID,
  name: string,
  value: SketchStyle
}

type SketchExportFormat = {
  _class: 'exportFormat',
  absoluteSize: number,
  fileFormat: string,
  name: string,
  namingScheme: number,
  scale: number,
  visibleScaleType: number
}

type SketchExportOptions = {
  _class: 'exportOptions',
  exportFormats: [SketchExportFormat],
  includedLayerIds: [], // TODO
  layerOptions: number,
  shouldTrim: bool
}

type SketchSharedStyleContainer = {
  _class: 'sharedStyleContainer',
  objects: [SketchSharedStyle]
}

type SketchSymbolContainer = {
  _class: 'symbolContainer',
  objects: [] // TODO
}

type SketchSharedTextStyleContainer {
  _class: 'sharedTextStyleContainer',
  objects: [SketchSharedStyle]
}

type SketchAssetsCollection = {
  _class: 'assetCollection',
  colors: [], // TODO
  gradients: [], // TODO
  imageCollection: SketchImageCollection,
  images: [] // TODO
}

type SketchMSJSONFileReference = {
  _class: 'MSJSONFileReference',
  _ref_class: 'MSImmutablePage' | 'MSImageData',
  _red: FilePathString
}

type SketchMSAttributedString = {
  _class: 'MSAttributedString',
  archivedAttributedString: {
    _archive: Base64String
  }
}

type SketchCurvePoint = {
  _class: 'curvePoint',
  do_objectID: UUID,
  cornerRadius: number,
  curveFrom: SketchPositionString,
  curveMode: number,
  curveTo: SketchPositionString,
  hasCurveFrom: bool,
  hasCurveTo: bool,
  point: SketchPositionString
}

type SketchRulerData = {
  _class: 'rulerData',
  base: number,
  guides: [] // TODO
}

type SketchText = {
  _class: 'text',
  do_objectID: UUID,
  exportOptions: SketchExportOptions,
  frame: SketchRect,
  isFlippedVertical: bool,
  isFlippedHorizontal: bool,
  isLocked: bool,
  isVisible: bool,
  layerListExpandedType: number,
  name: string,
  nameIsFixed: bool,
  originalObjectID: UUID,
  resizingType: number,
  rotation: number,
  shouldBreakMaskChain: bool,
  style: SketchStyle,
  attributedString: SketchMSAttributedString,
  automaticallyDrawOnUnderlyingPath: bool,
  dontSynchroniseWithSymbol: bool,
  glyphBounds: SketchNestedPositionString,
  heightIsClipped: bool,
  lineSpacingBehaviour: number,
  textBehaviour: number
}

type SketchShapeGroup = {
  _class: 'shapeGroup',
  do_objectID: UUID,
  exportOptions: SketchExportOptions,
  frame: SketchRect,
  isFlippedVertical: bool,
  isFlippedHorizontal: bool,
  isLocked: bool,
  isVisible: bool,
  layerListExpandedType: number,
  name: string,
  nameIsFixed: bool,
  originalObjectID: UUID,
  resizingType: number,
  rotation: number,
  shouldBreakMaskChain: bool,
  style: SketchStyle,
  hasClickThrough: bool,
  layers: [SketchLayer],
  clippingMaskMode: number,
  hasClippingMask: bool,
  windingRule: number
}

type SketchPath = {
  _class: 'path',
  isClosed: bool,
  points: [SketchCurvePoint]
}

type SketchShapePath = {
  _class: 'shapePath',
  do_objectID: UUID,
  exportOptions: SketchExportOptions,
  frame: SketchRect,
  isFlippedVertical: bool,
  isFlippedHorizontal: bool,
  isLocked: bool,
  isVisible: bool,
  layerListExpandedType: number,
  name: string,
  nameIsFixed: bool,
  resizingType: number,
  rotation: number,
  shouldBreakMaskChain: bool,
  booleanOperation: number,
  edited: bool,
  path: SketchPath
}

type SketchArtboard = {
  _class: 'artboard',
  do_objectID: UUID,
  exportOptions: SketchExportOptions,
  frame: SketchRect,
  isFlippedHorizontal: bool,
  isFlippedVertical: bool,
  isLocked: bool,
  isVisible: bool,
  layerListExpandedType: number,
  name: string,
  nameIsFixed: bool,
  resizingType: number,
  rotation: number,
  shouldBreakMaskChain: bool,
  style: SketchStyle,
  hasClickThrough: bool,
  layers: [SketchLayer],
  backgroundColor: SketchColor,
  hasBackgroundColor: bool,
  horizontalRulerData: SketchRulerData,
  includeBackgroundColorInExport: bool,
  includeInCloudUpload: bool,
  verticalRulerData: SketchRulerData
}

type SketchBitmap = {
  _class: 'bitmap',
  do_objectID: UUID,
  exportOptions: SketchExportOptions,
  frame: SketchRect,
  isFlippedHorizontal: bool,
  isFlippedVertical: bool,
  isLocked: bool,
  isVisible: bool,
  layerListExpandedType: number,
  name: string,
  nameIsFixed: bool,
  resizingType: number,
  rotation: number,
  shouldBreakMaskChain: bool,
  style: SketchStyle,
  clippingMask: SketchNestedPositionString,
  fillReplacesImage: bool,
  image: SketchMSJSONFileReference,
  nineSliceCenterRect: SketchNestedPositionString,
  nineSliceScale: SketchPositionString
}

type SketchSymbolInstance = {
  _class: 'symbolInstance',
  do_objectID: UUID,
  exportOptions: SketchExportOptions,
  frame: SketchRect,
  isFlippedHorizontal: bool,
  isFlippedVertical: bool,
  isLocked: bool,
  isVisible: bool,
  layerListExpandedType: number,
  name: string,
  nameIsFixed: bool,
  resizingType: number,
  rotation: number,
  shouldBreakMaskChain: bool,
  style: SketchStyle,
  horizontalSpacing: number,
  masterInfluenceEdgeMaxXPadding: number,
  masterInfluenceEdgeMaxYPadding: number,
  masterInfluenceEdgeMinXPadding: number,
  masterInfluenceEdgeMinYPadding: number,
  symbolID: number,
  verticalSpacing: number,
  overrides: {
    "0": {} // TODO
  }
}

type SketchGroup = {
  _class: 'group',
  do_objectID: UUID,
  exportOptions: SketchExportOptions,
  frame: SketchRect,
  isFlippedHorizontal: bool,
  isFlippedVertical: bool,
  isLocked: bool,
  isVisible: bool,
  layerListExpandedType: number,
  name: string,
  nameIsFixed: bool,
  originalObjectID: UUID,
  resizingType: number,
  rotation: number,
  shouldBreakMaskChain: bool,
  hasClickThrough: bool,
  layers: [SketchLayer]
}

type SketchRectangle = {
  _class: 'rectangle',
  do_objectID: UUID,
  exportOptions: SketchExportOptions,
  frame: SketchRect,
  isFlippedHorizontal: bool,
  isFlippedVertical: bool,
  isLocked: bool,
  isVisible: bool,
  layerListExpandedType: number,
  name: string,
  nameIsFixed: bool,
  resizingType: number,
  rotation: number,
  shouldBreakMaskChain: bool,
  booleanOperation: number,
  edited: bool,
  path: SketchPath,
  fixedRadius: number,
  hasConvertedToNewRoundCorners: bool
}

type SketchOval = {
  _class: 'oval',
  do_objectID: UUID,
  exportOptions: SketchExportOptions,
  frame: SketchRect,
  isFlippedHorizontal: bool,
  isFlippedVertical: bool,
  isLocked: bool,
  isVisible: bool,
  layerListExpandedType: number,
  name: string,
  nameIsFixed: bool,
  resizingType: number,
  rotation: number,
  shouldBreakMaskChain: bool,
  booleanOperation: number,
  edited: bool,
  path: SketchPath  
}

type SketchLayer =
  | SketchText
  | SketchShapeGroup
  | SketchShapePath
  | SketchBitmap
  | SketchArtboard
  | SketchSymbolInstance
  | SketchGroup
  | SketchRectangle
  | SketchOval

type SketchSymbolMaster = {
  backgroundColor: SketchColor,
  _class: 'symbolMaster',
  do_objectID: UUID,
  exportOptions: [SketchExportOptions],
  frame: SketchRect,
  hasBackgroundColor: bool,
  hasClickThrough: bool,
  horizontalRulerData: SketchRulerData,
  includeBackgroundColorInExport: bool,
  includeBackgroundColorInInstance: bool,
  includeInCloudUpload: bool,
  isFlippedHorizontal: bool,
  isFlippedVertical: bool,
  isLocked: bool,
  isVisible: bool,
  layerListExpandedType: number,
  layers: [SketchLayer],
  name: string,
  nameIsFixed: bool,
  resizingType: number,
  rotation: number,
  shouldBreakMaskChain: bool,
  style: SketchStyle,
  symbolID: UUID,
  verticalRulerData: SketchRulerData
}
'''
# document.json
class SketchDocument(SketchBase):
  """
  _class: 'document',
  do_objectID: UUID,
  assets: SketchAssetsCollection,
  currentPageIndex: number,
  enableLayerInteraction: bool,
  enableSliceInteraction: bool,
  foreignSymbols: [], // TODO
  layerStyles: SketchSharedStyleContainer,
  layerSymbols: SketchSymbolContainer,
  layerTextStyles: SketchSharedTextStyleContainer,
  pages: [SketchMSJSONFileReference]
  

  """
  CLASS = 'document'
  ATTRS = {
    'do_objectID': (asId, 0),
    #assets: SketchAssetsCollection,
    'currentPageIndex': (asInt, 0),
    'enableLayerInteraction': (asBool, False),
    'enableSliceInteraction': (asBool, False),
    #foreignSymbols: [], // TODO
    #'layerStyles: SketchSharedStyleContainer,
    #'layerSymbols: SketchSymbolContainer,
    #'layerTextStyles: SketchSharedTextStyleContainer,
    #'pages: [SketchMSJSONFileReference]
  }
  def __init__(self, d):
    SketchBase.__init__(self, d)
    self.pages = [] # List of SketchPage instances, filled by Pages JSON.

# pages/*.json
class SketchPage(SketchBase):
  """
  _class: 'page',
  do_objectID: UUID,
  exportOptions: SketchExportOptions,
  frame: SketchRect,
  hasClickThrough: bool,
  horizontalRulerData: SketchRulerData,
  includeInCloudUpload: bool,
  isFlippedHorizontal: bool,
  isFlippedVertical: bool,
  + isLocked: bool,
  + isVisible: bool,
  layerListExpandedType: number,
  layers: [SketchSymbolMaster],
  + name: string,
  nameIsFixed: bool,
  resizingType: number,
  rotation: number,
  shouldBreakMaskChain: bool,
  style: SketchStyle,
  verticalRulerData: SketchRulerData
}
  """
  CLASS = 'page'
  ATTRS = {
    'do_objectID': (asId, 0),    
    'frame': (SketchRect, (0, 0, 100, 100)),
    'isLocked': (asBool, False),
    'isVisible': (asBool, True),
  }
'''
// meta.json
type SketchMeta = {
  commit: string,
  appVersion: string,
  build: number,
  app: string,
  pagesAndArtboards: {
    [key: UUID]: { name: string }
  },
  fonts: [string], // Font names
  version: number,
  saveHistory: [ string ], // 'BETA.38916'
  autosaved: number,
  variant: string // 'BETA'
}

type SketchDocumentId = UUID

type SketchPageId = UUID

// user.json
type SketchUser = {
  [key: SketchPageId]: {
    scrollOrigin: SketchPositionString,
    zoomValue: number
  },
  [key: SketchDocumentId]: {
    pageListHeight: number,
    cloudShare: Unknown // TODO
  }
}

'''

if __name__ == '__main__':
  import doctest
  import sys
  sys.exit(doctest.testmod()[0])
