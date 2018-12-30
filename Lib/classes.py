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
#  Webviewer
#  https://github.com/AnimaApp/sketch-web-viewer
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


type Base64String = string

type FilePathString = string

'''

POINT_PATTERN = re.compile('\{([0-9\.\-]*), ([0-9\.\-]*)\}')
  # type SketchPositionString = string // '{0.5, 0.67135115527602085}'

class Point:
  def __init__(p, bcp1=None, bcp2=None):
    self.p = p # Set by property
    self.bcp1 = bcp1
    self.bcp2 = bcp2

  def _get_p(self):
    return self.x, self.y
  def _set_p(self, p):
    self.x, self.y = p
  p = property(_get_p, _set_p)

  def _get_bcp1(self):
    bcp = self.bcp1x, self.bcp1y
    if None in bcp:
      return None
    return bcp
  def _set_bcp1(self, bcp):
    if bcp is None:
      bcp = None, None
    self.bcp1x, self.bcp1y = bcp
  bcp1 = property(_get_bcp1, _set_bcp1)

  def _get_bcp2(self):
    bcp = self.bcp2x, self.bcp2y
    if None in bcp:
      return None
    return bcp
  def _set_bcp2(self, bcp):
    if bcp is None:
      bcp = None, None
    self.bcp2x, self.bcp2y = bcp
  bcp2 = property(_get_bcp2, _set_bcp2)

def asPoint(self, sketchPoint):
  """Interpret the {x,y} string into a point2D.

  >>> context = SketchContext()
  >>> context._SketchPoint2Point('{0, 0}')
  (0, 0)
  >>> context._SketchPoint2Point('{0000021, -12345}')
  (21, -12345)
  >>> context._SketchPoint2Point('{10.05, -10.66}')
  (10.05, -10.66)
  """
  sx, sy = self.POINT_PATTERN.findall(sketchPoint)[0]
  return Point((asNumber(sx), asNumber(sy)))

def asCurvePoint(self, sketchCurvePoint):
  """
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
  """
  return str(sketchCurvePoint)
  points = []
  if sketchCurvePoint['hasCurveFrom']:
    points.append(self._SketchPoint2Point(sketchCurvePoint['curveFrom']))
  if sketchCurvePoint['hasCurveTo']:
    points.append(self._SketchPoint2Point(sketchCurvePoint['curveTo']))
  points.append(self._SketchPoint2Point(sketchCurvePoint['point']))
  #print(points, sketchCurvePoint)
  return Point()

def asRect(sketchNestedPositionString):
  """
  type SketchNestedPositionString = string // '{{0, 0}, {75.5, 15}}'
  """
  if sketchNestedPositionString is None:
    return None
  (x, y), (w, h) = POINT_PATTERN.findall(sketchNestedPositionString)
  return x, y, w, h

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

def asString(v):
  return str(v)

def asColorList(v):
  return []

def asGradientList(v):
  return []

def asImageCollection(v):
  return []

def asImages(v):
  return []

def asDict(v):
  return {}

def asList(v):
  return list(v)

class SketchAppBase:
  """Base class for SketchAppReader and SketchAppWriter"""

class SketchBase:

  REPR_ATTRS = ['name'] # Attributes to be show in __repr__

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
    for attrName in self.REPR_ATTRS:
      if hasattr(self, attrName):
        s.append('%s=%s' % (attrName, getattr(self, attrName)))
    return ' '.join(s) + '>'

  def asDict(self):
    d = dict(_class=self._class)
    for attrName, (m, default) in self.ATTRS.items():
      d[attrName] = getattr(self, attrName)
    return d

  def asJson(self):
    d = {}
    for attrName in self.ATTRS.keys():
      attr = getattr(self, attrName)
      if isinstance(attr, (list, tuple)):
        l = [] 
        for e in attr:
          if hasattr(e, 'asJson'):
            l.append(e.asJson())
        attr = l
      elif hasattr(attr, 'asJson'):
        attr = attr.asJson()
      if attr is not None:
        assert isinstance(attr, (dict, int, float, list, tuple, str)), attr
        d[attrName] = attr
    if not d:
      return None
    d['_class'] = self.CLASS
    return d

class SketchLayer(SketchBase):

  def __init__(self, d):
    SketchBase.__init__(self, d)
    self.layers = [] # List of Sketch element instances.
    for layer in d.get('layers', []):
      self.layers.append(SKETCHLAYER_PY[layer['_class']](layer))

class SketchImageCollection(SketchBase):
  """
  _class: 'imageCollection',
  images: Unknown // TODO
  """
  CLASS = 'imageCollection'
  ATTRS = {
    'images': (asDict, {})
  }

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
  REPR_ATTRS = ['red', 'green', 'blue', 'alpha'] # Attributes to be show in __repr__
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
  <color red=1 green=0 blue=0 alpha=0>
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
  (<color red=0 green=0 blue=1 alpha=0>, 1)
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
'''

