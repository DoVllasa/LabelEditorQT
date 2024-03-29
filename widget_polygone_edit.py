import copy
from enum import Enum
from warnings import warn
from edit_gen_polygon import *


class Instructions(Enum):
    NoInstruction = 0
    PolygonInstruction = 1
    BackItem = 0
    NextItem = 1

# Über Categorization.Box.name ebenfall auf 'Box'
# Farbcode abspeichern, also Box = 'QtColor(255,0,0)'


class Categorization(Enum):
    Box = 'Box'
    Bag = 'Bag'
    Bundle = 'Bundle'
    Unknown = 'unknown'
    Rest = 'Rest'
    Flat = 'Flat'
    TransparentBag = 'Transparent bag'

''' Mit item.mPoints[0].x() oder y(), bekommt man die reinen float numbers, wichtig, wenn man später die reinen Koordinaten benötigt
'''


class PolygonItemsDisplay(QtWidgets.QGraphicsPathItem):
    circle = QtGui.QPainterPath()
    circle.addEllipse(QtCore.QRectF(-10, -10, 20, 20))
    square = QtGui.QPainterPath()
    square.addRect(QtCore.QRectF(-15, -15, 30, 30))

    def __init__(self, annotationItem, index):
        super(PolygonItemsDisplay, self).__init__()
        self.mAnnotationItem = annotationItem
        self.mIndex = index
        self.setPath(PolygonItemsDisplay.circle)
        self.setBrush(QtGui.QColor("blue"))
        self.setPen(QtGui.QPen(QtGui.QColor("blue"), 2))
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        self.setZValue(11)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

    def hoverEnterEvent(self, event):
        self.setPath(PolygonItemsDisplay.square)
        self.setBrush(QtGui.QColor("blue"))
        super(PolygonItemsDisplay, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setPath(PolygonItemsDisplay.circle)
        self.setBrush(QtGui.QColor("blue"))
        super(PolygonItemsDisplay, self).hoverLeaveEvent(event)

    def mouseReleaseEvent(self, event):
        self.setSelected(False)
        super(PolygonItemsDisplay, self).mouseReleaseEvent(event)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionChange and self.isEnabled():
            self.mAnnotationItem.movePoint(self.mIndex, value)
        return super(PolygonItemsDisplay, self).itemChange(change, value)


class PolygonAnnotation(QtWidgets.QGraphicsPolygonItem):
    def __init__(self, parent=None):
        super(PolygonAnnotation, self).__init__(parent)
        self.mPoints = []
        self.setZValue(10)
        self.setPen(QtGui.QPen(QtGui.QColor("blue"), 2))
        self.setAcceptHoverEvents(True)

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        # self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.mItems = []

    def numberOfPoints(self):
        return len(self.mItems)

    def addPoint(self, p):
        self.mPoints.append(p)
        self.setPolygon(QtGui.QPolygonF(self.mPoints))
        item = PolygonItemsDisplay(self, len(self.mPoints) - 1)
        item.setScale(0.3)
        self.scene().addItem(item)
        self.mItems.append(item)
        item.setPos(p)

    def removeLastPoint(self):
        if self.mPoints:
            self.mPoints.pop()
            self.setPolygon(QtGui.QPolygonF(self.mPoints))
            it = self.mItems.pop()
            self.scene().removeItem(it)
            del it

    def movePoint(self, i, p):
        if 0 <= i < len(self.mPoints):
            self.mPoints[i] = self.mapFromScene(p)
            self.setPolygon(QtGui.QPolygonF(self.mPoints))

    def moveItem(self, index, pos):
        if 0 <= index < len(self.mItems):
            item = self.mItems[index]
            item.setEnabled(False)
            item.setPos(pos)
            self.movePoint(index, pos)
            item.setEnabled(True)

    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemPositionHasChanged:
            for i, point in enumerate(self.mPoints):
                self.moveItem(i, self.mapToScene(point))
        return super(PolygonAnnotation, self).itemChange(change, value)


class ImageScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent=None):
        super(ImageScene, self).__init__(parent)
        self.imageItem = QtWidgets.QGraphicsPixmapItem()
        self.imageItem.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.addItem(self.imageItem)
        self.currentInstruction = Instructions.NoInstruction
        self.polygonItems = []
        self.imageName = ''
        self.savedCategoryDictonary = {}
        self.categorizedPolys = {}
        self.colorDefinition = {}
        self.colorDefinition[Categorization.Box.value] = QtGui.QColor(255, 0, 0, 150)
        self.colorDefinition[Categorization.Bag.value] = QtGui.QColor(0, 0, 255, 150)
        self.colorDefinition[Categorization.Bundle.value] = QtGui.QColor(0, 255, 0, 150)
        self.colorDefinition[Categorization.Unknown.value] = QtGui.QColor(255, 127, 36, 150)
        self.colorDefinition[Categorization.Rest.value] = QtGui.QColor(155, 48, 255, 150)
        self.colorDefinition[Categorization.Flat.value] = QtGui.QColor(255, 255, 0, 150)
        self.colorDefinition[Categorization.TransparentBag.value] = QtGui.QColor(0, 191, 255, 150)

    def load_image(self, filename):
        self.imageItem.setPixmap(QtGui.QPixmap(filename))
        self.setSceneRect(self.imageItem.boundingRect())
        self.imageName = filename
        if filename in imagePolygon:
            imagePolyData = imagePolygon[filename]
            self.savedCategoryDictonary = imagePolyData
            for i in self.savedCategoryDictonary.keys():
                self.createPoly(i)

    def createPoly(self, categorizationOfPolygone):
        self.categorizedPolys = {}
        for i in self.savedCategoryDictonary[categorizationOfPolygone]:
            self.setPolygonStructure(categorizationOfPolygone)
            for k in i:
                self.positionAddPoint(k)
            if categorizationOfPolygone in self.categorizedPolys:
                self.categorizedPolys[categorizationOfPolygone].append(i)
            else:
                createTmpListCoord = []
                createTmpListCoord.append(i)
                self.categorizedPolys[categorizationOfPolygone] = createTmpListCoord

    def setPolygonStructure(self, polyCategorization):
        self.polygonItem = PolygonAnnotation()
        self.polygonItem.setBrush(self.colorDefinition[polyCategorization])
        self.addItem(self.polygonItem)
        self.polygonItems.append(self.polygonItem)

    def setCurrentInstruction(self, instruction, category: str):
        self.currentInstruction = instruction
        self.setPolygonStructure(category)

    def mousePressEvent(self, event):
        if self.currentInstruction == Instructions.PolygonInstruction:
            self.positionAddPoint(event.scenePos())
        super(ImageScene, self).mousePressEvent(event)

    def positionAddPoint(self, position):
        self.polygonItem.removeLastPoint()
        self.polygonItem.addPoint(position)
        self.polygonItem.addPoint(position)

    def savePolygonInDictonary(self):
        self.savedCategoryDictonary = {}
        for i in self.polygonItems:
            if len(i.mPoints) != 0:
                polyCoordinates = i.mPoints[:-1]
                for k in self.colorDefinition.keys():
                    if self.colorDefinition[k].getRgb() == i.brush().color().getRgb():
                        if k not in self.savedCategoryDictonary:
                            polyTmpPointsCoord = []
                            polyTmpPointsCoord.append(polyCoordinates)
                            self.savedCategoryDictonary[k] = polyTmpPointsCoord
                            break
                        elif polyCoordinates not in self.savedCategoryDictonary[k]:
                            self.savedCategoryDictonary[k].append(polyCoordinates)
                            break
        # print('SAVEDSAVEDSAVED', self.savedCategoryDictonary)

    def mouseMoveEvent(self, event):
        if self.currentInstruction == Instructions.PolygonInstruction:
            self.polygonItem.movePoint(self.polygonItem.numberOfPoints() - 1, event.scenePos())
        self.savePolygonInDictonary()
        super(ImageScene, self).mouseMoveEvent(event)

    def removePolygon(self):
        categorizationType = None
        if self.polygonItem:
            for item in self.selectedItems():
                try:
                    allCoordinatesFromItem = item.mPoints[:-1]
                except AttributeError:
                    warn('You tried to remove before finishing')
                    return
                for i in self.colorDefinition.keys():
                    if self.colorDefinition[i].getRgb() == item.brush().color().getRgb():
                        categorizationType = i
                        break
                newCoordFromPoly = []
                for itemsCoordinates in self.savedCategoryDictonary[categorizationType]:
                    if allCoordinatesFromItem != itemsCoordinates:
                        newCoordFromPoly.append(itemsCoordinates)
                if len(newCoordFromPoly) != 0:
                    self.savedCategoryDictonary[categorizationType] = newCoordFromPoly
                else:
                    del self.savedCategoryDictonary[categorizationType]
                while len(item.mPoints) > 0:
                    item.removeLastPoint()
            for i in self.selectedItems():
                i.removeLastPoint()

    def removeAllPolygone(self):
        print('TESTSET', self.savedCategoryDictonary)
        setInformationFromImage(self.savedCategoryDictonary, self.imageName)
        for k in self.polygonItems:
            while len(k.mPoints) > 0:
                k.removeLastPoint()
            self.removeItem(k)
        self.savedCategoryDictonary = {}
        self.polygonItems = []


imagePolygon = {}

def setInformationFromImage(catgorizedDict: dict, name: str):
    if name != '':
        imagePolygon[name] = catgorizedDict
