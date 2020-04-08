from functools import partial
from os import listdir
import os
from os.path import isfile, join
import sys
from PySide2 import QtWidgets, QtGui, QtCore
from PySide2.QtWidgets import QWidget
from widget import Ui_Widget
from widget_polygone_edit import Instructions, ImageScene, Categorization


class WidgetWindow(QWidget):
    factor = 2.0

    def __init__(self, parent=None):
        super(WidgetWindow, self).__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)
        self.setWindowTitle("Truth Data generator Parcels")
        self.ui.graphicsView.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)
        self.ui.graphicsView.setMouseTracking(True)
        self.mView = self.ui.graphicsView
        self.mScene = ImageScene(self)
        self.mView.setScene(self.mScene)
        self.counterImages = 0
        self.colorNum = 0
        # self.directory = '/Users/dominim/Desktop/TestData'
        self.directory = '/Users/dominimvllasa/Desktop/TestData'
        # self.directory = '/home/dominim/Desktop/Data/wa1122/wa1122/png_rgb/t000'
        self.filenames = [f for f in listdir(self.directory) if isfile(join(os.path.realpath(self.directory), f))]
        self.realpathImages = []
        for index, filename in enumerate(self.filenames):
            self.realpathImages.append(self.directory + '/' + filename)
        self.load_image(Instructions.BackItem)
        # self.ui.nextImageButton.clicked.connect(partial(self.load_image, Instructions.NextItem.value))
        # self.ui.backButton.clicked.connect(partial(self.load_image, Instructions.BackItem.value))
        # self.ui.removeButton.clicked.connect(self.mScene.removePolygon)

# ----------------------------------------------------------------------------------------------------------------------
#   initialize Buttons for drawing Polygone
# ----------------------------------------------------------------------------------------------------------------------

        self.ui.boxButton.setStyleSheet("color: #FF0000")  # Red 255, 0, 0
        self.ui.bagButton.setStyleSheet("color: #0000FF")  # blue 0, 0, 255
        self.ui.bundleButton.setStyleSheet("color: #00FF00")  # Green 0, 255, 0
        self.ui.unknownButton.setStyleSheet("color: #FF7F24")  # orange 255, 127, 36
        self.ui.restButton.setStyleSheet("color: #9B30FF")  # purple 155, 48, 255
        self.ui.flatButton.setStyleSheet("color: #FFFF00")  # pink 255, 255, 0
        self.ui.transaprentBagButton.setStyleSheet("color: #00BFFF")  # Lightblue 0, 191, 255

        self.ui.boxButton.clicked.connect(partial(self.setColorCode, Categorization.Box.value))
        self.ui.bagButton.clicked.connect(partial(self.setColorCode, Categorization.Bag.value))
        self.ui.bundleButton.clicked.connect(partial(self.setColorCode, Categorization.Bundle.value))
        self.ui.unknownButton.clicked.connect(partial(self.setColorCode, Categorization.Unknown.value))
        self.ui.restButton.clicked.connect(partial(self.setColorCode, Categorization.Rest.value))
        self.ui.flatButton.clicked.connect(partial(self.setColorCode, Categorization.Flat.value))
        self.ui.transaprentBagButton.clicked.connect(partial(self.setColorCode, Categorization.TransparentBag.value))


# ----------------------------------------------------------------------------------------------------------------------
#   Set Shortcuts for QGraphicsView
# ----------------------------------------------------------------------------------------------------------------------

        QtWidgets.QShortcut(QtGui.QKeySequence.ZoomIn, self.mView, self.zoomIn)
        QtWidgets.QShortcut(QtGui.QKeySequence.ZoomOut, self.mView, self.zoomOut)

        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Right), self.mView,
                            activated=partial(self.load_image, Instructions.NextItem.value))
        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Left), self.mView,
                            activated=partial(self.load_image, Instructions.BackItem.value))

        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), self.mView,
                            activated=partial(self.mScene.setCurrentInstruction, Instructions.NoInstruction,
                                              Categorization.Box.value))

        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_A), self.mView,
                            activated=partial(self.mScene.setCurrentInstruction, Instructions.PolygonInstruction,
                                              Categorization.Box.value))

        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_X), self.mView, self.mScene.removeAllPolygone)
        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Y), self.mView, self.mScene.removePolygon)

        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_1), self.mView,
                            activated=partial(self.setColorCode, Categorization.Box.value))

        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_2), self.mView,
                            activated=partial(self.setColorCode, Categorization.Bag.value))

        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_3), self.mView,
                                activated=partial(self.setColorCode, Categorization.Bundle.value))

        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_4), self.mView,
                            activated=partial(self.setColorCode, Categorization.Unknown.value))

        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_5), self.mView,
                            activated=partial(self.setColorCode, Categorization.Rest.value))

        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_6), self.mView,
                            activated=partial(self.setColorCode, Categorization.Flat.value))

        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_7), self.mView,
                            activated=partial(self.setColorCode, Categorization.TransparentBag.value))


# ----------------------------------------------------------------------------------------------------------------------
#   Set Categorization with from images with ColorCodes
# ----------------------------------------------------------------------------------------------------------------------

    def setColorCode(self, catrgory: str):
        self.mScene.setCurrentInstruction(Instructions.PolygonInstruction, catrgory)

# ----------------------------------------------------------------------------------------------------------------------
#   Set View Modification with ZoomIn/-Out
# ----------------------------------------------------------------------------------------------------------------------

    @QtCore.Slot()
    def zoomIn(self):
        self.zoom(2)

    @QtCore.Slot()
    def zoomOut(self):
        self.zoom(1 / 2)

    def zoom(self, f):
        self.mView.scale(f, f)
        if self.mView.scene() is not None:
            self.mView.centerOn(self.mView.scene().imageItem)

    def showEvent(self, event: QtGui.QShowEvent):
        self.mView.fitInView(self.mScene.sceneRect(), QtCore.Qt.KeepAspectRatio)

# ----------------------------------------------------------------------------------------------------------------------
#   Load Images in QGraphicsScene and fit in QGraphicsView
# ----------------------------------------------------------------------------------------------------------------------

    @QtCore.Slot()
    def load_image(self, imageNavigation):
        self.mScene.removeAllPolygone()
        if imageNavigation == 1 and self.counterImages < self.realpathImages.__len__() - 1:
            self.counterImages = self.counterImages + 1
        elif imageNavigation == 0 and self.counterImages > 0:
            self.counterImages = self.counterImages - 1
        else:
            self.counterImages = 0

        if self.realpathImages[self.counterImages]:
            self.mScene.load_image(self.realpathImages[self.counterImages])
            self.mView.fitInView(self.mScene.imageItem, QtCore.Qt.KeepAspectRatio)
            self.mView.centerOn(self.mScene.imageItem)