class SketchEncodedAttributes(SketchBase):
  """
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
  """
  CLASS = 'sketchEncodedAttributes'
  ATTRS = {}

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
    if d is None:
      d = dict(x=0, y=0, w=0, h=0)
    self.x = d.get('x', 0)
    self.y = d.get('y', 0)
    self.w = d.get('width', 100)
    self.h = d.get('height', 100)
    self.constrainProportions = d.get('constrainProportions', False)

  def __repr__(self):
    s = '(x=%s y=%d w=%d h=%d' % (self.x, self.y, self.w, self.h)
    if self.constrainProportions:
       s += ' constrain=True'
    return s + ')'

  def asJson(self):
    return dict(x=self.x, y=self.y, width=self.w, heigh=self.h, constrainProportions=self.constrainProportions)

class SketchTextStyle(SketchBase):
  """
  _class: 'textStyle',
  encodedAttributes: SketchEncodedAttributes
  """
  CLASS = 'textStyle'
  ATTRS = {
    'encodedAttributes': (SketchEncodedAttributes, None),
  }

class SketchBorderOptions(SketchBase):
  """
  _class: 'borderOptions',
  do_objectID: UUID,
  isEnabled: bool,
  dashPattern: [], // TODO,
  lineCapStyle: number,
  lineJoinStyle: number
  """
  CLASS = 'borderOptions'
  ATTRS = {
    'do_objectID': (asId, 0),
    'isEnabled': (asBool, True),
    'dashPattern': (asString, ''),
    'lineCapStyle': (asNumber, 0),
    'lineJoinStyle': (asNumber, 0),
  }

class SketchColorControls(SketchBase):
  """
  _class: 'colorControls',
  isEnabled: bool,
  brightness: number,
  contrast: number,
  hue: number,
  saturation: number
  """
  CLASS = 'colorConstrols'
  ATTRS = {

  }

class SketchStyle(SketchBase):
  """
  _class: 'style',
  blur: ?[SketchBlur],
  borders: ?[SketchBorder],
  borderOptions: ?SketchBorderOptions,
  contextSettings: ?SketchGraphicsContextSettings,
  colorControls: ?SketchColorControls,
  endDecorationType: number,
  fills: [SketchFill],
  innerShadows: [SketchInnerShadow],
  + miterLimit: number,
  shadows: ?[SketchShadow],
  sharedObjectID: UUID,
  startDecorationType: number,
  textStyle: ?SketchTextStyle
  + endMarkerType: number,
  + startMarkerType: number,
  + windingRule: number,
  """
  CLASS = 'style'
  ATTRS = {
    'endMarkerType': (asInt, 0),
    'miterLimit': (asInt, 10),
    'startMarkerType': (asInt, 0),
    'windingRule': (asInt, 1)
  }

class SketchSharedStyle(SketchBase):
  """
  _class: 'sharedStyle',
  do_objectID: UUID,
  name: string,
  value: SketchStyle
  """
  CLASS = 'sharedStyle'
  ATTRS = {

  }

class SketchExportFormat(SketchBase):
  """
  _class: 'exportFormat',
  absoluteSize: number,
  fileFormat: string,
  name: string,
  namingScheme: number,
  scale: number,
  visibleScaleType: number
  """
  CLASS = 'exportFormat'
  ATTRS = {

  }

class SketchExportOptions(SketchBase):
  """
  _class: 'exportOptions',
  exportFormats: [SketchExportFormat],
  includedLayerIds: [], // TODO
  layerOptions: number,
  shouldTrim: bool
  """
  CLASS = 'exportOptions'
  ATTRS = {

  }

class SketchSharedStyleContainer(SketchBase):
  """
  _class: 'sharedStyleContainer',
  objects: [SketchSharedStyle]
  """
  CLASS = 'sharedStyleContainer'
  ATTRS = {
    'objects': (asList, []),
  }

class SketchSymbolContainer(SketchBase):
  """
  _class: 'symbolContainer',
  objects: [] // TODO
  """
  CLASS = 'symbolContainer'
  ATTRS = {
    'objects': (asList, []),
  }

class SketchSharedTextStyleContainer(SketchBase):
  """
  _class: 'sharedTextStyleContainer',
  objects: [SketchSharedStyle]
  """
  CLASS = 'sharedTextStyleContainer'
  ATTRS = {
    'objects': (asList, []),
  }

class SketchAssetsCollection(SketchBase):
  """
  _class: 'assetCollection',
  colors: [], // TODO
  gradients: [], // TODO
  imageCollection: SketchImageCollection,
  images: [] // TODO
  """
  CLASS = 'assetCollection'
  ATTRS = {
    'colors': (asColorList, []),
    'gradients': (asGradientList, []),
    'imageCollection': (SketchImageCollection, []),
    'images': (asImages, []),
  }

def SketchMSJSONFileReferenceList(refs):
  l = []
  for ref in refs:
    l.append(SketchMSJSONFileReference(ref))
  return l

class SketchMSJSONFileReference(SketchBase):
  """
  _class: 'MSJSONFileReference',
  _ref_class: 'MSImmutablePage' | 'MSImageData',
  _ref: FilePathString
  """
  CLASS = 'MSJSONFileReference'
  ATTRS = {
    '_ref_class': (asString, 'MSImmutablePage'),
    '_ref': (asString, ''),
  }

class SketchMSAttributedString(SketchBase):
  """
  _class: 'MSAttributedString',
  archivedAttributedString: {
    _archive: Base64String
  }
  """
  CLASS = 'MSAttributedString'
  ATTRS = {

  }

class SketchCurvePoint(SketchBase):
  """
  _class: 'curvePoint',
  do_objectID: UUID,
  cornerRadius: number,
  curveFrom: SketchPositionString,
  curveMode: number,
  curveTo: SketchPositionString,
  hasCurveFrom: bool,
  hasCurveTo: bool,
  point: SketchPositionString
  """
  CLASS = 'curvePoint'
  ATTRS = {

  }

class SketchRulerData(SketchBase):
  """
  _class: 'rulerData',
  base: number,
  guides: [] // TODO
  """
  CLASS = 'rulerData'
  ATTRS = {

  }

class SketchText(SketchBase):
  """
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
  """
  CLASS = 'text'
  ATTRS = {

  }

class SketchShapeGroup(SketchLayer):
  """
  _class: 'shapeGroup',
  + do_objectID: UUID,
  + exportOptions: SketchExportOptions,
  + frame: SketchRect,
  + isFlippedVertical: bool,
  + isFlippedHorizontal: bool,
  + isLocked: bool,
  + isVisible: bool,
  + layerListExpandedType: number,
  + name: string,
  + nameIsFixed: bool,
  + originalObjectID: UUID,
  + resizingType: number,
  + rotation: number,
  + shouldBreakMaskChain: bool,
  + style: SketchStyle,
  + hasClickThrough: bool,
  # layers: [SketchLayer],
  clippingMaskMode: number,
  hasClippingMask: bool,
  windingRule: number
  """
  CLASS = 'shapeGroup'
  ATTRS = {
    'do_objectID': (asId, 0),
    'exportOptions': (SketchExportOptions, None),
    'frame': (SketchRect, None),
    'isFlippedVertical': (asBool, False),
    'isFlippedHorizontal': (asBool, False),
    'isLocked': (asBool, False),
    'isVisible': (asBool, True),
    'layerListExpandedType': (asInt, 0),
    'name': (asString, ''),
    'nameIsFixed': (asBool, False),
    'originalObjectID': (asId, None),
    'resizingType': (asInt, 0),
    'rotation': (asNumber, 0),
    'shouldBreakMaskChain': (asBool, False),
    'style': (SketchStyle, None),
    'hasClickThrough': (asBool, False),
  }

class SketchPath(SketchBase):
  """
  _class: 'path',
  isClosed: bool,
  points: [SketchCurvePoint]
  """
  CLASS = 'path'
  ATTRS = {

  }

class SketchShapePath(SketchBase):
  """
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
  """
  CLASS = 'shapePath'
  ATTRS = {
    'do_objectID': (asId, 0),
    'exportOptions': (SketchExportOptions, None),
    'frame': (SketchRect, None),
    'isFlippedHorizontal': (asBool, False),
    'isLocked': (asBool, False),
    'isVisible': (asBool, True),
    'layerListExpandedType': (asInt, 0),
    'name': (asString, ''),
    'nameIsFixed': (asBool, False),
    'name': (asString, ''),
    'nameIsFixed': (asBool, False),
  }

class SketchArtboard(SketchLayer):
  """
  _class: 'artboard',
  + do_objectID: UUID,
  + exportOptions: SketchExportOptions,
  + frame: SketchRect,
  + isFlippedHorizontal: bool,
  + isFlippedVertical: bool,
  + isLocked: bool,
  + isVisible: bool,
  + layerListExpandedType: number,
  + name: string,
  + nameIsFixed: bool,
  + resizingType: number,
  + rotation: number,
  + shouldBreakMaskChain: bool,
  + style: SketchStyle,
  + hasClickThrough: bool,
  # layers: [SketchLayer],
  + backgroundColor: SketchColor,
  + hasBackgroundColor: bool,
  + horizontalRulerData: SketchRulerData,
  + includeBackgroundColorInExport: bool,
  + includeInCloudUpload: bool,
  + verticalRulerData: SketchRulerData
  """
  REPR_ATTRS = ['name', 'frame'] # Attributes to be show in __repr__
  CLASS = 'artboard'
  ATTRS = {
    'do_objectID': (asId, 0),
    'exportOptions': (SketchExportOptions, None),
    'frame': (SketchRect, None),
    'isFlippedHorizontal': (asBool, False),
    'isFlippedVertical': (asBool, False),
    'isLocked': (asBool, False),
    'isVisible': (asBool, True),
    'layerListExpandedType': (asInt, 0),
    'name': (asString, 'Artboard'),
    'nameIsFixed': (asBool, False),
    'resizingType': (asInt, 0),
    'rotation': (asNumber, 0),
    'shouldBreakMaskChain': (asBool, False),
    'style': (SketchStyle, None),
    'hasClickThrough': (asBool, False),
    'backgroundColor': (SketchColor, None),
    'hasBackgroundColor': (asBool, False),
    'horizontalRulerData': (SketchRulerData, None),
    'verticalRulerData': (SketchRulerData, None),
    'includeBackgroundColorInExport': (asBool, False),
    'includeInCloudUpload': (asBool, True),
    'layers': (asList, []),
  }

class SketchBitmap(SketchBase):
  """
  _class: 'bitmap',
  + do_objectID: UUID,
  + exportOptions: SketchExportOptions,
  + frame: SketchRect,
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
  """
  CLASS = 'bitmap'
  ATTRS = {
    'do_objectID': (asId, 0),
    'exportOptions': (SketchExportOptions, None),
    'frame': (SketchRect, None),
    'isFlippedHorizontal': (asBool, False),
    'isFlippedVertical': (asBool, False),
    'isLocked': (asBool, False),
    'isVisible': (asBool, True),
    'layerListExpandedType': (asInt, 0),
    'name': (asString, ''),
    'nameIsFixed': (asBool, False),
    'resizingType': (asInt, 0),
    'rotation': (asNumber, 0),
    'shouldBreakMaskChain': (asBool, False),
    'style': (SketchStyle, None),
    'clippingMask': (asRect, None),
    'fillReplacesImage': (asBool, False),
    'image': (asString, ''),
    'nineSliceCenterRect': (asRect, None),
    'nineSliceScale': (asRect, None)
  }

class SketchSymbolInstance(SketchBase):
  """
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
  """
  CLASS = 'symbolInstance'
  ATTRS = {

  }

class SketchGroup(SketchLayer):
  """
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
  # layers: [SketchLayer]
  """
  CLASS = 'group'
  ATTRS = {

  }

class SketchRectangle(SketchBase):
  """
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
  """
  CLASS = 'rectangle'
  ATTRS = {

  }

class SketchOval(SketchBase):
  """
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
  """
  CLASS = 'oval'
  ATTRS = {

  }

# Conversion of Sketch layer class name to Python class.
SKETCHLAYER_PY = {
  'text': SketchText,
  'shapeGroup': SketchShapeGroup,
  'shapePath': SketchShapePath,
  'bitmap': SketchBitmap,
  'artboard': SketchArtboard,
  'symbolInstance': SketchSymbolInstance,
  'group': SketchGroup,
  'rectangle': SketchRectangle,
  'oval': SketchOval,
}

'''
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
  layers: SketchLayerList,
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
  + do_objectID: UUID,
  + assets: SketchAssetsCollection,
  + colorSpace: number,
  + currentPageIndex: number,
  + enableLayerInteraction: bool,
  + enableSliceInteraction: bool,
  foreignSymbols: [], // TODO
  + layerStyles: SketchSharedStyleContainer,
  + layerSymbols: SketchSymbolContainer,
  + layerTextStyles: SketchSharedTextStyleContainer,
  + pages: SketchMSJSONFileReferenceList,
  """
  CLASS = 'document'
  ATTRS = {
    'do_objectID': (asId, 0),
    'assets': (SketchAssetsCollection, []),
    'colorSpace': (asInt, 0),
    'currentPageIndex': (asInt, 0),
    'enableLayerInteraction': (asBool, False),
    'enableSliceInteraction': (asBool, False),
    'foreignLayerStyles': (asList, []),
    'foreignSymbols': (asList, []),
    'foreignTextStyles': (asList, []),
    'layerStyles': (SketchSharedStyleContainer, {}),
    'layerSymbols': (SketchSymbolContainer, {}),
    'layerTextStyles': (SketchSharedTextStyleContainer, {}),
    'pages': (SketchMSJSONFileReferenceList, []),
  }

# pages/*.json
class SketchPage(SketchLayer):
  """
  _class: 'page',
  do_objectID: UUID,
  + booleanOperation: number, 
  + exportOptions: SketchExportOptions,
  + frame: SketchRect,
  + hasClickThrough: bool,
  + horizontalRulerData: SketchRulerData,
  + includeInCloudUpload: bool,
  + isFlippedHorizontal: bool,
  + isFlippedVertical: bool,
  + isLocked: bool,
  + isVisible: bool,
  + layerListExpandedType: number,
  # layers: [SketchSymbolMaster],
  + name: string,
  + nameIsFixed: bool,
  + resizingType: number,
  + rotation: number,
  + shouldBreakMaskChain: bool,
  + style: SketchStyle,
  + verticalRulerData: SketchRulerData
  + userInfo: {}
}
  """
  CLASS = 'page'
  ATTRS = {
    'do_objectID': (asId, 0),    
    'booleanOperation': (asInt, -1),
    'frame': (SketchRect, None),
    'hasClickThrough': (asBool, True),
    'includeInCloudUpload': (asBool, False),
    'isFlippedHorizontal': (asBool, False),
    'isFlippedVertical': (asBool, False),
    'isLocked': (asBool, False),
    'isVisible': (asBool, True),
    'layerListExpandedType': (asInt, 0),
    'name': (asString, 'Untitled'),
    'nameIsFixed': (asBool, False),
    'resizingType': (asInt, 0),
    'rotation': (asNumber, 0),
    'shouldBreakMaskChain': (asBool, False),
    'style': (SketchStyle, None),
    'verticalRulerData': (SketchRulerData, None),
    'horizontalRulerData': (SketchRulerData, None),
    'userInfo': (asDict, {}),
  }
  def asJson(self):
    d = {}
    for attrName in self.ATTRS.keys():
      attr = getattr(self, attrName)
      if isinstance(attr, (list, tuple)):
        l = [] 
        for e in attr:
          if hasattr(e, 'asJson'):
            l.append(e.asJson())
        attr = l
      elif hasattr(attr, 'asJson'):
        attr = attr.asJson()
      if attr is not None:
        assert isinstance(attr, (dict, int, float, list, tuple, str)), attr
        d[attrName] = attr
    if not d:
      return None
    d['_class'] = self.CLASS
    d['layers'] = []
    return d

class SketchFile:
  def __init__(self):
    self.pages = {}
    self.document = None
    self.user = None 
    self.meta = None

  def __repr__(self):
    return '<sketchFile>'   

# meta.json
class SketchMeta(SketchBase):
  """
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
  """
  CLASS = 'meta'
  ATTRS = {
    'commit': (asString, ''),
    'appVersion': (asString, ''),
    'build': (asNumber, 0),
  }

# user.json
class SketchUser(SketchBase):
  """
  [key: SketchPageId]: {
    scrollOrigin: SketchPositionString,
    zoomValue: number
  },
  [key: SketchDocumentId]: {
    pageListHeight: number,
    cloudShare: Unknown // TODO
  }
  """
  CLASS = 'user'
  ATTRS = {
  }
  def __init__(self, d):
    SketchBase.__init__(self, d)
    self.document = dict(pageListHeight=118)

  def asJson(self):
    return dict(document=dict(pageListHeight=self.document['pageListHeight']))

if __name__ == '__main__':
  import doctest
  import sys
  sys.exit(doctest.testmod()[0])
